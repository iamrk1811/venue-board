from django.urls import path
from .views import DashboardSummaryView, VenueDetailView, AlertListView

urlpatterns = [
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("venues/<int:venue_id>/detail/", VenueDetailView.as_view(), name="venue-detail"),
    path("alerts/", AlertListView.as_view(), name="alert-list"),
]
