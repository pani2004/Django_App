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
        source_raw = request.data.get("source", "")
        file = request.FILES.get("file")

        # Postman/clients sometimes attach the CSV to "source" by mistake
        if not file and hasattr(source_raw, "read"):
            file = source_raw
            source_raw = request.data.get("source_type") or request.POST.get("source", "")

        if isinstance(source_raw, str):
            source = source_raw.strip().upper()
        else:
            source = ""

        if not source and file:
            return Response(
                {
                    "detail": (
                        "Missing text field 'source'. Use form-data: source=SAP (Text) "
                        "and file=<csv> (File). Do not put the CSV on the source field."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if source not in DataSource.values:
            return Response(
                {"detail": "source must be SAP, UTILITY, or TRAVEL (text field, not a file)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not file:
            return Response(
                {"detail": "file is required — attach the CSV on the 'file' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
