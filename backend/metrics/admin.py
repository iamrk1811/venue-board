from django.contrib import admin
from .models import VenueHourlyMetrics, VenueDailySummary, VenueItemDaily, Alert

admin.site.register(VenueHourlyMetrics)
admin.site.register(VenueDailySummary)
admin.site.register(VenueItemDaily)
admin.site.register(Alert)
