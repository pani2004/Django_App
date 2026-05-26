from django.contrib import admin

from .models import (
    AuditLog,
    DataSourceConfig,
    EmissionEstimate,
    IngestionBatch,
    NormalizedActivity,
    RawRow,
)


@admin.register(IngestionBatch)
class IngestionBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "source", "status", "row_count_success", "created_at")
    list_filter = ("source", "status", "organization")


@admin.register(NormalizedActivity)
class NormalizedActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "activity_type", "scope", "review_status", "organization", "batch")
    list_filter = ("scope", "review_status", "source_system")


admin.site.register(RawRow)
admin.site.register(EmissionEstimate)
admin.site.register(DataSourceConfig)
admin.site.register(AuditLog)
