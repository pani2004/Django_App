from django.urls import path

from .views import (
    ActivityDetailView,
    ActivityListView,
    BatchDetailView,
    BatchListView,
    BatchUploadView,
)

urlpatterns = [
    path("batches/upload/", BatchUploadView.as_view(), name="batch-upload"),
    path("batches/", BatchListView.as_view(), name="batch-list"),
    path("batches/<int:pk>/", BatchDetailView.as_view(), name="batch-detail"),
    path("activities/", ActivityListView.as_view(), name="activity-list"),
    path("activities/<int:pk>/", ActivityDetailView.as_view(), name="activity-detail"),
]
