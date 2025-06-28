import random
import uvicorn
from fastapi import FastAPI, Path, HTTPException, status
from fastapi.responses import JSONResponse
from common.schemas import ResponseModel, ErrorModel, RequestModel, Serial

tags_metadata = [
    {
        "name": "Provisioning",
        "description": "Операции конфигурирования абонентского оборудования",
    }
]

app = FastAPI(
    title="Service-A • Provisioning stub",
    description="Закрытый сервис, имитирующий долгое конфигурирование CPE.",
    version="1.0.0",
    contact={"name": "NOC team", "email": "noc@example.com"},
    docs_url="/swagger",
    redoc_url=None,
    openapi_url="/swagger.json",
    openapi_tags=tags_metadata,
)


@app.post(
    "/api/v1/equipment/cpe/{id}",
    tags=["Provisioning"],
    summary="Запуск конфигурирования оборудования",
    response_model=ResponseModel,
    responses={
        404: {"model": ErrorModel, "description": "Equipment not found"},
        500: {"model": ErrorModel, "description": "Internal error"},
    },
)
async def configure_device(
    body: RequestModel,
    id: Serial = Path(..., title="Серийный номер"),
):
    """
    Эндпоинт имитирует **долгое** конфигурирование устройства.
    В 10 % случаев отдаёт *500*, в 5 % — *404*.
    """
    # await asyncio.sleep(60)
    if random.random() < 0.1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal provisioning exception",
        )
    if random.random() < 0.05:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested equipment is not found",
        )
    return JSONResponse({"code": status.HTTP_200_OK, "message": "success"})


def run_service(port: int = 8000) -> None:
    """Функция, стартующая сервис"""
    uvicorn.run(app, host="0.0.0.0", port=port)
