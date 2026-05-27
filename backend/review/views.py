from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsOrganizationMember
from ingestion.models import BatchStatus, IngestionBatch, NormalizedActivity, ReviewStatus
from ingestion.serializers import NormalizedActivityListSerializer

from .serializers import AuditLogSerializer, ReviewActionSerializer
from .services import ReviewError, approve_activity, bulk_approve_clean, flag_activity, reject_activity


class DashboardStatsView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        org = request.user.organization
        activities = NormalizedActivity.objects.filter(organization=org)

        by_scope = {
            row["scope"]: row["c"]
            for row in activities.values("scope").annotate(c=Count("id"))
        }
        by_status = {
            row["review_status"]: row["c"]
            for row in activities.values("review_status").annotate(c=Count("id"))
        }

        return Response(
            {
                "pending_review": activities.filter(review_status=ReviewStatus.PENDING).count(),
                "flagged": activities.filter(review_status=ReviewStatus.FLAGGED).count(),
                "approved_locked": activities.filter(is_locked=True).count(),
                "needs_attention": activities.filter(
                    Q(review_status=ReviewStatus.PENDING) & ~Q(quality_flags=[])
                ).count(),
                "failed_batches": IngestionBatch.objects.filter(
                    organization=org, status=BatchStatus.FAILED
                ).count(),
                "by_scope": by_scope,
                "by_status": by_status,
            }
        )


class ActivityApproveView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request, pk):
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            activity = approve_activity(
                activity_id=pk,
                organization=request.user.organization,
                actor=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ReviewError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(NormalizedActivityListSerializer(activity).data)


class ActivityFlagView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request, pk):
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            activity = flag_activity(
                activity_id=pk,
                organization=request.user.organization,
                actor=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ReviewError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(NormalizedActivityListSerializer(activity).data)


class ActivityRejectView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request, pk):
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            activity = reject_activity(
                activity_id=pk,
                organization=request.user.organization,
                actor=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ReviewError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(NormalizedActivityListSerializer(activity).data)


class BulkApproveView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request):
        count = bulk_approve_clean(organization=request.user.organization, actor=request.user)
        return Response({"approved_count": count})


class ActivityAuditView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request, pk):
        from ingestion.models import AuditLog

        logs = AuditLog.objects.filter(
            organization=request.user.organization,
            entity_type="NormalizedActivity",
            entity_id=str(pk),
        )
        return Response(AuditLogSerializer(logs, many=True).data)
