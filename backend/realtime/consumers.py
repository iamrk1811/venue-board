import json
from channels.generic.websocket import AsyncWebsocketConsumer


class DashboardConsumer(AsyncWebsocketConsumer):
    GROUP = "dashboard"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    # --- Handlers for group_send events ---

    async def summary_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "summary_updated",
            "summary": event["summary"],
            "venue_id": event["venue_id"],
        }))

    async def alert_triggered(self, event):
        await self.send(text_data=json.dumps({
            "type": "alert_triggered",
            "alert": event["alert"],
        }))

    async def alert_resolved(self, event):
        await self.send(text_data=json.dumps({
            "type": "alert_resolved",
            "alert_id": event["alert_id"],
        }))
