import datetime as dt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.sql import Update
from sqlalchemy import DateTime, JSON, Enum, Integer, String, update
from .schemas import TaskStatus
from .settings import settings

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    equipment_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.now
    )
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.RUNNING
    )

    @classmethod
    def update_task_status_query(
        cls,
        task_id: int,
        equipment_id: str,
        status: TaskStatus,
    ) -> Update:
        return (
            update(cls)
            .where(cls.id == task_id, cls.equipment_id == equipment_id)
            .values(status=status)
        )

    @classmethod
    def refresh_task_status_query(
        cls, initial_status: TaskStatus, new_status: TaskStatus, timeout: int
    ) -> Update:
        return (
            update(cls)
            .where(
                cls.created_at - dt.datetime.now() <= timeout,
                cls.status == initial_status,
            )
            .values(status=new_status)
        )


engine = create_async_engine(settings.db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
