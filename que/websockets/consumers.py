from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings


class TeacherConsumer(AsyncJsonWebsocketConsumer):
    groups = ['teachers', "queue_listeners"]

    async def queue_ticket_appended(self, event):
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_TICKET_APPEND,
                "display_name": event["display_name"],
                "principal_name": event["principal_name"],
            },
        )

    async def queue_ticket_deleted(self, event):
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_TICKET_DELETE,
                "position": event["position"],
                "principal_name": event["principal_name"],
            },
        )


class StudentConsumer(AsyncJsonWebsocketConsumer):
    groups = ['students', "queue_listeners"]

    async def queue_ticket_deleted(self, event):
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_TICKET_DELETE,
                "position": event["position"],
                "principal_name": event["principal_name"],
            },
        )

    async def queue_cleared(self, _):
        await self.send_json({"msg_type": settings.MSG_TYPE_TICKET_CLEAR, }, )

    async def queue_next(self, _):
        await self.send_json({"msg_type": settings.MSG_TYPE_TICKET_NEXT, }, )
