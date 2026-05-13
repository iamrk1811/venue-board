from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_from_token(token_str):
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import TokenError
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        token = AccessToken(token_str)
        user = User.objects.get(pk=token["user_id"])
        return user
    except (TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            query_string = scope.get("query_string", b"").decode()
            params = parse_qs(query_string)
            token_list = params.get("token", [])

            if token_list:
                scope["user"] = await get_user_from_token(token_list[0])
            else:
                scope["user"] = AnonymousUser()

            if not scope["user"].is_authenticated:
                from channels.exceptions import DenyConnection
                raise DenyConnection("Invalid or missing token")

        return await super().__call__(scope, receive, send)
