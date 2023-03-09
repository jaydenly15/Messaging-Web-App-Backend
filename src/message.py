import pytest
from src.channel import channel_join_v1
from src.error import InputError
from src.error import AccessError
from src.data_store import data_store
from src.auth import auth_register_v1
from src.token import generate_token, get_user_from_token
from datetime import date, datetime, timedelta
import threading
from src.notification import add_tag_notif, add_react_notif
from src.other import get_user_info
from typing import Dict, Union
from src.user import update_num_message_count

#****************************************FUNCTIONS FOR MESSAGE/SEND/V1******************************************
def channel_message_send_validator(function):
    """Wrapper function to validate message_send parameters. 
    """
    def wrapper(token, channel_id, message, *args, **kwargs):
        store = data_store.get()
        user_id = get_user_from_token(token)['u_id']

        # check that length of message is less than 1 or over 1000 characters
        if len(message) < 1 or len(message) > 1000:
            raise InputError(description="Length of message must be between 1 and 1000 characters")

        # check that authorised_user is a part of the channel
        channel_found = False
        for channel in store['channels']:
            if channel_id == channel['id']:
                # check that user is in list of users in channel
                if user_id not in channel['users']:
                    raise AccessError(description="User is not a member of the channel")
                channel_found = True
                break

        if not channel_found:
            raise InputError(description="Channel ID does not exist.")

        return function(user_id, channel_id, message, kwargs.get('delay_to', datetime.now().timestamp()))
    return wrapper


def append_channel_message_to_db(channel_id: int, new_message: str) -> None:
    store = data_store.get()

    for channel in store['channels']:
        if channel_id == channel['id']:
            channel['messages'].append(new_message)

    add_tag_notif(new_message, channel_info=channel)
    data_store.set(store)
    update_num_message_count(new_message['u_id'])

@channel_message_send_validator
def message_send_v1(user_id: int, channel_id: int, message: str, delay_to=None) -> Dict[str, int]:
    store = data_store.get()
    store['message_num'] += 1
    
    new_message = {
        'message': message,
        'message_id': store['message_num'],
        'u_id': user_id,
        'time_created': delay_to,
        'reacts': [{
            "react_id": 1,
            "u_ids": [],
            "is_this_user_reacted": False
        }],
        'is_pinned': False
    }
    
    wait_duration = delay_to - datetime.now().timestamp()

    if wait_duration < 0:
        wait_duration = 0

    t = threading.Timer(wait_duration, append_channel_message_to_db, \
    args=(channel_id, new_message))
    t.start()
    
    data_store.set(store)
    update_num_message_count(user_id)
    return {'message_id': store['message_num']}

#****************************************FUNCTIONS FOR MESSAGE/EDIT/V1******************************************


