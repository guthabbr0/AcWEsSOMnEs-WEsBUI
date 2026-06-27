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


class UserModerationAppeal(Base):
    __tablename__ = 'user_moderation_appeal'

    id = Column(Text, primary_key=True, unique=True)
    ban_id = Column(Text, nullable=False, index=True)
    user_id = Column(Text, nullable=False, index=True)
    message = Column(Text, nullable=False)
    status = Column(Text, nullable=False, index=True)
    created_at = Column(BigInteger, nullable=False, index=True)
    resolved_at = Column(BigInteger, nullable=True, index=True)
    resolved_by = Column(Text, nullable=True)
    resolution_note = Column(Text, nullable=True)


class UserModerationAuditLog(Base):
    __tablename__ = 'user_moderation_audit_log'

    id = Column(Text, primary_key=True, unique=True)
    actor_user_id = Column(Text, nullable=True, index=True)
    target_user_id = Column(Text, nullable=True, index=True)
    action = Column(Text, nullable=False, index=True)
    ban_id = Column(Text, nullable=True, index=True)
    appeal_id = Column(Text, nullable=True, index=True)
    data = Column(JSON, nullable=True)
    created_at = Column(BigInteger, nullable=False, index=True)


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


class UserModerationAppealModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ban_id: str
    user_id: str
    message: str
    status: str
    created_at: int
    resolved_at: int | None = None
    resolved_by: str | None = None
    resolution_note: str | None = None


class UserModerationAppealForm(BaseModel):
    ban_id: str
    message: str


class UserModerationAppealResolveForm(BaseModel):
    status: str = 'resolved'
    resolution_note: str | None = None


class UserModerationAuditLogModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_user_id: str | None = None
    target_user_id: str | None = None
    action: str
    ban_id: str | None = None
    appeal_id: str | None = None
    data: dict | None = None
    created_at: int


class UserModerationRiskModel(BaseModel):
    user_id: str
    score: int
    level: str
    active_bans: int
    total_bans: int
    pending_appeals: int
    rejected_appeals: int
    recent_events: int
    reasons: list[str]


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


def get_moderation_ban_payload(ban: UserModerationBanModel) -> dict:
    return {
        **ban.model_dump(),
        'message': get_moderation_ban_message(ban),
    }


