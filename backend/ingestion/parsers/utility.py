from datetime import datetime

from .base import parse_decimal, read_csv_rows


def parse_utility_csv(file_content: bytes) -> list[dict]:
    rows = read_csv_rows(file_content, delimiter=",")
    results = []

    for idx, row in enumerate(rows, start=2):
        errors = []
        quality_flags = []

        usage = parse_decimal(row.get("usage_kwh") or row.get("USAGE_KWH") or "")
        start = _parse_date(row.get("bill_start_date") or "")
        end = _parse_date(row.get("bill_end_date") or "")
        facility = (row.get("facility_id") or "").strip()
        account = (row.get("account_number") or "").strip()
        meter = (row.get("meter_number") or "").strip()

        if usage is None:
            errors.append("Missing usage_kwh")
        if not start or not end:
            errors.append("Missing billing period dates")

        if start and end:
            days = (end - start).days + 1
            if days > 45:
                quality_flags.append("long_billing_period")

        normalized = {
            "scope": "SCOPE_2",
            "scope_category": "2.1_purchased_electricity",
            "activity_type": "electricity_kwh",
            "activity_value": usage,
            "activity_unit": "kWh",
            "original_value": usage,
            "original_unit": "kWh",
            "facility_code": facility,
            "cost_center": "",
            "vendor_id": (row.get("utility_name") or "").strip(),
            "period_start": start,
            "period_end": end,
            "source_system": "UTILITY",
            "source_record_id": f"{account}-{meter}-{start}",
            "quality_flags": quality_flags,
            "metadata": {
                "rate_schedule": (row.get("rate_schedule") or "").strip(),
                "peak_demand_kw": row.get("peak_demand_kw") or "",
            },
        }

        results.append({
            "row_number": idx,
            "raw_data": row,
            "normalized": normalized if not errors else normalized,
            "errors": errors,
        })

    return results


def _parse_date(value: str):
    if not value or not str(value).strip():
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None
