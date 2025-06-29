import asyncio
import aio_pika
import httpx
from pydantic import ValidationError

from common import db
from common.settings import settings
from common.amqp import QueueConsumerBase
from common.schemas import RequestModelMsg, ResponseModel, TaskStatus
from common.logger import get_logger


class WorkerQueueConsumer(QueueConsumerBase):
    queue_name = "provisioning_tasks"
    routing_key = settings.rmq_taks_routing_key

    async def process_message(self, message: dict) -> None:
        request = RequestModelMsg(**message)
        async with db.AsyncSessionLocal() as session:
            stmt = db.Task.update_task_status_query(
                request.task_id, request.equipment_id, TaskStatus.FAILED
            )
            try:
                response = await self._send_provisioning_request(request)
                if response.code == httpx.codes.OK:
                    stmt = db.Task.update_task_status_query(
                        request.task_id, request.equipment_id, TaskStatus.SUCCESS
                    )
            except httpx.HTTPError:
                self._logger.exception("Service A Connection error")
            except ValidationError:
                self._logger.exception("Service A Validation error")
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def _send_provisioning_request(message: RequestModelMsg) -> ResponseModel:
        async with httpx.AsyncClient(timeout=settings.read_timeout) as client:
            response = await client.post(
                settings.provisioning_service_url + f"/api/v1/equipment/cpe/{message.equipment_id}",
                json=message.model_dump(),
            )
            print(response.json())
            return ResponseModel(**response.json())


async def consume() -> None:
    logger = get_logger()
    connection = await aio_pika.connect_robust(str(settings.rmq_url))
    async with connection:
        consumer = WorkerQueueConsumer(connection, logger)
        await consumer.consume()


def run_service() -> None:
    asyncio.run(consume())
