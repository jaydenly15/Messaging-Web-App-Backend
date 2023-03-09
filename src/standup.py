from typing import List
from src.data_store import data_store
from src.token import get_user_from_token
from src.error import InputError
from src.error import AccessError
from src.message import message_send_v1
from src.user import update_num_message_count
import datetime
import threading
from json import dump
from typing import List, Union

queue = [

]
def save(store):
    with open('src/data_store.json', 'w') as file:
        dump(store, file)
    pass

def write_buffer(token: str, channel_id: int) -> None:
    #after lenght seconds add all the words to a string then return
    global queue
    store = data_store.get()
    for channels in store['channels']:
        if channel_id == channels['id']:
            channels['standup']['active'] = False
    message = '\n'.join(queue)
    if len(queue) != 0:
        message_send_v1(token, channel_id, message)
    save(store)
    queue = []
    pass

def standup_start_v1(token: str, channel_id: int, length: int) -> float:
    """
    Starts a standup using an authorised user in a valid channel with how long they want it to be.
    The users of the channel can post messages in the standup using standup/send/v1 and all messages
    will be posted grouped together by the user who initialised it.

    Args:
        token (string): the token of a user
        channel_id (integer): the channel id
        length (integer): the length of seconds

    Raises:
        InputError: raised when channel_id does not refer to a valid
        InputError: raised when length is a negative integer
        InputError: raised when an active standup is currently running in the channel
        AccessError: raised when the given auth_user_id is not a valid id in the channel

    Returns:
        (float):     
        time_finish (when the standup ends)
    """
    if length < 0:
        raise InputError("Invalid length")

    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']
        
    for channels in store['channels']:
        if channel_id == channels['id']:
            for users in channels['users']:
                if user_id == users:
                    break
            else:
                raise AccessError("User not in channel")
            if channels['standup']['active'] == True:
                raise InputError("Standup already running")
            write_buffer(token, channel_id)
            channels['standup']['active'] = True
            time_finish = datetime.datetime.now().timestamp() + length
            channels['standup']['time_finish'] = time_finish
            break
    else: 
        raise InputError("Channel ID does not exist.")

    message = threading.Timer(length, write_buffer, args=(token, channel_id))
    message.start()

    return time_finish

def standup_active_v1(token: str, channel_id: int) -> List[Union[bool, float]]:
    """
    If there is an active standup calling standup/active/v1 will return whether the standup is active or not
    and if so when the standup finishes

    Args:
        token (string): the token of a user
        channel_id (integer): the channel id

    Raises:
        InputError: raised when channel_id does not refer to a valid
        AccessError: raised when the given auth_user_id is not a valid id in the channel

    Returns:
        (list):     
        [is_active, time_finish]
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    for channels in store['channels']:
        if channels['id'] == channel_id:
            for users in channels['users']:
                if user_id == users:
                    break
            else:
                raise AccessError("User not in channel")
            is_active = channels['standup']['active']
            if is_active == True:
                time_finish = channels['standup']['time_finish']
            else:
                time_finish = None
            break
    else:
        raise InputError("Channel ID does not exist.")

    return [is_active, time_finish]

def standup_send_v1(token: str, channel_id: int, message: str) -> None:
    """
    Using standup/send/v1 when there is an active standup will append the message into the message queue and
    once the standup is over all messages in said queue will be messaged to the channel messages by the standup
    creator.

    Args:
        token (string): the token of a user
        channel_id (integer): the channel id
        message (string): the message string

    Raises:
        InputError: raised when channel_id does not refer to a valid
        InputError: raised when length of message is over 1000 characters
        InputError: raised when an active standup is not currently running
        AccessError: raised when the given auth_user_id is not a valid id in the channel

    Returns:
        {}
    """
    global queue
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    for channels in store['channels']:
        if channel_id == channels['id']:
            for user in channels['users']:
                if user_id == user:
                    for users in store['users']:
                        if user_id == users['u_id']:
                            user_name = users['handle_str']
                    break
                else:
                    raise AccessError("User not in channel")
            if channels['standup']['active'] == False:
                raise InputError("No active standup")
            else:
                if len(message) > 1000:
                    raise InputError("Length of message is over 1000")
                standup_message = user_name + ": " + message
                queue.append(standup_message)
            break
    else:
        raise InputError("Channel ID does not exist.")

    update_num_message_count(user_id)
    return {}
