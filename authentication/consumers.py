import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from .models import Collaboration
from django.utils import timezone

logger = logging.getLogger(__name__)

class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4001)
            return

        self.user = self.scope["user"]
        self.collab_uuid = self.scope['url_route']['kwargs']['collab_uuid']
        
        try:
            # Get collaboration by UUID
            self.collab = await self.get_collaboration()
            self.room_group_name = f"collab_{self.collab_uuid}"

            if await self.validate_access():
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
                await self.send_user_list()
                logger.info(f"User {self.user.email} connected to collaboration {self.collab_uuid}")
            else:
                await self.close(code=4003)
        except Collaboration.DoesNotExist:
            logger.error(f"Collaboration {self.collab_uuid} not found")
            await self.close(code=4004)
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close(code=4002)

    @database_sync_to_async
    def get_collaboration(self):
        """Get collaboration by UUID"""
        return Collaboration.objects.get(channel_group=self.collab_uuid)

    @database_sync_to_async
    def validate_access(self):
        """Verify user access using UUID"""
        return Collaboration.objects.filter(
            channel_group=self.collab_uuid,
            participants=self.user
        ).exists()

    @database_sync_to_async
    def get_participants(self):
        """Get participants list"""
        try:
            return list(self.collab.participants.values_list('email', flat=True))
        except Exception as e:
            logger.error(f"Participant fetch error: {str(e)}")
            return []

    async def send_user_list(self):
        """Send participant updates"""
        participants = await self.get_participants()
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'user_list', 'participants': participants}
            )
        except Exception as e:
            logger.error(f"User list error: {str(e)}")

    async def user_list(self, event):
        """Handle user list broadcasts"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'user_list',
                'participants': event['participants']
            }))
        except Exception as e:
            logger.error(f"User list send error: {str(e)}")

    async def receive(self, text_data):
        """Process incoming messages"""
        try:
            data = json.loads(text_data)
            if data.get('type') not in ['document_update', 'cursor_position']:
                raise ValueError("Invalid message type")
            
            data['user_id'] = str(self.user.id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': data['type'],
                    'data': data,
                    'sender_channel': self.channel_name
                }
            )
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Message processing error: {str(e)}")

    async def document_update(self, event):
        """Handle document changes"""
        try:
            if event['sender_channel'] != self.channel_name:
                event['data']['timestamp'] = timezone.now().isoformat()
                await self.send(text_data=json.dumps(event['data']))
        except Exception as e:
            logger.error(f"Document update failed: {str(e)}")

    async def cursor_position(self, event):
        """Handle cursor movements"""
        try:
            if event['sender_channel'] != self.channel_name:
                await self.send(text_data=json.dumps(event['data']))
        except Exception as e:
            logger.error(f"Cursor update failed: {str(e)}")

    async def disconnect(self, close_code):
        """Clean up on disconnect"""
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.email} disconnected")
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")