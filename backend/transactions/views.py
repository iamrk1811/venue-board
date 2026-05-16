from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.views import APIView
from rest_framework import status

from core.responses import success_response, error_response

from .serializers import TransactionIngestSerializer
from .services import TransactionService


class TransactionIngestView(APIView):
    @extend_schema(
        tags=["transactions"],
        summary="Ingest a POS transaction",
        description="Accepts a single transaction from a venue POS system",
        request=TransactionIngestSerializer,
        responses={
            201: OpenApiResponse(description="Transaction accepted and metrics updated"),
            400: OpenApiResponse(description="Validation error / malformed payload"),
            401: OpenApiResponse(description="Missing or invalid JWT token"),
        }
    )
    def post(self, request):
        serializer = TransactionIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = TransactionService.ingest(serializer.validated_data)
        if txn:
            return success_response(None, status=status.HTTP_201_CREATED)
        return error_response("something went wrong while creating txn", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
