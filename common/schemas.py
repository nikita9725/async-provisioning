from typing import Literal
from pydantic import BaseModel, constr, conint, Field

Serial = constr(pattern=r"^[a-zA-Z0-9]{6,}$")


class ConnectionParameters(BaseModel):
    """Набор параметров, необходимых для подключения к оборудованию."""

    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["admin"])
    vlan: int | None = None
    interfaces: list[int]


class RequestModel(BaseModel):
    """Запрос к оборудованию."""

    timeoutInSeconds: conint(gt=0, lt=60) = Field(
        ..., examples=[14], description="Время ожидания ответа от оборудования"
    )
    parameters: ConnectionParameters = Field(
        ...,
        description="Учётные данные и прочие параметры подключения",
        examples=[
            {"username": "admin", "password": "admin", "interfaces": [1, 2, 3, 4]}
        ],
    )


class ResponseModel(BaseModel):
    code: Literal[200]
    message: str = Field(examples=["success"])


class ErrorModel(BaseModel):
    code: int = Field(examples=[500])
    message: str = Field(examples=["Internal provisioning exception"])
