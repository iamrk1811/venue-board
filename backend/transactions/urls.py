from django.urls import path
from .views import TransactionIngestView

urlpatterns = [
    path("transactions/", TransactionIngestView.as_view(), name="transaction-ingest"),
]
