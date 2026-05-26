from django.conf import settings
from django.db import models


class DataSource(models.TextChoices):
    SAP = "SAP", "SAP"
    UTILITY = "UTILITY", "Utility"
    TRAVEL = "TRAVEL", "Travel"


class DataSourceConfig(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="data_source_configs",
    )
    source = models.CharField(max_length=20, choices=DataSource.choices)
    plant_lookup = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "data_source_configs"
        unique_together = ("organization", "source")

    def __str__(self):
        return f"{self.organization.slug} - {self.source}"


class BatchStatus(models.TextChoices):
    PROCESSING = "processing", "Processing"
    COMPLETE = "complete", "Complete"
    FAILED = "failed", "Failed"


class IngestionBatch(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="batches",
    )
    source = models.CharField(max_length=20, choices=DataSource.choices)
    filename = models.CharField(max_length=512)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_batches",
    )
    status = models.CharField(
        max_length=20,
        choices=BatchStatus.choices,
        default=BatchStatus.PROCESSING,
    )
    row_count_total = models.PositiveIntegerField(default=0)
    row_count_success = models.PositiveIntegerField(default=0)
    row_count_failed = models.PositiveIntegerField(default=0)
    error_summary = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ingestion_batches"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source} batch {self.pk} ({self.status})"


class RawRow(models.Model):
    batch = models.ForeignKey(
        IngestionBatch,
        on_delete=models.CASCADE,
        related_name="raw_rows",
    )
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField()
    parse_errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ingestion_raw_rows"
        ordering = ["row_number"]
        unique_together = ("batch", "row_number")


class Scope(models.TextChoices):
    SCOPE_1 = "SCOPE_1", "Scope 1"
    SCOPE_2 = "SCOPE_2", "Scope 2"
    SCOPE_3 = "SCOPE_3", "Scope 3"


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    FLAGGED = "flagged", "Flagged"
    REJECTED = "rejected", "Rejected"


class NormalizedActivity(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="activities",
    )
    batch = models.ForeignKey(
        IngestionBatch,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    raw_row = models.OneToOneField(
        RawRow,
        on_delete=models.CASCADE,
        related_name="normalized_activity",
        null=True,
        blank=True,
    )
    scope = models.CharField(max_length=20, choices=Scope.choices)
    scope_category = models.CharField(max_length=64)
    activity_type = models.CharField(max_length=64)
    activity_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    activity_unit = models.CharField(max_length=32, blank=True)
    original_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    original_unit = models.CharField(max_length=32, blank=True)
    facility_code = models.CharField(max_length=64, blank=True)
    cost_center = models.CharField(max_length=64, blank=True)
    vendor_id = models.CharField(max_length=64, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    source_system = models.CharField(max_length=32)
    source_record_id = models.CharField(max_length=128, blank=True)
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    quality_flags = models.JSONField(default=list, blank=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "normalized_activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "review_status"]),
            models.Index(fields=["organization", "scope"]),
            models.Index(fields=["organization", "batch"]),
        ]

    def __str__(self):
        return f"{self.activity_type} ({self.scope}) - {self.review_status}"


class EmissionMethod(models.TextChoices):
    ACTIVITY = "activity_based", "Activity based"
    SPEND = "spend_fallback", "Spend fallback"
    DISTANCE = "distance_estimated", "Distance estimated"


class Confidence(models.TextChoices):
    HIGH = "high", "High"
    MEDIUM = "medium", "Medium"
    LOW = "low", "Low"


class EmissionEstimate(models.Model):
    normalized_activity = models.OneToOneField(
        NormalizedActivity,
        on_delete=models.CASCADE,
        related_name="emission_estimate",
    )
    method = models.CharField(max_length=32, choices=EmissionMethod.choices)
    factor_source = models.CharField(max_length=255)
    factor_value = models.DecimalField(max_digits=20, decimal_places=8)
    co2e_kg = models.DecimalField(max_digits=20, decimal_places=6)
    co2e_tonnes = models.DecimalField(max_digits=20, decimal_places=8)
    confidence = models.CharField(max_length=16, choices=Confidence.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "emission_estimates"

    def __str__(self):
        return f"{self.co2e_tonnes} tCO2e ({self.confidence})"


class AuditLog(models.Model):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)
    action = models.CharField(max_length=64)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_actions",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
