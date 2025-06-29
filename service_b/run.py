import aio_pika
import uvicorn
from typing import AsyncGenerator
from fastapi import FastAPI, status, HTTPException, Depends
from starlette.responses import JSONResponse

from common.schemas import (
    Serial,
    RequestModel,
    CreateTaskResponse,
    ResponseModel,
    TaskStatus,
    RequestModelMsg,
)
from common import db
from common.settings import settings
from common.amqp import QueueProducer


async def get_db_session() -> AsyncGenerator[db.AsyncSessionLocal, None]:
    async with db.AsyncSessionLocal() as session:
        yield session


async def get_rmq_connect() -> AsyncGenerator[aio_pika.abc.AbstractConnection, None]:
    connection = await aio_pika.connect_robust(settings.rmq_url)
    async with connection:
        yield connection


app = FastAPI(
    title="Service B",
    version="1.0.0",
    description="API-сервис для создания задач на CPE-оборудовании",
    contact={"name": "NOC team", "email": "noc@example.com"},
    docs_url="/swagger",
    redoc_url=None,
    openapi_url="/swagger.json",
)


@app.post(
    "/api/v1/equipment/cpe/{id}/task",
    tags=["Tasks"],
    summary="Создать задачу для CPE",
    response_model=CreateTaskResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Результат создания задачи",
)
async def create_task(
    id: Serial,
    payload: RequestModel,
    rmq_connection: aio_pika.abc.AbstractConnection = Depends(get_rmq_connect),
    db_session: db.AsyncSessionLocal = Depends(get_db_session),
) -> CreateTaskResponse:
    qp = QueueProducer(rmq_connection)
    async with db_session.begin():
        task = db.Task(equipment_id=id, payload=payload.model_dump())
        db_session.add(task)
        await db_session.flush()
        msg_obj = RequestModelMsg(
            **payload.model_dump(), equipment_id=task.equipment_id, task_id=task.id
        )
        try:
            await qp.publish(msg_obj.model_dump(), settings.rmq_taks_routing_key)
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as exc:
            raise HTTPException(
                status_code=500, detail="Creating task internal error"
            ) from exc
    return CreateTaskResponse(code=status.HTTP_201_CREATED, task_id=task.id)


@app.get(
    "/api/v1/equipment/cpe/{id}/task/{task}",
    tags=["Tasks"],
    summary="Получить сатус задачи для CPE",
    response_model=ResponseModel,
    response_description="Статус задачи",
    responses={
        status.HTTP_200_OK: {"model": ResponseModel, "description": "Ok"},
        status.HTTP_404_NOT_FOUND: {
            "model": ResponseModel,
            "description": "Task not found",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ResponseModel,
            "description": "Internal error",
        },
    },
)
async def get_status(
    id: Serial, task: int, db_session: db.AsyncSessionLocal = Depends(get_db_session)
) -> JSONResponse:
    task_status_resp_map = {
        TaskStatus.SUCCESS: (status.HTTP_200_OK, "Completed"),
        TaskStatus.FAILED: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal provisioning exception",
        ),
    }
    task = await db_session.get(db.Task, task)
    if not task:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "The requested task is not found"
        )
    if task.equipment_id != id:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "The requested equipment is not found"
        )
    status_code, msg = task_status_resp_map.get(
        task.status, (status.HTTP_200_OK, "Task is still running")
    )
    return JSONResponse(
        status_code=status_code,
        content=ResponseModel(code=status_code, message=msg).model_dump(),
    )


def run_service(port: int = 8001) -> None:
    """Функция, стартующая сервис"""
    uvicorn.run(app, host="0.0.0.0", port=port)
