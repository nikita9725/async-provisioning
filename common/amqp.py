import aio_pika
import json
from abc import ABC, abstractmethod
from .settings import settings
from logging import Logger


class QueueConsumerBase(ABC):
    queue_name: str
    routing_key: str

    def __init__(
        self, connection: aio_pika.abc.AbstractConnection, logger: Logger
    ) -> None:
        self._connection = connection
        self._logger = logger

    @abstractmethod
    async def process_message(self, message: dict) -> None:
        """Метод, отвечающий за обработку JSON сообщения"""

    async def consume(self) -> None:
        self._logger.info(f"{self.__class__} consumer is starting...")
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=settings.rmq_prefetch_count)
        queue = await channel.declare_queue(self.queue_name, auto_delete=False)
        async with queue.iterator() as q:
            async for message in q:
                await self._process_message(message)
        self._logger.info(f"{self.__class__} consumer is shutting down...")

    async def _process_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        async with message.process():
            message_json = json.loads(message.body)
            await self.process_message(message_json)


class QueueProducer:
    def __init__(self, connection: aio_pika.abc.AbstractConnection) -> None:
        self._connection = connection

    async def publish(self, message: dict, routing_key: str) -> None:
        channel = await self._connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key,
        )
