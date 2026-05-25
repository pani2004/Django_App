from ingestion.models import AuditLog


def log_audit(*, organization, entity_type, entity_id, action, actor, before=None, after=None, reason=""):
    return AuditLog.objects.create(
        organization=organization,
        entity_type=entity_type,
        entity_id=str(entity_id),
        action=action,
        actor=actor,
        before=before or {},
        after=after or {},
        reason=reason,
    )
