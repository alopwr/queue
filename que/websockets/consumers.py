from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TeacherConsumer(AsyncJsonWebsocketConsumer):
    groups = ["teachers", "queue_listeners"]

    async def queue_ticket_appended(self, event):
        await self.send_json(
            {
                "msg_type": "queue.ticket_appended",
                "display_name": event["display_name"],
                "principal_name": event["principal_name"],
            },
        )

    async def queue_ticket_deleted(self, event):
        await self.send_json({"msg_type": "queue.ticket_deleted"},)


class StudentConsumer(AsyncJsonWebsocketConsumer):
    groups = ["students", "queue_listeners"]
    position = None
    average_meeting_time = None
    userId = None

    async def connect(self):
        self.userId = self.scope["url_route"]["kwargs"]["id"]
        await self.accept()

    @database_sync_to_async
    def load_status(self):
        from ..models import QueueTicket, average_meeting_time

        ticket = QueueTicket.objects.get(user_id=self.userId)
        self.position = ticket.position_in_queue
        self.average_meeting_time = average_meeting_time()

    async def queue_ticket_deleted(self, event):
        if event["position"] < self.position:
            self.position -= 1
            self.average_meeting_time = event["average"]
            await self.send_update()

    async def queue_cleared(self, _):
        await self.send_json({"msg_type": "queue.cleared",},)

    async def queue_next(self, event):
        self.position -= 1
        self.average_meeting_time = event["average"]
        await self.send_update()

    async def send_update(self):
        await self.send_json(
            {
                "msg_type": "queue.updated",
                "estimated_time": self.average_meeting_time * self.position,
                "position": self.position,
            },
        )

    async def receive_json(self, content, **kwargs):
        if content["type"] == "get.update":
            await self.load_status()
            await self.send_update()