def message_edit_v1(token: str, message_id: int, message: str) -> None:
    """Given a message, update its text with new text.
       If the new message is an empty string, the message is deleted.

    Args:
        token (str): The token of the user who wants to edit the message
        message_id (int): The messageid of the message being edited
        message (str): The message that it is being changed to 

    Raises:
        InputError: Message_id does not refer to a valid message within a 
                    channel/dm that the authorised user has joined
        AccessError: Message_id is valid but either:
                        - The message was not sent by the authorised user
                        - The authorised user does not have owner permissions
                          in the channel/dm
        InputError: Length of the message is over 1000 characters

    Returns:
        {}
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    # check if user is a global owner
    is_global = False
    for users in store['users']:
        if user_id == users['u_id']:
            is_global = users['is_global_owner']

    u_id = user_id
    valid = False
    in_channel = False
    message_pointer = None
    channel_pointer = None
    dm_pointer = None
    # iterate through all channels
    for channels in store['channels']:
        for messages in channels['messages']:
            # if message is matched
            if message_id == messages['message_id']:
                u_id = messages['u_id']
                if is_global:
                    valid = True
                elif user_id in channels['owner']:
                    valid = True
                if user_id in channels['users']:
                    in_channel = True
                if in_channel == True and user_id == messages['u_id']:
                    valid = True
                message_pointer = messages
                channel_pointer = channels  

    for dms in store['dms']:
        for messages in dms['messages']:
            # if message is matched
            if message_id == messages['message_id']:
                u_id = messages['u_id']
                if user_id == dms['owner']:
                    valid = True
                if user_id in dms['members']:
                    in_channel = True
                if in_channel == True and user_id == messages['u_id']:
                    valid = True
                message_pointer = messages
                dm_pointer = dms

    if u_id != user_id and not valid and in_channel:
        raise AccessError(description="This user doesn't have the required permissions to edit this message")
    if not valid:
        raise InputError(description="Message_id does not refer to a valid message within a channel/DM that the user has joined")                
    if len(message) > 1000:
        raise InputError(description="Length of message is over 1000 messages")
    # remove message if edited message is empty
    if message == "":
        channel_pointer['messages'].remove(message_pointer)
    else:
        message_pointer['message'] = message
        add_tag_notif(message_pointer, channel_info=channel_pointer, dm_info=dm_pointer)
    data_store.set(store)
    return {}

#****************************************FUNCTIONS FOR MESSAGE/REMOVE/V1******************************************

def message_remove_v1(token: str, message_id: int) -> None:
    """Given a message_id for a message, this message is removed from the channel/DM

    Args:
        token (str): The user that wants to remove a message
        message_id (int): The messageid that is being removed

    Raises:
        InputError: Messageid does not refer to a valid message within the channel/dm
                    that the authorised user has joined
        AccessError: When the messageid is valid but either:
                        - the message was not sent by the authorised user
                        - the authorised user does not have owner permissions in the channel/dm

    Returns:
        {}
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    # check if user is a global owner
    is_global = False
    for users in store['users']:
        if user_id == users['u_id']:
            is_global = users['is_global_owner']

    u_id = user_id
    valid = False
    in_channel = False
    message_pointer = None
    channel_pointer = None
    # iterate through all channels
    for channels in store['channels']:
        for messages in channels['messages']:
            # if message is matched
            if message_id == messages['message_id']:
                u_id = messages['u_id']
                if is_global:
                    valid = True
                elif user_id in channels['owner']:
                    valid = True
                if user_id in channels['users']:
                    in_channel = True
                if in_channel == True and user_id == messages['u_id']:
                    valid = True
                message_pointer = messages
                channel_pointer = channels

    for dms in store['dms']:
        for messages in dms['messages']:
            # if message is matched
            if message_id == messages['message_id']:
                u_id = messages['u_id']
                if user_id == dms['owner']:
                    valid = True
                if user_id in dms['members']:
                    in_channel = True
                if in_channel == True and user_id == messages['u_id']:
                    valid = True
                message_pointer = messages
                channel_pointer = dms
    if u_id != user_id and not valid and in_channel:
        raise AccessError(description="This user doesn't have the required permissions to edit this message")
    if not valid:
        raise InputError(description="Message_id does not refer to a valid message within a channel/DM that the user has joined")                
  
    # remove message
    channel_pointer['messages'].remove(message_pointer)
    data_store.set(store)
    update_num_message_count(u_id)
    return {}

