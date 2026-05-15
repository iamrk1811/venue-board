from django.db import connection
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import redis


def _check_db():
    try:
        connection.ensure_connection()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_redis():
    try:
        url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(url, socket_connect_timeout=2)
        client.ping()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    db = _check_db()
    cache = _check_redis()

    overall = "ok" if db["status"] == "ok" and cache["status"] == "ok" else "degraded"

    return Response(
        {
            "status": overall,
            "services": {
                "db": db,
                "redis": cache,
            },
        },
        status=200 if overall == "ok" else 503,
    )
