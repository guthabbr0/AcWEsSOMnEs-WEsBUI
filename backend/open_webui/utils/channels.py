import re
from typing import Optional

from open_webui.models.access_grants import (
    AccessGrants,
    has_public_write_access_grant,
    normalize_access_grants,
)
from open_webui.models.channels import ChannelModel
from sqlalchemy.ext.asyncio import AsyncSession


async def channel_has_access(
    user_id: str,
    channel: ChannelModel,
    permission: str = 'read',
    strict: bool = True,
    db: Optional[AsyncSession] = None,
) -> bool:
    if await AccessGrants.has_access(
        user_id=user_id,
        resource_type='channel',
        resource_id=channel.id,
        permission=permission,
        db=db,
    ):
        return True

    if not strict and permission == 'write' and has_public_write_access_grant(channel.access_grants):
        return True

    return False


def channel_has_explicit_write_policy(channel: ChannelModel) -> bool:
    return any(grant.get('permission') == 'write' for grant in normalize_access_grants(channel.access_grants))


async def channel_has_write_access(
    user_id: str,
    channel: ChannelModel,
    db: Optional[AsyncSession] = None,
) -> bool:
    if await channel_has_access(user_id, channel, permission='write', strict=False, db=db):
        return True

    # Awesome WebUI compatibility: public/readable standard channels are chatty by
    # default unless the channel owner added an explicit write policy.
    if not channel_has_explicit_write_policy(channel):
        return await channel_has_access(user_id, channel, permission='read', db=db)

    return False


def extract_mentions(message: str, triggerChar: str = '@'):
    # Escape triggerChar in case it's a regex special character
    triggerChar = re.escape(triggerChar)
    pattern = rf'<{triggerChar}([A-Z]):([^|>]+)'

    matches = re.findall(pattern, message)
    return [{'id_type': id_type, 'id': id_value} for id_type, id_value in matches]


def replace_mentions(message: str, triggerChar: str = '@', use_label: bool = True):
    """
    Replace mentions in the message with either their label (after the pipe `|`)
    or their id if no label exists.

    Example:
      "<@M:gpt-4.1|GPT-4>" -> "GPT-4"   (if use_label=True)
      "<@M:gpt-4.1|GPT-4>" -> "gpt-4.1" (if use_label=False)
    """
    # Escape triggerChar
    triggerChar = re.escape(triggerChar)

    def replacer(match):
        id_type, id_value, label = match.groups()
        return label if use_label and label else id_value

    # Regex captures: idType, id, optional label
    pattern = rf'<{triggerChar}([A-Z]):([^|>]+)(?:\|([^>]+))?>'
    return re.sub(pattern, replacer, message)