#****************************************FUNCTIONS FOR MESSAGE/SENDDM/V1******************************************
def message_senddm_v1(token: str, dm_id: int, message: str) -> Dict[str, int]:
    """ Send a message from authorised_user to the DM specified by dm_id.
        Note: Each message should have it's own unique ID, i.e. no messages
        should share an ID with another message, even if that other message
        is in a different channel or DM.
    Args:
        token (str): The token of the user sending the dm
        dm_id (int): The dmid of the dm that the message is being sent in 
        message (str): The message being sent

    Raises:
        InputError: Length of message is less than 1 or over 1000 characters
        InputError: dmid does not refer to a valid dm
        AccessError: dm_id is valid and the authorised user is not a member of the dm

    Returns:
        message_id: The id of the message
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    dm_ids = [dms['dm_id'] for dms in store['dms']]

    # check that dm_id is valid
    if dm_id not in dm_ids:
        raise InputError(description="DM ID does not exist.")

    # check that length of message is less than 1 or over 1000 characters
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Length of message must be between 1 and 1000 characters")

    # check that authorised_user is a part of the dm
    for dms in store['dms']:
        if dm_id == dms['dm_id']:
            # check that user is in list of users in dm
            if user_id not in dms['members']:
                raise AccessError(description="User is not a member of the dm")
            # run if user is in list of users in the channel
            else:
                # increment number of messages
                store['message_num'] += 1
                current_time = datetime.now()
                time = int(current_time.timestamp())
                new_message = {
                    "message": message,
                    "message_id": store['message_num'],
                    'u_id': user_id,
                    'time_created': time,
                    'reacts': [{
                        "react_id": 1,
                        "u_ids": [],
                        "is_this_user_reacted": False
                    }],
                    'is_pinned': False
                }
                # append new message
                dms['messages'].append(new_message)
                add_tag_notif(new_message, dm_info=dms)
    data_store.set(store)
    update_num_message_count(user_id)
    return {
        'message_id': store['message_num']
    }

#****************************************FUNCTIONS FOR MESSAGE/SHARE/V1******************************************
def message_share_v1(token: str, og_message_id: int, message: str, channel_id: int, dm_id: int) -> Dict[str, Union[None, int]]:
    """

    Args:
        token (str): The token of the user sharing the message
        og_message_id (int): ID of the original message
        message (str): Optional message in addition to the shared message
        channel_id (int): The channel the message is being shared to
        dm_id (int): The dm that the message is being shared to

    Raises:
        InputError: Both channel id and dm id are invalid
        InputError: Neither channel id nor dm id are -1
        InputError: Og message id does not refer to a valid message within a 
                    channel/dm that the authorised user has joined
        InputError: Length of the message is more than 1000 characters
        AccessError: The pair of channel id and dm id are valid and the authorised user 
                     has not joined the channel or dm they are trying to share the message to

    Returns:
    Dict:   {
            'shared_message_id': ID of the shared message
            }
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    found_channel_id = False
    found_dm_id = False
    in_channel = False
    found_og_message = False
    og_message_recorder = None
    # iterate through all channels
    for channels in store['channels']:
        # iterate through all messages
        for messages in channels['messages']:
            # if we find the message that we want to share
            if og_message_id == messages['message_id']:
                found_og_message = True
                og_message_recorder = messages['message']
        if channels['id'] == channel_id:
            found_channel_id = True
            # check that user is in the channel
            if user_id in channels['users']:
                in_channel = True

    # iterate through all dms
    for dms in store['dms']:
        # iterate through all messages
        for dm_msg in dms['messages']:
            # if we find the message that we want to share
            if og_message_id == dm_msg['message_id']:
                found_og_message = True
                og_message_recorder = dm_msg['message']
        if dms['dm_id'] == dm_id:
            found_dm_id = True
            # check that user is in the dm      
            if user_id in dms['members']:
                in_channel = True


    # if both channel_id and dm_id is invalid
    if not found_channel_id and not found_dm_id:
        raise InputError(description="Both channel_id and dm_id are invalid.")

    # if neither channel_id nor dm_id is -1
    if channel_id != -1 and dm_id != -1:
        raise InputError(description="Neither channel_id nor dm_id are -1.")

    # if og_message_id does not refer to a valid message in the channel/DM that the user has joined
    if not found_og_message:
        raise InputError(description="og_message_id does not refer to a valid message in the channel/DM that the user has joined.")

    # length of message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description="Length of message must be less than or equal to 1000 characters.")

    # if channel_id and dm_id are valid but the user has not joined the channel/dm they are trying to share the message to
    if not in_channel:
        raise AccessError(description="channel_id and dm_id are valid but the user has not joined the channel/DM they are trying to share the message to.")


    # share message
    shared_message = f"'{og_message_recorder}' - {message}"
    shared_message_id = None
    if found_channel_id:
        shared_message_id = message_send_v1(token, channel_id, shared_message)['message_id']
    if found_dm_id: 
        shared_message_id = message_senddm_v1(token, dm_id, shared_message)['message_id']

    data_store.set(store)
    update_num_message_count(user_id)
    return {'shared_message_id': shared_message_id}

