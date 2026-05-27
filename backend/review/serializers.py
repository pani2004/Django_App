from rest_framework import serializers

from ingestion.models import AuditLog
from ingestion.serializers import NormalizedActivityListSerializer


class ReviewActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "entity_type",
            "entity_id",
            "action",
            "actor_email",
            "timestamp",
            "before",
            "after",
            "reason",
        )


class ActivityWithAuditSerializer(NormalizedActivityListSerializer):
    audit_logs = serializers.SerializerMethodField()

    class Meta(NormalizedActivityListSerializer.Meta):
        fields = NormalizedActivityListSerializer.Meta.fields + ("audit_logs",)

    def get_audit_logs(self, obj):
        logs = AuditLog.objects.filter(
            organization=obj.organization,
            entity_type="NormalizedActivity",
            entity_id=str(obj.pk),
        )[:20]
        return AuditLogSerializer(logs, many=True).data
