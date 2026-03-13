import json
import logging
from nats.aio.client import Client as NATS
from nats.js.errors import NotFoundError

logger = logging.getLogger("NatsClient")

class EventBus:
    def __init__(self):
        self.nc = NATS()
        self.js = None
        self.connected = False

    async def connect(self, servers=["nats://127.0.0.1:4222"]):
        try:
            await self.nc.connect(servers=servers)
            self.js = self.nc.jetstream()
            self.connected = True
            
            # Ensure the streams exist
            await self.setup_streams()
            logger.info(f"Connected to NATS JetStream cluster at {servers}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")

    async def setup_streams(self):
        # STREAM: Telemetry (Volatile, high throughput, short retention)
        try:
            await self.js.stream_info("TELEMETRY")
        except NotFoundError:
            await self.js.add_stream(name="TELEMETRY", subjects=["node.telemetry.>"], max_age=60) # keep for 60s
            
        # STREAM: Commands (Reliable delivery to Sentinels)
        try:
            await self.js.stream_info("COMMANDS")
        except NotFoundError:
            await self.js.add_stream(name="COMMANDS", subjects=["sentinel.broadcast.>"])

    async def publish_telemetry(self, node_id: str, payload: dict):
        if not self.connected: return
        subject = f"node.telemetry.{node_id}"
        await self.js.publish(subject, json.dumps(payload).encode())

    async def broadcast_sentinel_command(self, command: dict):
        if not self.connected: return
        subject = "sentinel.broadcast.global"
        # Push command down the wire. Sentinels subscribed to this will react instantly.
        await self.js.publish(subject, json.dumps(command).encode())

nats_bus = EventBus()
