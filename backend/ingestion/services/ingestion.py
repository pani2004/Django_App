from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ingestion.emissions import estimate_emissions
from ingestion.models import (
    BatchStatus,
    EmissionEstimate,
    IngestionBatch,
    NormalizedActivity,
    RawRow,
)
from ingestion.parsers import PARSERS
from ingestion.services.quality import apply_quality_heuristics


@transaction.atomic
def process_upload(*, organization, user, source: str, filename: str, file_content: bytes) -> IngestionBatch:
    parser = PARSERS.get(source)
    if not parser:
        raise ValueError(f"Unknown source: {source}")

    batch = IngestionBatch.objects.create(
        organization=organization,
        source=source,
        filename=filename,
        uploaded_by=user,
        status=BatchStatus.PROCESSING,
    )

    parsed_rows = parser(file_content)
    batch.row_count_total = len(parsed_rows)

    success = 0
    failed = 0
    error_summary = []

    activities_for_heuristics = []

    for row in parsed_rows:
        raw = RawRow.objects.create(
            batch=batch,
            row_number=row["row_number"],
            raw_data=row["raw_data"],
            parse_errors=row["errors"],
        )

        if row["errors"] and row["normalized"] is None:
            failed += 1
            error_summary.append({"row": row["row_number"], "errors": row["errors"]})
            continue

        normalized = row.get("normalized")
        if not normalized:
            failed += 1
            continue

        activity = NormalizedActivity.objects.create(
            organization=organization,
            batch=batch,
            raw_row=raw,
            scope=normalized["scope"],
            scope_category=normalized["scope_category"],
            activity_type=normalized["activity_type"],
            activity_value=normalized.get("activity_value"),
            activity_unit=normalized.get("activity_unit") or "",
            original_value=normalized.get("original_value"),
            original_unit=normalized.get("original_unit") or "",
            facility_code=normalized.get("facility_code") or "",
            cost_center=normalized.get("cost_center") or "",
            vendor_id=normalized.get("vendor_id") or "",
            period_start=normalized.get("period_start"),
            period_end=normalized.get("period_end"),
            source_system=normalized["source_system"],
            source_record_id=normalized.get("source_record_id") or "",
            quality_flags=normalized.get("quality_flags") or [],
        )
        activities_for_heuristics.append(activity)

        estimate = estimate_emissions(normalized)
        if estimate:
            EmissionEstimate.objects.create(
                normalized_activity=activity,
                **estimate,
            )

        if row["errors"]:
            failed += 1
            error_summary.append({"row": row["row_number"], "errors": row["errors"]})
        else:
            success += 1

    apply_quality_heuristics(activities_for_heuristics, batch)

    batch.row_count_success = success
    batch.row_count_failed = failed
    batch.error_summary = error_summary[:50]
    batch.status = BatchStatus.COMPLETE if success > 0 else BatchStatus.FAILED
    batch.completed_at = timezone.now()
    batch.save()

    return batch
