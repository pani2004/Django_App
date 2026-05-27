from django.db import transaction
from django.utils import timezone

from common.audit import log_audit
from ingestion.models import NormalizedActivity, ReviewStatus


class ReviewError(Exception):
    pass


def _get_activity(activity_id, organization):
    try:
        return NormalizedActivity.objects.select_related("emission_estimate").get(
            pk=activity_id,
            organization=organization,
        )
    except NormalizedActivity.DoesNotExist as exc:
        raise ReviewError("Activity not found") from exc


@transaction.atomic
def approve_activity(*, activity_id, organization, actor, reason=""):
    activity = _get_activity(activity_id, organization)
    if activity.is_locked:
        raise ReviewError("Row is already locked for audit")

    before = {"review_status": activity.review_status, "is_locked": activity.is_locked}
    activity.review_status = ReviewStatus.APPROVED
    activity.is_locked = True
    activity.save(update_fields=["review_status", "is_locked", "updated_at"])

    log_audit(
        organization=organization,
        entity_type="NormalizedActivity",
        entity_id=activity.pk,
        action="approved",
        actor=actor,
        before=before,
        after={"review_status": activity.review_status, "is_locked": True},
        reason=reason,
    )
    return activity


@transaction.atomic
def flag_activity(*, activity_id, organization, actor, reason=""):
    activity = _get_activity(activity_id, organization)
    if activity.is_locked:
        raise ReviewError("Cannot flag a locked row")

    before = {"review_status": activity.review_status}
    activity.review_status = ReviewStatus.FLAGGED
    activity.save(update_fields=["review_status", "updated_at"])

    log_audit(
        organization=organization,
        entity_type="NormalizedActivity",
        entity_id=activity.pk,
        action="flagged",
        actor=actor,
        before=before,
        after={"review_status": activity.review_status},
        reason=reason,
    )
    return activity


@transaction.atomic
def reject_activity(*, activity_id, organization, actor, reason=""):
    activity = _get_activity(activity_id, organization)
    if activity.is_locked:
        raise ReviewError("Cannot reject a locked row")

    before = {"review_status": activity.review_status}
    activity.review_status = ReviewStatus.REJECTED
    activity.save(update_fields=["review_status", "updated_at"])

    log_audit(
        organization=organization,
        entity_type="NormalizedActivity",
        entity_id=activity.pk,
        action="rejected",
        actor=actor,
        before=before,
        after={"review_status": activity.review_status},
        reason=reason,
    )
    return activity


@transaction.atomic
def bulk_approve_clean(*, organization, actor):
    """Approve pending rows with no quality flags."""
    qs = NormalizedActivity.objects.filter(
        organization=organization,
        review_status=ReviewStatus.PENDING,
        is_locked=False,
        quality_flags=[],
    )
    count = 0
    for activity in qs:
        approve_activity(activity_id=activity.pk, organization=organization, actor=actor)
        count += 1
    return count
