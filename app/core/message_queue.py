import aio_pika
import json
from aio_pika import abc
from typing import Any, Dict, Optional, Awaitable, Callable
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self):
        self.connection: Optional[abc.AbstractRobustConnection] = None
        self.channel: Optional[abc.AbstractChannel] = None

    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def publish_message(self, queue_name: str, message: Dict[str, Any], priority: int = 0):
        """Publish message to queue"""
        if self.channel is None:
            await self.connect()

        channel = self.channel
        assert channel is not None

        await channel.declare_queue(queue_name, durable=True)

        message_body = json.dumps(message).encode()
        message_obj = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            priority=priority
        )

        await channel.default_exchange.publish(
            message_obj,
            routing_key=queue_name
        )
        logger.info(f"Published message to queue: {queue_name}")

    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any]], Awaitable[Any]]
    ):
        """Consume messages from queue"""
        if self.channel is None:
            await self.connect()

        channel = self.channel
        assert channel is not None

        queue = await channel.declare_queue(queue_name, durable=True)

        async def process_message(message: abc.AbstractIncomingMessage):
            async with message.process():
                try:
                    message_data = json.loads(message.body.decode())
                    await callback(message_data)
                    logger.info(f"Processed message from queue: {queue_name}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Requeue message on failure
                    await message.nack(requeue=True)

        await queue.consume(process_message)
        logger.info(f"Started consuming messages from queue: {queue_name}")

    async def close(self):
        """Close RabbitMQ connection"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("Closed RabbitMQ connection")

# Global message queue instance
message_queue = MessageQueue()