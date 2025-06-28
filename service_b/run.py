import uvicorn
from fastapi import FastAPI, status, HTTPException
from starlette.responses import JSONResponse

from common.schemas import Serial, RequestModel, CreateTaskResponse, ResponseModel, TaskStatus
from common import db


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
async def create_task(id: Serial, payload: RequestModel) -> CreateTaskResponse:
    async with db.AsyncSessionLocal() as session:
        task = db.Task(equipment_id=id, payload=payload.model_dump())
        session.add(task)
        await session.commit()
        await session.refresh(task)
    return CreateTaskResponse(code=status.HTTP_201_CREATED, task_id=task.id)


@app.get(
    '/api/v1/equipment/cpe/{id}/task/{task}',
    tags=["Tasks"],
    summary="Получить сатус задачи для CPE",
    response_model=ResponseModel,
    response_description="Статус задачи",
    responses={
        status.HTTP_200_OK: {"model": ResponseModel, "description": "Ok"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModel, "description": "Task not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseModel, "description": "Internal error"},
    },
)
async def get_status(id: Serial, task: int) -> JSONResponse:
    task_status_resp_map = {
        TaskStatus.SUCCESS: (status.HTTP_200_OK, "Completed"),
        TaskStatus.FAILED: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal provisioning exception"),
    }
    async with db.AsyncSessionLocal() as session:
        task = await session.get(db.Task, task)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'The requested task is not found')
        if task.equipment_id != id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'The requested equipment is not found')
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
