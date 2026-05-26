from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsOrganizationMember

from .models import DataSource, IngestionBatch, NormalizedActivity
from .serializers import (
    IngestionBatchDetailSerializer,
    IngestionBatchSerializer,
    NormalizedActivityDetailSerializer,
    NormalizedActivityListSerializer,
)
from .services import process_upload


class BatchUploadView(APIView):
    permission_classes = [IsOrganizationMember]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        source = request.data.get("source", "").upper()
        file = request.FILES.get("file")

        if source not in DataSource.values:
            return Response(
                {"detail": "source must be SAP, UTILITY, or TRAVEL"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not file:
            return Response({"detail": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

        content = file.read()
        batch = process_upload(
            organization=request.user.organization,
            user=request.user,
            source=source,
            filename=file.name,
            file_content=content,
        )
        return Response(
            IngestionBatchSerializer(batch).data,
            status=status.HTTP_201_CREATED,
        )


class BatchListView(generics.ListAPIView):
    permission_classes = [IsOrganizationMember]
    serializer_class = IngestionBatchSerializer

    def get_queryset(self):
        return IngestionBatch.objects.filter(
            organization=self.request.user.organization
        )


class BatchDetailView(generics.RetrieveAPIView):
    permission_classes = [IsOrganizationMember]
    serializer_class = IngestionBatchDetailSerializer

    def get_queryset(self):
        return IngestionBatch.objects.filter(
            organization=self.request.user.organization
        )


class ActivityListView(generics.ListAPIView):
    permission_classes = [IsOrganizationMember]
    serializer_class = NormalizedActivityListSerializer

    def get_queryset(self):
        qs = NormalizedActivity.objects.filter(
            organization=self.request.user.organization
        ).select_related("batch", "emission_estimate")

        status_filter = self.request.query_params.get("review_status")
        scope = self.request.query_params.get("scope")
        source = self.request.query_params.get("source")
        has_flags = self.request.query_params.get("has_flags")

        if status_filter:
            qs = qs.filter(review_status=status_filter)
        if scope:
            qs = qs.filter(scope=scope)
        if source:
            qs = qs.filter(batch__source=source.upper())
        if has_flags == "true":
            qs = qs.exclude(quality_flags=[])

        return qs


class ActivityDetailView(generics.RetrieveAPIView):
    permission_classes = [IsOrganizationMember]
    serializer_class = NormalizedActivityDetailSerializer

    def get_queryset(self):
        return NormalizedActivity.objects.filter(
            organization=self.request.user.organization
        ).select_related("batch", "raw_row", "emission_estimate")
