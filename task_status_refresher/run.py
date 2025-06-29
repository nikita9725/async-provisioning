import asyncio
from common.settings import settings
from common import db
from common.schemas import TaskStatus
from common.logger import get_logger


logger = get_logger()

async def refresh_statuses() -> None:
    logger.info("Refreshing statuses worker started")
    while True:
        async with db.AsyncSessionLocal() as session:
            await session.execute(
                db.Task.refresh_task_status_query(
                    TaskStatus.RUNNING,
                    TaskStatus.FAILED,
                    settings.refresh_status_timeout,
                )
            )
            await session.commit()
            logger.info("Statuses refreshed")
        await asyncio.sleep(settings.refresh_status_timeout)


def run_service() -> None:
    asyncio.run(refresh_statuses())
