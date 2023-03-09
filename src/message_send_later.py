import threading

from hypothesis.strategies._internal.core import data
from src.data_store import data_store
from src.token import get_user_from_token, get_ids_from_token
from threading import Timer
from datetime import datetime, timedelta
from src.message import message_send_v1
from src.error import AccessError, InputError
from src.message import message_send_v1
from src.notification import add_tag_notif
from src.other import save
from typing import Dict
from src.user import update_num_message_count

def message_send_later_v1(token: str, channel_id: int, message: str, time_sent: int) -> Dict[str, int]:
    """Send a message from the authorised user to the channel specified by channel_id 
       automatically at a specified time in the future.

    Args:
        token (str): The token of the user sending the message
        channel_id (int): The id of the channel
        message (str): The message being sent
        time_sent (int)): The time it is going to be sent

    Raises:
        InputError: The time sent is a time in the past

    Returns:
    Dict:   {
            'message_id': The id of the message
            }
    """
    wait_duration = time_sent - datetime.now().timestamp()
    if wait_duration < 0:
        raise InputError(description='Time sent is a time in the past')

    message_id = message_send_v1(token, channel_id, message, \
                                delay_to=time_sent)['message_id']
    u_id = get_user_from_token(token)['u_id']
    update_num_message_count(u_id)
    return {'message_id': message_id}

def append_dm_message_to_db(dm_id: int, new_message: str) -> None:
    """Appends the dm to the database

    Args:
        dm_id (int): The id of the dm
        new_message (str): The message being sent
    """
    store = data_store.get()

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            dm['messages'].append(new_message)
            break
    
    add_tag_notif(new_message, dm_info=dm)
    save()
    data_store.set(store)
    update_num_message_count(new_message['u_id'])

def message_send_later_dm_v1(token: str, dm_id: int, message: str, time_sent: int) -> Dict[str, int]:
    """Send a message from the authorised user to the DM specified by dm_id 
       automatically at a specified time in the future.

    Args:
        token (str): The token of the user sending the dm
        dm_id (int): The id of the dm
        message (str): The message being sent
        time_sent (int): The time it is going to be sent

    Raises:
        AccessError: Dm id is valid and the authorised user is not a member of the 
                     dm they are trying to post to
        InputError: Dm id does not refer to a valid dm
        InputError: The length of the message is over 1000 characters
        InputError: Time sent is a time in the past

    Returns:
    Dict:   {
            'message_id': The id of the message
            }
        
    """
    store = data_store.get()

    u_id = get_user_from_token(token)['u_id']

    dm_found = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            dm_found = True
            break

    if u_id not in dm['members']:
        raise AccessError(description="User is not a member of the dm")

    if not dm_found:
        raise InputError(description='Invalid dm_id')

    wait_duration = time_sent - datetime.now().timestamp()
    if wait_duration < 0:
        raise InputError(description='Time sent is a time in the past')
    
    if len(message) > 1000:
        raise InputError(description="Length of message must be between 1 and 1000 characters")
    
    store['message_num'] += 1
    
    new_message = {
        'message': message,
        'message_id': store['message_num'],
        'u_id': u_id,
        'time_created': time_sent,
        'reacts': [{
            "react_id": 1,
            "u_ids": [],
            "is_this_user_reacted": False
        }],
        'is_pinned': False
    }

    t = threading.Timer(wait_duration, append_dm_message_to_db, \
    args=(dm_id, new_message))
    t.start()

    data_store.set(store)
    update_num_message_count(u_id)
    return {'message_id': store['message_num']}