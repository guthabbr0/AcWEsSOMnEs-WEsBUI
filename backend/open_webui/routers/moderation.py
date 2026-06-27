from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from open_webui.constants import ERROR_MESSAGES
from open_webui.internal.db import get_async_session
from open_webui.models.moderation import (
    UserModerationAppealForm,
    UserModerationAppealModel,
    UserModerationAppealResolveForm,
    UserModerationAuditLogModel,
    UserModerationBanForm,
    UserModerationBanModel,
    UserModerationBans,
    UserModerationRiskModel,
    get_moderation_ban_payload,
    get_moderation_ban_message,
)
from open_webui.models.users import Users
from open_webui.utils.auth import get_admin_user, get_verified_user


router = APIRouter()


async def emit_site_ban_update(user_id: str, event_type: str, ban: UserModerationBanModel | None = None):
    try:
        from open_webui.socket.main import emit_to_users

        await emit_to_users(
            'events',
            {
                'chat_id': None,
                'message_id': None,
                'data': {
                    'type': event_type,
                    'data': get_moderation_ban_payload(ban) if ban else None,
                },
            },
            [user_id],
        )
    except Exception:
        pass


async def emit_admin_moderation_event(event_type: str, data: dict):
    try:
        from open_webui.socket.main import emit_to_users

        admin_response = await Users.get_users(filter={'roles': ['admin']}, limit=500)
        admin_ids = [admin.id for admin in admin_response.get('users', [])]
        if not admin_ids:
            return

        await emit_to_users(
            'events',
            {
                'chat_id': None,
                'message_id': None,
                'data': {
                    'type': event_type,
                    'data': data,
                },
            },
            admin_ids,
        )
    except Exception:
        pass


class ModerationBanCreateForm(UserModerationBanForm):
    pass


class ModerationBanListResponse(BaseModel):
    items: list[UserModerationBanModel]


class ActiveModerationBanResponse(UserModerationBanModel):
    message: str


class ActiveModerationBanListResponse(BaseModel):
    items: list[ActiveModerationBanResponse]


class ModerationAppealCreateForm(UserModerationAppealForm):
    pass


class ModerationAppealResolveForm(UserModerationAppealResolveForm):
    pass


class ModerationAppealListResponse(BaseModel):
    items: list[UserModerationAppealModel]


class ModerationAuditLogListResponse(BaseModel):
    items: list[UserModerationAuditLogModel]


class ModerationRiskResponse(UserModerationRiskModel):
    pass


class ModerationCenterResponse(BaseModel):
    bans: list[UserModerationBanModel]
    appeals: list[UserModerationAppealModel]
    audit: list[UserModerationAuditLogModel]
    risks: list[UserModerationRiskModel]


class ModerationBanPublicStatusResponse(BaseModel):
    active: bool
    ban: ActiveModerationBanResponse | None = None


@router.post('/appeals', response_model=UserModerationAppealModel)
async def create_moderation_appeal(
    form_data: ModerationAppealCreateForm,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        appeal = await UserModerationBans.create_appeal(form_data, db=db)
        await emit_admin_moderation_event(
            'moderation:appeal_created',
            {
                'appeal': appeal.model_dump(),
            },
        )
        return appeal
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get('/bans/{ban_id}/status', response_model=ModerationBanPublicStatusResponse)
async def get_public_moderation_ban_status(
    ban_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    ban = await UserModerationBans.get_ban_by_id(ban_id, db=db)
    if not ban or ban.revoked_at:
        return {'active': False, 'ban': None}

    active_bans = await UserModerationBans.get_active_bans(ban.user_id, scope=ban.scope, db=db)
    active = next((item for item in active_bans if item.id == ban.id), None)
    if not active:
        return {'active': False, 'ban': None}

    return {
        'active': True,
        'ban': ActiveModerationBanResponse(
            **active.model_dump(),
            message=get_moderation_ban_message(active),
        ),
    }


@router.get('/appeals', response_model=ModerationAppealListResponse)
async def list_moderation_appeals(
    user_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    return {
        'items': await UserModerationBans.get_appeals(
            user_id=user_id,
            status=status_filter,
            db=db,
        )
    }


@router.post('/appeals/{appeal_id}/resolve', response_model=UserModerationAppealModel)
async def resolve_moderation_appeal(
    appeal_id: str,
    form_data: ModerationAppealResolveForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    appeal = await UserModerationBans.resolve_appeal(appeal_id, form_data, resolved_by=user.id, db=db)
    if not appeal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Moderation appeal not found.')
    return appeal


@router.get('/audit', response_model=ModerationAuditLogListResponse)
async def list_moderation_audit_logs(
    user_id: Optional[str] = None,
    action_prefix: Optional[str] = None,
    limit: int = 100,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    return {
        'items': await UserModerationBans.get_audit_logs(
            user_id=user_id,
            action_prefix=action_prefix,
            limit=limit,
            db=db,
        )
    }


@router.get('/risk/{user_id}', response_model=ModerationRiskResponse)
async def get_moderation_user_risk(
    user_id: str,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await UserModerationBans.get_user_risk(user_id, db=db)


@router.get('/center', response_model=ModerationCenterResponse)
async def get_moderation_center(
    limit: int = 100,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    bans = await UserModerationBans.get_bans(include_inactive=True, db=db)
    appeals = await UserModerationBans.get_appeals(status='pending', db=db)
    audit = await UserModerationBans.get_audit_logs(limit=limit, db=db)
    user_ids = []
    for ban in bans:
        if ban.user_id not in user_ids:
            user_ids.append(ban.user_id)
    for appeal in appeals:
        if appeal.user_id not in user_ids:
            user_ids.append(appeal.user_id)

    risks = [await UserModerationBans.get_user_risk(user_id, db=db) for user_id in user_ids[:50]]
    return {
        'bans': bans[: max(1, min(int(limit or 100), 500))],
        'appeals': appeals[: max(1, min(int(limit or 100), 500))],
        'audit': audit,
        'risks': risks,
    }


@router.get('/bans', response_model=ModerationBanListResponse)
async def list_moderation_bans(
    user_id: Optional[str] = None,
    include_inactive: bool = True,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    return {
        'items': await UserModerationBans.get_bans(
            user_id=user_id,
            include_inactive=include_inactive,
            db=db,
        )
    }


@router.post('/bans', response_model=UserModerationBanModel)
async def create_moderation_ban(
    form_data: ModerationBanCreateForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    target_user = await Users.get_user_by_id(form_data.user_id, db=db)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.USER_NOT_FOUND)
    if target_user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Admin users cannot be moderated.')

    try:
        ban = await UserModerationBans.insert_new_ban(form_data, created_by=user.id, db=db)
        if ban.scope == 'site' and not ban.revoked_at:
            await emit_site_ban_update(ban.user_id, 'moderation:site_ban', ban)
        return ban
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post('/bans/{ban_id}/revoke', response_model=UserModerationBanModel)
async def revoke_moderation_ban(
    ban_id: str,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    ban = await UserModerationBans.revoke_ban(ban_id, revoked_by=user.id, db=db)
    if not ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Moderation ban not found.')
    if ban.scope == 'site':
        await emit_site_ban_update(ban.user_id, 'moderation:site_unban')
    return ban


@router.get('/me/active', response_model=ActiveModerationBanListResponse)
async def get_my_active_moderation_bans(
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    bans = await UserModerationBans.get_active_bans(user.id, db=db)
    return {
        'items': [
            ActiveModerationBanResponse(
                **ban.model_dump(),
                message=get_moderation_ban_message(ban),
            )
            for ban in bans
        ]
    }
