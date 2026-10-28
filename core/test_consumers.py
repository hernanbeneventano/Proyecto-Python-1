from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase

from config.asgi import application
from .models import Project


class TaskNotificationConsumerTests(TransactionTestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Proyecto de prueba")

    async def test_existing_project_accepts_connection_and_sends_echo_and_events(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/projects/{self.project.pk}/",
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        message = {"mensaje": "hola desde el cliente"}
        await communicator.send_json_to(message)
        self.assertEqual(
            await communicator.receive_json_from(),
            {"echo": message},
        )

        payload = {"type": "task.created", "task_id": 1}
        await get_channel_layer().group_send(
            f"project_{self.project.pk}",
            {"type": "task_notification", "payload": payload},
        )
        self.assertEqual(await communicator.receive_json_from(), payload)
        await communicator.disconnect()

    async def test_unknown_project_rejects_connection(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/projects/999999/",
        )

        connected, _ = await communicator.connect()

        self.assertFalse(connected)
