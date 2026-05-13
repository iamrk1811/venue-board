from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from venues.models import Venue
from venues.serializers import VenueSerializer
from .models import Alert, VenueDailySummary, VenueHourlyMetrics, VenueItemDaily
from .serializers import (
    AlertSerializer,
    HourlyMetricsSerializer,
    TopItemSerializer,
    VenueRankingSerializer,
)

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
            "Returns today's aggregated totals, venue rankings by revenue, "
            "the top 10 items sold across all venues, and a count of active alerts. "
            "All data is read from precomputed metric tables — no raw transaction scans."
        ),
        responses={
            200: _DashboardSummaryResponseSerializer,
            401: OpenApiResponse(description="Missing or invalid JWT token."),
        },
    )
    def get(self, request):
        today = timezone.now().date()

        summaries = (
            VenueDailySummary.objects
            .filter(date=today)
            .select_related("venue")
            .order_by("-total_sales")
        )

        total_sales = sum(s.total_sales for s in summaries)
        total_transactions = sum(s.transaction_count for s in summaries)

        top_items = list(
            VenueItemDaily.objects
            .filter(date=today)
            .values("item_id", "item_name")
            .annotate(
                total_qty=Sum("total_qty"),
                total_revenue=Sum("total_revenue"),
            )
            .order_by("-total_revenue")[:10]
        )

        active_alert_count = Alert.objects.filter(is_active=True).count()

        return Response({
            "total_sales_today": str(total_sales),
            "total_transactions_today": total_transactions,
            "active_alert_count": active_alert_count,
            "venue_rankings": VenueRankingSerializer(summaries, many=True).data,
            "top_items": top_items,
        })


class VenueDetailView(APIView):
    @extend_schema(
        tags=["dashboard"],
        summary="Venue detail",
        description=(
            "Returns hourly metrics for the last 24 hours, the top 10 items by revenue "
            "for today, and any active anomaly alerts for the requested venue."
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
