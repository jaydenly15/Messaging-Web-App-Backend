import pytest
from src.channel import channel_join_v1
from src.error import InputError
from src.error import AccessError
from src.data_store import data_store
from src.token import get_user_from_token
from src.auth import auth_register_v1
from typing import Dict, Union
from src.user import update_num_channels
from src.other import save

def channels_list_v1(auth_user_id: int) -> Dict[str, Union[int, str]]:
    """ Provides a list of all channels (and their associated details) that the authorised user is a part of.

    Args:
        auth_user_id (integer): the id of a user
        
    Raises:
        AccessError: raised when the given auth_user_id is not a valid id

    Returns:
        (dictionary):     
        {
            'channels' (a list of dictionaries): [
                {
                    'channel_id': Channel id,
                    'name': Channel name
                }
            ]
        }
    """
    store = data_store.get()
    
    channel_list = []
    # Iterate through all channels stored in channels list
    for channels in store['channels']:
        # Checks if user is a member of channels
        if auth_user_id in channels['users']:
            channel_details = {
                'channel_id': channels['id'],
                'name': channels['name']
            }
            channel_list.append(channel_details)    
    return {
        'channels': channel_list
    }

def channels_listall_v1(auth_user_id: int) -> Dict[str, Union[int, str]]:
    """Provides a list of all channels, including private channels, (and their associated details).

    Args:
        auth_user_id (integer): the id of a user
        
    Raises:
        AccessError: raised when the given auth_user_id is not a valid id

    Returns:
        (dictionary):     
        {
            'channels' (a list of dictionaries): [
                {
                    'channel_id': Channel id,
                    'name': Channel name
                }
            ]
        }
    """
    store = data_store.get()

    channel_list = []
    # iterate through all channels stored in channels list
    for channels in store['channels']:
        channel_details = {
            'channel_id': channels['id'],
            'name': channels['name']
         }
        channel_list.append(channel_details)

    return {
        'channels': channel_list
    }

def channels_create_v1(auth_user_id: int, name: str, is_public: bool) -> Dict[str, int]:
    """Creates a new channel with the given name that is either a public or private channel. 
    The user who created it automatically joins the channel. 
    For this iteration, the only channel owner is the user who created the channel.

    Args:
        auth_user_id (integer): the id of a user
        name (string): the name of the channel being created
        is_public (bool): True if the new channel is a public channel, False otherwise

    Raises:
        InputError: raised when length of name is less than 1 or larger than 20
        AccessError: raised when the given auth_user_id is not a valid id

    Returns:
        (dictionary):     
        {
            'channel_id': The ID of the created channel
        }
    """

    store = data_store.get()

    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Length of name must be be between 1 and 20 characters.")
    
    # id of the newly created channel is one more than the current amount of channels
    id = len(store['channels']) + 1

    new_channel = {
        'id': id,
        'owner': [auth_user_id],
        'name': name,
        'users': [auth_user_id],
        'messages': [],
        'public': is_public,
        'standup': {'active': False,
                    'time_finish': 0,
        }
    }
    
    store['channels'].append(new_channel)
    data_store.set(store)
    print("Adding for person with", auth_user_id)
    update_num_channels(auth_user_id)
    save()

    return {
        'channel_id': id
    }