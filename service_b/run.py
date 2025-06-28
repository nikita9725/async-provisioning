import uvicorn
from fastapi import FastAPI, status
from common.schemas import Serial, RequestModel, CreateTaskResponse
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


def run_service(port: int = 8001) -> None:
    """Функция, стартующая сервис"""
    uvicorn.run(app, host="0.0.0.0", port=port)
