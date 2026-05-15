from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from venues.models import Venue
from venues.serializers import VenueSerializer
from .models import Alert, VenueHourlyMetrics, VenueItemDaily
from .serializers import (
    AlertSerializer,
    HourlyMetricsSerializer,
    TopItemSerializer,
    VenueRankingSerializer,
)
from core.cache import get_summary

_TopItemInlineSerializer = inline_serializer(
    name="DashboardTopItem",
    fields={
        "item_id": serializers.CharField(),
        "item_name": serializers.CharField(),
        "total_qty": serializers.IntegerField(),
        "total_revenue": serializers.DecimalField(max_digits=12, decimal_places=2),
    },
)

_DashboardSummaryResponseSerializer = inline_serializer(
    name="DashboardSummaryResponse",
    fields={
        "total_sales_today": serializers.CharField(),
        "total_transactions_today": serializers.IntegerField(),
        "active_alert_count": serializers.IntegerField(),
        "venue_rankings": VenueRankingSerializer(many=True),
        "top_items": _TopItemInlineSerializer,
    },
)

_VenueDetailResponseSerializer = inline_serializer(
    name="VenueDetailResponse",
    fields={
        "venue": VenueSerializer(),
        "hourly_metrics": HourlyMetricsSerializer(many=True),
        "top_items": TopItemSerializer(many=True),
        "active_alerts": AlertSerializer(many=True),
    },
)


class DashboardSummaryView(APIView):
    @extend_schema(
        tags=["dashboard"],
        summary="Global dashboard summary",
        description=(
            "Returns overall summary along with venue ranked list"
        ),
        responses={
            200: _DashboardSummaryResponseSerializer,
            401: OpenApiResponse(description="Missing or invalid JWT token."),
        },
    )
    def get(self, request):
        return Response(get_summary())


class VenueDetailView(APIView):
    @extend_schema(
        tags=["dashboard"],
        summary="Venue detail",
        description=(
            "Returns hourly metrics for the last 24 hours and the top 10 items by revenue along with alerts"
        ),
        responses={
            200: _VenueDetailResponseSerializer,
            401: OpenApiResponse(description="Missing or invalid JWT token."),
            404: OpenApiResponse(description="Venue not found."),
        },
    )
    def get(self, request, venue_id):
        try:
            venue = Venue.objects.get(pk=venue_id)
        except Venue.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        today = timezone.now().date()
        since = timezone.now() - timedelta(hours=24)

        hourly = (
            VenueHourlyMetrics.objects
            .filter(venue=venue, hour__gte=since)
            .order_by("hour")
        )

        top_items = (
            VenueItemDaily.objects
            .filter(venue=venue, date=today)
            .order_by("-total_revenue")[:10]
        )

        active_alerts = (
            Alert.objects
            .filter(venue=venue, is_active=True)
            .order_by("-created_at")
        )

        return Response({
            "venue": VenueSerializer(venue).data,
            "hourly_metrics": HourlyMetricsSerializer(hourly, many=True).data,
            "top_items": TopItemSerializer(top_items, many=True).data,
            "active_alerts": AlertSerializer(active_alerts, many=True).data,
        })


class AlertListView(APIView):
    @extend_schema(
        tags=["alerts"],
        summary="List active alerts",
        description="Returns the 50 most recent active anomaly alerts across all venues.",
        responses={
            200: AlertSerializer(many=True),
            401: OpenApiResponse(description="Missing or invalid JWT token."),
        },
    )
    def get(self, request):
        alerts = (
            Alert.objects
            .filter(is_active=True)
            .select_related("venue")
            .order_by("-created_at")[:50]
        )
        return Response(AlertSerializer(alerts, many=True).data)
