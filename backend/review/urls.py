from django.urls import path

from .views import (
    ActivityApproveView,
    ActivityAuditView,
    ActivityFlagView,
    ActivityRejectView,
    BulkApproveView,
    DashboardStatsView,
)

urlpatterns = [
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("activities/<int:pk>/approve/", ActivityApproveView.as_view(), name="activity-approve"),
    path("activities/<int:pk>/flag/", ActivityFlagView.as_view(), name="activity-flag"),
    path("activities/<int:pk>/reject/", ActivityRejectView.as_view(), name="activity-reject"),
    path("activities/<int:pk>/audit/", ActivityAuditView.as_view(), name="activity-audit"),
    path("activities/bulk-approve/", BulkApproveView.as_view(), name="activity-bulk-approve"),
]