#****************************************FUNCTIONS FOR MESSAGE/REACT/V1******************************************
def message_react_v1(token: str, message_id: int, react_id: int) -> None:
    """Given a message within a channel or DM the authorised user is part of,
        add a "react" to that particular message.

    Args:
        token (str): The token of the user reacting to the message
        message_id (int): The id of the message
        react_id (int)): The id of the reaction

    Raises:
        InputError: Message id is not a valid message within a channel or DM that the authorised
                    user has joined 
        InputError: React id is not a valid react ID
        InputError: The message already contains a react with ID react id from the authorised user
    Returns:
        {}
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    valid_message_id = False
    message_pointer = None
    channel_pointer = None
    dm_pointer = None
     # iterate through all channels
    for channels in store['channels']:
        # iterate through all messages
        for messages in channels['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the channel
                if user_id in channels['users']:
                    valid_message_id = True
                    # check if user is in the list of reacted users
                    if user_id in messages['reacts'][0]['u_ids']: 
                        # the message already contains a react with ID react_id from the authorised user
                        raise InputError(description="This message already contains a react with ID react_id from the authorised user.")
                    message_pointer = messages
                    channel_pointer = channels

    # iterate through all dms
    for dms in store['dms']:
        # iterate through all messages
        for messages in dms['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the dm
                if user_id in dms['members']:
                    valid_message_id = True
                    # check if user is in the list of reacted users
                    if user_id in messages['reacts'][0]['u_ids']: 
                        # the message already contains a react with ID react_id from the authorised user
                        raise InputError(description="This message already contains a react with ID react_id from the authorised user.")
                    message_pointer = messages
                    dm_pointer = dms

    # message_id is not a valid message within a channel or DM that the authorised user has joined
    if not valid_message_id:
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined.")
    # react_id is not a valid react ID (currently the only valid react ID is 1)    
    if react_id != 1:
        raise InputError(description="react_id is not a valid react ID. Currently, the only valid react ID is 1.")

    # add react to the message - 'reacts': [{'react_id': "", 'u_ids': [], 'is_this_user_reacted': True}]
    message_pointer['reacts'][0]['u_ids'].append(user_id)
    message_pointer['reacts'][0]['is_this_user_reacted'] = True
    add_react_notif(user_id,message_pointer, channel_info=channel_pointer, dm_info=dm_pointer) 
    data_store.set(store)
    return {}

#****************************************FUNCTIONS FOR MESSAGE/UNREACT/V1****************************************
def message_unreact_v1(token: str, message_id: int, react_id: int) -> None:
    """Given a message within a channel or DM the authorised user is part of,
       remove a "react" to that particular message.

    Args:
        token (str): The token of the user unreacting 
        message_id (int): The id of the message
        react_id (int): The id of the reaction

    Raises:
        InputError: Message id is not a valid message within a channel or dm that
                    the authorised user has joined
        InputError: React id is not a valid react id
        InputError: The message does not contain a react with ID react id from the 
                    authorised user

    Returns:
        {}
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    valid_message_id = False
    message_pointer = None
     # iterate through all channels
    for channels in store['channels']:
        # iterate through all messages
        for messages in channels['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the channel
                if user_id in channels['users']:
                    valid_message_id = True
                    # if the message already does not contain a react with ID react_id from the authorised user
                    if user_id not in messages['reacts'][0]['u_ids']:
                        raise InputError(description="This message does not contain a react with ID react_id from the authorised user.")
                    message_pointer = messages
 
    # iterate through all dms
    for dms in store['dms']:
        # iterate through all messages
        for messages in dms['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the dm
                if user_id in dms['members']:
                    valid_message_id = True
                    # if the message already does not contain a react with ID react_id from the authorised user
                    if user_id not in messages['reacts'][0]['u_ids']:
                        raise InputError(description="This message does not contain a react with ID react_id from the authorised user.")
                    message_pointer = messages

    # message_id is not a valid message within a channel or DM that the authorised user has joined
    if not valid_message_id:
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined.")
    # react_id is not a valid react ID (currently the only valid react ID is 1)    
    if react_id != 1:
        raise InputError(description="react_id is not a valid react ID. Currently, the only valid react ID is 1.")

    # remove user's react to the message
    message_pointer['reacts'][0]['u_ids'].remove(user_id)
    message_pointer['reacts'][0]['is_this_user_reacted'] = False
    data_store.set(store)
    return {}

#****************************************FUNCTIONS FOR MESSAGE/PIN/V1********************************************
def message_pin_v1(token: str, message_id: int) -> None:
    """Given a message within a channel or DM, mark it as "pinned".

    Args:
        token (str): The token of the user trying to pin the message
        message_id (int): The id of the message

    Raises:
        InputError: Message id is not a valid message within a channel or dm that 
                    the authorised user has joined
        InputError: The message is already pinned
        AccessError: Message id refers to a valid message in a joined channel/dm
                     and the authorised user does not have permissions in the channel/dm

    Returns:
        {}
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    is_global = False
    for users in store['users']:
        if user_id == users['u_id']:
            is_global = users['is_global_owner']

    valid_message_id = False
    has_permissions = False
    message_pointer = None
     # iterate through all channels
    for channels in store['channels']:
        # iterate through all messages
        for messages in channels['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the channel that the message is sent in
                if user_id in channels['users']:
                    valid_message_id = True
                    message_pointer = messages
                # if user is a global user
                if is_global:
                    has_permissions = True
                # if user is an owner
                elif user_id in channels['owner']:
                    has_permissions = True
                # the message is already pinned
                if messages['is_pinned']:
                    raise InputError(description="The message is already pinned.")

    # iterate through all dms
    for dms in store['dms']:
        # iterate through all messages
        for messages in dms['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the dm
                if user_id in dms['members']:
                    valid_message_id = True
                    message_pointer = messages
                # if user is an owner
                if user_id == dms['owner']:
                    has_permissions = True
                # the message is already pinned
                if messages['is_pinned']:
                    raise InputError(description="The message is already pinned.")

    # message_id refers to a valid message in a joined channel/DM but the user does not have owner permissions in the channel/DM
    if valid_message_id and not has_permissions:
        raise AccessError(description="message_id refers to a valid message in a joined channel/DM but the authorised user does not have owner permissions in the channel/DM.")

    # message_id is not a valid message within a channel or DM that the authorised user has joined
    if not valid_message_id:
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined.")

    # pin message
    message_pointer['is_pinned'] = True
    data_store.set(store)

    return {}

#****************************************FUNCTIONS FOR MESSAGE/UNPIN/V1******************************************
def message_unpin_v1(token: str, message_id: int) -> None:
    """Given a message within a channel or DM, remove its mark as pinned.

    Args:
        token (str): The token of the user unpinning the message
        message_id (int): The id of the message

    Raises:
        InputError: Message id is not a valid message within a channel or dm that 
                    the authorised user has joined
        InputError: The message is not already pinned
        AccessError: Message id refers to a valid message in a joined channel/dm
                     and the authorised user does not have permissions in the channel/dm

    Returns:
        {}
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    is_global = False
    for users in store['users']:
        if user_id == users['u_id']:
            is_global = users['is_global_owner']

    valid_message_id = False
    has_permissions = False
    message_pointer = None
     # iterate through all channels
    for channels in store['channels']:
        # iterate through all messages
        for messages in channels['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the channel that the message is sent in
                if user_id in channels['users']:
                    valid_message_id = True
                    message_pointer = messages
                # if user is a global user
                if is_global:
                    has_permissions = True
                # if user is an owner
                elif user_id in channels['owner']:
                    has_permissions = True
                # the message is already unpinned
                if not messages['is_pinned']:
                    raise InputError(description="The message is already unpinned.")

    # iterate through all dms
    for dms in store['dms']:
        # iterate through all messages
        for messages in dms['messages']:
            # if we find the message that we want to share
            if message_id == messages['message_id']:
                # check that user is in the dm
                if user_id in dms['members']:
                    valid_message_id = True
                    message_pointer = messages
                # if user is an owner
                if user_id == dms['owner']:
                    has_permissions = True
                # the message is already unpinned
                if not messages['is_pinned']:
                    raise InputError(description="The message is already unpinned.")

    # message_id refers to a valid message in a joined channel/DM but the user does not have owner permissions in the channel/DM
    if valid_message_id and not has_permissions:
        raise AccessError(description="message_id refers to a valid message in a joined channel/DM but the authorised user does not have owner permissions in the channel/DM.")

    # message_id is not a valid message within a channel or DM that the authorised user has joined
    if not valid_message_id:
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined.")

    # unpin message
    message_pointer['is_pinned'] = False
    data_store.set(store)

    return {}

