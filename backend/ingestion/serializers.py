from rest_framework import serializers

from .models import EmissionEstimate, IngestionBatch, NormalizedActivity, RawRow


class EmissionEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionEstimate
        fields = (
            "method",
            "factor_source",
            "factor_value",
            "co2e_kg",
            "co2e_tonnes",
            "confidence",
        )


class RawRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRow
        fields = ("row_number", "raw_data", "parse_errors")


class NormalizedActivityListSerializer(serializers.ModelSerializer):
    emission = EmissionEstimateSerializer(source="emission_estimate", read_only=True)
    batch_source = serializers.CharField(source="batch.source", read_only=True)

    class Meta:
        model = NormalizedActivity
        fields = (
            "id",
            "batch",
            "batch_source",
            "scope",
            "scope_category",
            "activity_type",
            "activity_value",
            "activity_unit",
            "facility_code",
            "period_start",
            "period_end",
            "source_system",
            "source_record_id",
            "review_status",
            "quality_flags",
            "is_locked",
            "emission",
            "created_at",
        )


class NormalizedActivityDetailSerializer(NormalizedActivityListSerializer):
    raw_row = RawRowSerializer(read_only=True)
    original_value = serializers.DecimalField(max_digits=20, decimal_places=6, read_only=True)
    original_unit = serializers.CharField(read_only=True)
    cost_center = serializers.CharField(read_only=True)
    vendor_id = serializers.CharField(read_only=True)

    class Meta(NormalizedActivityListSerializer.Meta):
        fields = NormalizedActivityListSerializer.Meta.fields + (
            "raw_row",
            "original_value",
            "original_unit",
            "cost_center",
            "vendor_id",
        )


class IngestionBatchSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)

    class Meta:
        model = IngestionBatch
        fields = (
            "id",
            "source",
            "filename",
            "status",
            "row_count_total",
            "row_count_success",
            "row_count_failed",
            "error_summary",
            "uploaded_by_email",
            "created_at",
            "completed_at",
        )


class IngestionBatchDetailSerializer(IngestionBatchSerializer):
    raw_rows = RawRowSerializer(many=True, read_only=True)

    class Meta(IngestionBatchSerializer.Meta):
        fields = IngestionBatchSerializer.Meta.fields + ("raw_rows",)
