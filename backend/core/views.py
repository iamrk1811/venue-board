import redis

from django.conf import settings
from django.db import connection
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from core.responses import error_response, success_response


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

    services = {"db": db, "redis": cache}
    if overall == "ok":
        return success_response({"services": services})
    return error_response("Service degraded", detail={"services": services}, status=503)
