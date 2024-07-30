from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import subprocess


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.process = await asyncio.create_subprocess_shell(
            "dbus-monitor \"interface='com.kylin.AppManager', member='LaunchApp'\"",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await self.accept()
        asyncio.create_task(self.send_app_launch_notifications())

    async def disconnect(self, close_code):
        self.process.terminate()
        await self.process.wait()

    async def send_app_launch_notifications(self):
        while True:
            line = await self.process.stdout.readline()
            if line:
                line = line.decode().strip()  # Assuming output is encoded in utf-8
                print("Received line:", line)  # Debug output
                if "string" in line:
                    app_path = line.strip().split(' ')[1]
                    await self.send(app_path)  # Send the app path to the client

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
