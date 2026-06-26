import time
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, Integer, Text, delete, select

from open_webui.internal.db import Base, get_async_db_context
from sqlalchemy.ext.asyncio import AsyncSession


class ModelHealthCheck(Base):
    __tablename__ = 'model_health_check'

    id = Column(Text, primary_key=True, unique=True)
    model_id = Column(Text, nullable=False, index=True)
    model_name = Column(Text, nullable=False)
    owned_by = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False)
    latency_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    checked_at = Column(BigInteger, nullable=False, index=True)


class ModelHealthCheckModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_id: str
    model_name: str
    owned_by: Optional[str] = None
    status: bool
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    checked_at: int


class ModelHealthCheckForm(BaseModel):
    model_id: str
    model_name: str
    owned_by: Optional[str] = None
    status: bool
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    checked_at: Optional[int] = None


class ModelHealthCheckTable:
    async def insert_checks(
        self, checks: list[ModelHealthCheckForm], db: Optional[AsyncSession] = None
    ) -> list[ModelHealthCheckModel]:
        if not checks:
            return []

        inserted_checks: list[ModelHealthCheckModel] = []

        async with get_async_db_context(db) as db:
            for check in checks:
                payload = check.model_dump()
                payload['id'] = str(uuid.uuid4())
                payload['checked_at'] = payload.get('checked_at') or int(time.time())

                record = ModelHealthCheck(**payload)
                db.add(record)
                inserted_checks.append(ModelHealthCheckModel.model_validate(record))

            await db.commit()

        return inserted_checks

    async def get_checks_since(
        self, since: int, db: Optional[AsyncSession] = None
    ) -> list[ModelHealthCheckModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(
                select(ModelHealthCheck)
                .where(ModelHealthCheck.checked_at >= since)
                .order_by(ModelHealthCheck.checked_at.asc(), ModelHealthCheck.model_name.asc())
            )
            records = result.scalars().all()
            return [ModelHealthCheckModel.model_validate(record) for record in records]

    async def get_latest_check_at(self, db: Optional[AsyncSession] = None) -> Optional[int]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(ModelHealthCheck).order_by(ModelHealthCheck.checked_at.desc()).limit(1))
            record = result.scalars().first()
            return record.checked_at if record else None

    async def delete_checks_before(self, before: int, db: Optional[AsyncSession] = None) -> int:
        async with get_async_db_context(db) as db:
            result = await db.execute(delete(ModelHealthCheck).where(ModelHealthCheck.checked_at < before))
            await db.commit()
            return int(result.rowcount or 0)


ModelHealthChecks = ModelHealthCheckTable()
