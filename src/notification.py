from hashlib import new
from src.token import get_user_from_token
from src.data_store import data_store
from src.other import get_handle_from_id, get_user_info

import re
from typing import Dict, Union, List, Optional

def search_tags(handle_str: str, message: str) -> bool:
    """
    Args:
        handle_str (string)
        message (string)

    Returns:
        bool: True if user with handle, 'handle_str' is tagged in message
        False otherwise.
    """
    var = re.compile(rf'(@{handle_str}(\W|\Z))')
    mo = var.search(message)

    try:
        var = mo.group()
        return True
    except:
        return False

def search_tags_in_message(members: List[int], message: str) -> List[int]:
    """Searches for members who are tagged in a message

    Args:
        members (list): List of members' user IDs
        message (string)

    Returns:
        members_tagged_u_ids: List of IDs of tagged members
    """
    members_by_handle_str = list(map(get_handle_from_id, members))
    members_tagged_handles = list(filter(lambda x: search_tags(x, message), members_by_handle_str))
    members_tagged_u_ids = list(map(lambda x: get_user_info(x)['u_id'], members_tagged_handles))

    return members_tagged_u_ids

def add_notification(notif_message, user_id, channel_id=-1, dm_id=-1):
    """Appends a notification to the database.

    Args:
        notif_message (string)
        user_id (integer): ID of person who receives the notification
        channel_id (int, optional): Channel ID, if message is sent to a channel. Defaults to -1.
        dm_id (int, optional): DM ID, if message is sent to a DM. Defaults to -1.
    """
    store = data_store.get()
    new_notification = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': notif_message
    }
    for user in store['users']:
        if user_id == user['u_id']:
            user['notifications'].append(new_notification)
    data_store.set(store)


def add_tag_notif(new_message, channel_info=None, dm_info=None):
    """Finds users tagged in a message and notifies them.

    Args:
        new_message (string)
        channel_info ([type], optional): Channel ID, if message is sent to a channel. Defaults to -1.
        dm_info ([type], optional): DM ID, if message is sent to a DM. Defaults to -1.
    """

    if dm_info is not None:
        name = dm_info['name'] 
        members = dm_info['members']
    else:
        name = channel_info['name']
        members = channel_info['users']

    members_tagged = search_tags_in_message(members, new_message['message'])
    message_owner_handle = get_user_info(new_message['u_id'])['handle_str']
    
    for member_id in members_tagged:
        notif_message = f"{message_owner_handle} tagged you in {name}: {new_message['message'][:20]}"
        if dm_info is not None:
            add_notification(notif_message, member_id, dm_id=dm_info['dm_id'])
        else:
            add_notification(notif_message, member_id, channel_id=channel_info['id'])

def add_react_notif(user_id, new_message, channel_info=None, dm_info=None):
    """Appends a notification to list of user's notification when a message is reacted to.

    Args:
        new_message (string)
        channel_info ([type], optional): Channel ID, if message is sent to a channel. Defaults to -1.
        dm_info ([type], optional): DM ID, if message is sent to a DM. Defaults to -1.
    """
    name = dm_info['name'] if dm_info is not None else channel_info['name']

    user_reacted_handle = get_user_info(user_id)['handle_str']
    notif_message = f"{user_reacted_handle} reacted to your message in {name}"

    if dm_info is not None:
        add_notification(notif_message, new_message['u_id'], dm_id=dm_info['dm_id'])
    else:
        add_notification(notif_message, new_message['u_id'], channel_id=channel_info['id'])

def add_invite_notif(inviter_id, u_id, channel_info=None, dm_info=None):
    """Appends a notification to list of user's notification when a message is reacted to.

    Args:
        new_message (string)
        channel_info ([type], optional): Channel ID, if message is sent to a channel. Defaults to -1.
        dm_info ([type], optional): DM ID, if message is sent to a DM. Defaults to -1.
    """

    name = dm_info['name'] if dm_info is not None else channel_info['name']

    inviter_handle = get_user_info(inviter_id)['handle_str']

    notif_message = f"{inviter_handle} added you to {name}"

    if dm_info is not None:
        add_notification(notif_message, u_id, dm_id=dm_info['dm_id'])
    else:
        add_notification(notif_message, u_id, channel_id=channel_info['id'])

def notifications_get_v1(token: str) -> Dict[str, List[Dict[str, Union[int, str]]]]:
    """Return the user's most recent 20 notifications, ordered from most recent to least recent.

    Args:
        token (string): User whose notifications is to be listed

    Returns:
        notifications: List of dictionaries of type notifications
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    for user in store['users']:
        if user_id == user['u_id']:
            latest_notifications = user['notifications'][-20:]

    return {'notifications': latest_notifications}