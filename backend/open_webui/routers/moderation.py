from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from open_webui.constants import ERROR_MESSAGES
from open_webui.internal.db import get_async_session
from open_webui.models.moderation import (
    UserModerationBanForm,
    UserModerationBanModel,
    UserModerationBans,
    get_moderation_ban_message,
)
from open_webui.models.users import Users
from open_webui.utils.auth import get_admin_user, get_verified_user


router = APIRouter()


class ModerationBanCreateForm(UserModerationBanForm):
    pass


class ModerationBanListResponse(BaseModel):
    items: list[UserModerationBanModel]


class ActiveModerationBanResponse(UserModerationBanModel):
    message: str


class ActiveModerationBanListResponse(BaseModel):
    items: list[ActiveModerationBanResponse]


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
        return await UserModerationBans.insert_new_ban(form_data, created_by=user.id, db=db)
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
