# authentication/middleware.py
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class WebSocketAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        user = await self.get_user(scope)
        scope['user'] = user
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, scope):
        session = scope.get('session')
        if not session:
            return AnonymousUser()
        return session.get('_auth_user_id') or AnonymousUser()