class UserModerationBanTable:
    async def add_audit_log(
        self,
        action: str,
        actor_user_id: str | None = None,
        target_user_id: str | None = None,
        ban_id: str | None = None,
        appeal_id: str | None = None,
        data: dict | None = None,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationAuditLogModel:
        async with get_async_db_context(db) as session:
            record = UserModerationAuditLog(
                id=str(uuid.uuid4()),
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=str(action or '').strip()[:128],
                ban_id=ban_id,
                appeal_id=appeal_id,
                data=data or {},
                created_at=int(time.time()),
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return UserModerationAuditLogModel.model_validate(record)

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
            ban = UserModerationBanModel.model_validate(record)

        await self.add_audit_log(
            'ban.created',
            actor_user_id=created_by,
            target_user_id=ban.user_id,
            ban_id=ban.id,
            data={'scope': ban.scope, 'expires_at': ban.expires_at},
            db=db,
        )
        return ban

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

    async def get_ban_by_id(
        self,
        ban_id: str,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationBanModel | None:
        async with get_async_db_context(db) as session:
            record = await session.get(UserModerationBan, ban_id)
            return UserModerationBanModel.model_validate(record) if record else None

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
            ban = UserModerationBanModel.model_validate(record)

        await self.add_audit_log(
            'ban.revoked',
            actor_user_id=revoked_by,
            target_user_id=ban.user_id,
            ban_id=ban.id,
            data={'scope': ban.scope},
            db=db,
        )
        return ban

    async def create_appeal(
        self,
        form_data: UserModerationAppealForm,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationAppealModel:
        message = str(form_data.message or '').strip()
        if not message:
            raise ValueError('Appeal message is required.')
        if len(message) > 4000:
            message = message[:4000]

        ban = await self.get_ban_by_id(form_data.ban_id, db=db)
        if not ban or ban.revoked_at:
            raise ValueError('This ban is no longer active.')
        active_ban = await self.get_active_site_ban(ban.user_id, db=db)
        if not active_ban or active_ban.id != ban.id:
            raise ValueError('This ban is no longer active.')

        async with get_async_db_context(db) as session:
            record = UserModerationAppeal(
                id=str(uuid.uuid4()),
                ban_id=ban.id,
                user_id=ban.user_id,
                message=message,
                status='pending',
                created_at=int(time.time()),
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            appeal = UserModerationAppealModel.model_validate(record)

        await self.add_audit_log(
            'appeal.created',
            actor_user_id=ban.user_id,
            target_user_id=ban.user_id,
            ban_id=ban.id,
            appeal_id=appeal.id,
            db=db,
        )
        return appeal

    async def get_appeals(
        self,
        user_id: str | None = None,
        status: str | None = None,
        db: Optional[AsyncSession] = None,
    ) -> list[UserModerationAppealModel]:
        async with get_async_db_context(db) as session:
            stmt = select(UserModerationAppeal)
            if user_id:
                stmt = stmt.where(UserModerationAppeal.user_id == user_id)
            if status:
                stmt = stmt.where(UserModerationAppeal.status == status)
            stmt = stmt.order_by(UserModerationAppeal.created_at.desc())
            result = await session.execute(stmt)
            return [UserModerationAppealModel.model_validate(row) for row in result.scalars().all()]

    async def resolve_appeal(
        self,
        appeal_id: str,
        form_data: UserModerationAppealResolveForm,
        resolved_by: str,
        db: Optional[AsyncSession] = None,
    ) -> UserModerationAppealModel | None:
        status_value = str(form_data.status or 'resolved').strip().lower()
        if status_value not in {'resolved', 'rejected'}:
            status_value = 'resolved'

        async with get_async_db_context(db) as session:
            record = await session.get(UserModerationAppeal, appeal_id)
            if not record:
                return None
            record.status = status_value
            record.resolved_at = int(time.time())
            record.resolved_by = resolved_by
            record.resolution_note = str(form_data.resolution_note or '').strip()[:2000] or None
            await session.commit()
            await session.refresh(record)
            appeal = UserModerationAppealModel.model_validate(record)

        await self.add_audit_log(
            f'appeal.{status_value}',
            actor_user_id=resolved_by,
            target_user_id=appeal.user_id,
            ban_id=appeal.ban_id,
            appeal_id=appeal.id,
            data={'resolution_note': appeal.resolution_note},
            db=db,
        )
        return appeal

    async def get_audit_logs(
        self,
        user_id: str | None = None,
        action_prefix: str | None = None,
        limit: int = 100,
        db: Optional[AsyncSession] = None,
    ) -> list[UserModerationAuditLogModel]:
        async with get_async_db_context(db) as session:
            stmt = select(UserModerationAuditLog)
            if user_id:
                stmt = stmt.where(
                    or_(
                        UserModerationAuditLog.target_user_id == user_id,
                        UserModerationAuditLog.actor_user_id == user_id,
                    )
                )
            if action_prefix:
                stmt = stmt.where(UserModerationAuditLog.action.like(f'{action_prefix}%'))
            stmt = stmt.order_by(UserModerationAuditLog.created_at.desc()).limit(max(1, min(int(limit or 100), 500)))
            result = await session.execute(stmt)
            return [UserModerationAuditLogModel.model_validate(row) for row in result.scalars().all()]

    async def get_user_risk(self, user_id: str, db: Optional[AsyncSession] = None) -> UserModerationRiskModel:
        active_bans = await self.get_active_bans(user_id, db=db)
        all_bans = await self.get_bans(user_id=user_id, include_inactive=True, db=db)
        appeals = await self.get_appeals(user_id=user_id, db=db)
        audit_logs = await self.get_audit_logs(user_id=user_id, limit=200, db=db)

        pending_appeals = len([appeal for appeal in appeals if appeal.status == 'pending'])
        rejected_appeals = len([appeal for appeal in appeals if appeal.status == 'rejected'])
        now = int(time.time())
        recent_events = len([entry for entry in audit_logs if entry.created_at >= now - 7 * 24 * 60 * 60])

        score = 0
        reasons = []
        if active_bans:
            score += min(50, len(active_bans) * 25)
            reasons.append(f'{len(active_bans)} active ban(s)')
        if all_bans:
            score += min(25, len(all_bans) * 5)
            reasons.append(f'{len(all_bans)} total ban(s)')
        if rejected_appeals:
            score += min(15, rejected_appeals * 5)
            reasons.append(f'{rejected_appeals} rejected appeal(s)')
        if recent_events:
            score += min(10, recent_events * 2)
            reasons.append(f'{recent_events} recent moderation event(s)')
        if pending_appeals:
            reasons.append(f'{pending_appeals} pending appeal(s)')

        score = min(100, score)
        if score >= 70:
            level = 'high'
        elif score >= 35:
            level = 'medium'
        elif score > 0:
            level = 'low'
        else:
            level = 'clear'

        return UserModerationRiskModel(
            user_id=user_id,
            score=score,
            level=level,
            active_bans=len(active_bans),
            total_bans=len(all_bans),
            pending_appeals=pending_appeals,
            rejected_appeals=rejected_appeals,
            recent_events=recent_events,
            reasons=reasons,
        )

    async def delete_user_bans(self, user_id: str, db: Optional[AsyncSession] = None) -> bool:
        async with get_async_db_context(db) as session:
            await session.execute(delete(UserModerationBan).where(UserModerationBan.user_id == user_id))
            await session.commit()
            return True


UserModerationBans = UserModerationBanTable()
