from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, conint, Field
from fastapi import status, Path


Serial = Annotated[
    str,
    Path(
        description="Серийный номер оборудования",
        pattern=r"^[A-Za-z0-9]{6,}$",
    ),
]


class CreateTaskResponse(BaseModel):
    code: int = Field(..., examples=[status.HTTP_201_CREATED])
    task_id: int = Field(..., examples=[42])


class ConnectionParameters(BaseModel):
    """Набор параметров, необходимых для подключения к оборудованию."""

    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["admin"])
    vlan: int | None = None
    interfaces: list[int]


class RequestModel(BaseModel):
    """Запрос к оборудованию."""

    timeout_in_seconds: conint(gt=0, lt=60) = Field(
        ..., examples=[14], description="Время ожидания ответа от оборудования"
    )
    parameters: ConnectionParameters = Field(
        ...,
        description="Учётные данные и прочие параметры подключения",
        examples=[
            {"username": "admin", "password": "admin", "interfaces": [1, 2, 3, 4]}
        ],
    )


class RequestModelMsg(RequestModel):
    equipment_id: str
    task_id: int


class ResponseModel(BaseModel):
    code: int = Field(examples=[status.HTTP_200_OK])
    message: str = Field(examples=["success"])


class TaskStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
