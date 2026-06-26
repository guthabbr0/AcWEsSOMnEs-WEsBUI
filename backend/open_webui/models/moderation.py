import time
import uuid
from typing import Optional

from open_webui.internal.db import Base, get_async_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, JSON, Text, and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserModerationBan(Base):
    __tablename__ = 'user_moderation_ban'

    id = Column(Text, primary_key=True, unique=True)
    user_id = Column(Text, nullable=False, index=True)
    scope = Column(Text, nullable=False, index=True)
    reason = Column(Text, nullable=False)

    model_ids = Column(JSON, nullable=True)
    channel_ids = Column(JSON, nullable=True)

    starts_at = Column(BigInteger, nullable=False, index=True)
    expires_at = Column(BigInteger, nullable=True, index=True)
    created_at = Column(BigInteger, nullable=False)
    created_by = Column(Text, nullable=False)

    revoked_at = Column(BigInteger, nullable=True, index=True)
    revoked_by = Column(Text, nullable=True)


class UserModerationBanModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    scope: str
    reason: str
    model_ids: list[str] | None = None
    channel_ids: list[str] | None = None
    starts_at: int
    expires_at: int | None = None
    created_at: int
    created_by: str
    revoked_at: int | None = None
    revoked_by: str | None = None


class UserModerationBanForm(BaseModel):
    user_id: str
    scope: str
    reason: str
    model_ids: list[str] | None = None
    channel_ids: list[str] | None = None
    starts_at: int | None = None
    expires_at: int | None = None
    duration_seconds: int | None = None


MODERATION_SCOPES = {'site', 'models', 'channels'}


def normalize_moderation_scope(scope: str) -> str:
    normalized = str(scope or '').strip().lower()
    if normalized not in MODERATION_SCOPES:
        raise ValueError('Invalid moderation scope.')
    return normalized


def normalize_target_ids(value) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        return []
    normalized = []
    for item in value:
        item_id = str(item or '').strip()
        if item_id and item_id not in normalized:
            normalized.append(item_id)
    return normalized


def ban_matches_target(ban: UserModerationBanModel, model_id: str | None = None, channel_id: str | None = None) -> bool:
    if ban.scope == 'models':
        model_ids = ban.model_ids or []
        return not model_ids or bool(model_id and model_id in model_ids)

    if ban.scope == 'channels':
        channel_ids = ban.channel_ids or []
        return not channel_ids or bool(channel_id and channel_id in channel_ids)

    return True


def get_moderation_ban_message(ban: UserModerationBanModel) -> str:
    if ban.scope == 'site':
        action = 'accessing this website'
    elif ban.scope == 'models':
        action = 'chatting with this model'
    else:
        action = 'typing in this channel'

    expiry = f' Expires at: {ban.expires_at}.' if ban.expires_at else ''
    return f'You are temporarily banned from {action}. Reason: {ban.reason}.{expiry}'


class UserModerationBanTable:
    async def insert_new_ban(
        self,
        form_data: UserModerationBanForm,
        created_by: str,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationBanModel:
        now = int(time.time())
        scope = normalize_moderation_scope(form_data.scope)
        starts_at = form_data.starts_at or now
        expires_at = form_data.expires_at
        if expires_at is None and form_data.duration_seconds:
            expires_at = starts_at + max(1, int(form_data.duration_seconds))

        reason = str(form_data.reason or '').strip()
        if not reason:
            raise ValueError('A moderation reason is required.')

        model_ids = normalize_target_ids(form_data.model_ids)
        channel_ids = normalize_target_ids(form_data.channel_ids)
        if scope != 'models':
            model_ids = None
        if scope != 'channels':
            channel_ids = None

        async with get_async_db_context(db) as session:
            record = UserModerationBan(
                id=str(uuid.uuid4()),
                user_id=form_data.user_id,
                scope=scope,
                reason=reason[:1000],
                model_ids=model_ids,
                channel_ids=channel_ids,
                starts_at=starts_at,
                expires_at=expires_at,
                created_at=now,
                created_by=created_by,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return UserModerationBanModel.model_validate(record)

    async def get_bans(
        self,
        user_id: str | None = None,
        include_inactive: bool = True,
        db: Optional[AsyncSession] = None,
    ) -> list[UserModerationBanModel]:
        now = int(time.time())
        async with get_async_db_context(db) as session:
            stmt = select(UserModerationBan)
            if user_id:
                stmt = stmt.where(UserModerationBan.user_id == user_id)
            if not include_inactive:
                stmt = stmt.where(
                    UserModerationBan.revoked_at.is_(None),
                    UserModerationBan.starts_at <= now,
                    or_(UserModerationBan.expires_at.is_(None), UserModerationBan.expires_at > now),
                )
            stmt = stmt.order_by(UserModerationBan.created_at.desc())
            result = await session.execute(stmt)
            return [UserModerationBanModel.model_validate(row) for row in result.scalars().all()]

    async def get_active_bans(
        self,
        user_id: str,
        scope: str | None = None,
        db: Optional[AsyncSession] = None,
    ) -> list[UserModerationBanModel]:
        now = int(time.time())
        async with get_async_db_context(db) as session:
            stmt = select(UserModerationBan).where(
                UserModerationBan.user_id == user_id,
                UserModerationBan.revoked_at.is_(None),
                UserModerationBan.starts_at <= now,
                or_(UserModerationBan.expires_at.is_(None), UserModerationBan.expires_at > now),
            )
            if scope:
                stmt = stmt.where(UserModerationBan.scope == normalize_moderation_scope(scope))
            stmt = stmt.order_by(UserModerationBan.created_at.desc())
            result = await session.execute(stmt)
            return [UserModerationBanModel.model_validate(row) for row in result.scalars().all()]

    async def get_active_site_ban(self, user_id: str, db: Optional[AsyncSession] = None) -> UserModerationBanModel | None:
        bans = await self.get_active_bans(user_id, scope='site', db=db)
        return bans[0] if bans else None

    async def get_active_model_ban(
        self,
        user_id: str,
        model_id: str,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationBanModel | None:
        bans = await self.get_active_bans(user_id, scope='models', db=db)
        return next((ban for ban in bans if ban_matches_target(ban, model_id=model_id)), None)

    async def get_active_channel_ban(
        self,
        user_id: str,
        channel_id: str,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationBanModel | None:
        bans = await self.get_active_bans(user_id, scope='channels', db=db)
        return next((ban for ban in bans if ban_matches_target(ban, channel_id=channel_id)), None)

    async def revoke_ban(
        self,
        ban_id: str,
        revoked_by: str,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationBanModel | None:
        async with get_async_db_context(db) as session:
            record = await session.get(UserModerationBan, ban_id)
            if not record:
                return None
            record.revoked_at = int(time.time())
            record.revoked_by = revoked_by
            await session.commit()
            await session.refresh(record)
            return UserModerationBanModel.model_validate(record)

    async def delete_user_bans(self, user_id: str, db: Optional[AsyncSession] = None) -> bool:
        async with get_async_db_context(db) as session:
            await session.execute(delete(UserModerationBan).where(UserModerationBan.user_id == user_id))
            await session.commit()
            return True


UserModerationBans = UserModerationBanTable()
