from src.data_store import data_store
from src.other import is_valid_user_id, get_user_info
from src.token import get_user_from_token
from src.error import InputError
from src.error import AccessError
from src.notification import add_invite_notif
from src.user import update_num_channels
from typing import Dict, Union, List

def is_global_owner(auth_user_id: int) -> bool:
    """
    Returns a bool for whether they are a global owner or not

    Args:
        auth_user_id (int): The user id of the person we are checking

    Returns:
        Bool: True if they are a global owner, false if they are not
    """
    global_owner = False
    store = data_store.get()
    for user in store['users']:
        if auth_user_id == user['u_id']:
            global_owner = user['is_global_owner']
    return global_owner

def channel_invite_v1(auth_user_id: int, channel_id: int, u_id: int) -> None:
    """
    Adds a user's ID to the channel->user dictionary int he data_store
    Returns nothing as it should just store that data of the user's ID.

    Args:
        auth_user_id(int): The user ID of the user who invited
        channel_id(int): The channel ID of the channel the user got invited to
        u_id(int): The user ID of the user who has been invited

    Raises:
        InputError: User ID does not exist
        InputError: User is channel owner
        InputError: User is already in channel
        AccessError: Authorised user is not a member or owner of the channel
        InputError: Channel ID is not valid

    Returns:
        {}
    """
    data = data_store.get()
    
    if not is_valid_user_id(u_id):
        raise InputError(description="u_id does not refer to a valid user")

    for channel in data['channels']:
        if channel_id == channel['id']:

            # Checks if user is already in channel
            if u_id in channel['users']:
                raise InputError(description="User is already in channel")

            # Checks in user if someone has invited from user or owner
            if auth_user_id not in channel['users']:
                raise AccessError(description="Authorised user is not a member or owner of the channel")

            # Appends the previous made dictionary to the dictionary of user in the channel
            channel['users'].append(u_id)
            add_invite_notif(auth_user_id, u_id, channel_info=channel)
            data_store.set(data)
            update_num_channels(u_id)
            break
    else:
        raise InputError(description="Channel ID is not valid")
    return {
    }

def channel_details_v1(auth_user_id: int, channel_id: int) -> Dict[str, Union[str, bool, List[int]]]:
    """
    This function will provide basic details about the channel

    Args:
        auth_user_id (int): The id a user in the channel
        channel_id (int): The id of the channel we get the info from 
    
    Raises:
        1. InputError 
            -   channel_id does not refer to a valid channel
        2. AccessError
            -   channel_id is valid but the authorised user is not a member
                of the channel
        
    Returns:
    Dict:
        {
        'name': Channel name,
        'is_public': True or False if a channel is public or not,
        'owner_members': The owner's information,
        'all_members': All members of the channel's information
        }
    """
    store = data_store.get()

    # Returns list of members in a channel
    for channel in store['channels']:
        if channel['id'] == channel_id:
            channel_details = channel
            list_of_members = channel['users']
            # If a user not a member of the channel it raises an AccessError
            if auth_user_id not in list_of_members:
                raise AccessError(description="This user does not have access to this channel")
            break
    else:
        # Raises Input Error if channel ID is not found
        raise InputError(description="Channel ID is not valid")

    return {    
        'name': channel_details['name'],
        'is_public': channel_details['public'],
        'owner_members': list(map(get_user_info, [owner for owner in channel_details['owner']])),
        'all_members': list(map(get_user_info, [owner for owner in channel_details['users']]))
    }


def channel_messages_v1(auth_user_id: int, channel_id: int, start: int) -> Dict[str, Union[List[str], int]]:
    """
    Reads all messages from the most recent (index start) to end (start + 50) in the selected channel
    Returns the messages in the channel between the start and end and returns start and end values.

    Args:
        auth_user_id(int): The user ID of the user who is in the Channel
        channel_id(int): The channel ID of the channel the messages are in
        start(int): Start is the index starting point for when to read messages

    Raises:
        InputError: Start is greater then the total number of messages in channel
        AccessError: Auth user is not not a member of the channel
        InputError: Channel ID is not valid

    Returns:
        {messages, start, end}
    """
    data = data_store.get()
    start = int(start)
    # Dict for return usage
    dict_return = {
        'messages': [],
        'start': start,
        'end': start + 50
    }

    for channel in data['channels']:
        if channel_id == channel['id']:
            # Assigns messages the list of dictionarys in channel['message']
            messages = channel['messages']

            # Checks if start is larger then message amount
            if start < 0:
                raise InputError(description="Start has to be a positive integer")

            if start > len(messages):
                raise InputError(description="Start is larger than message amount")

            # Checks if end is larger then message amount
            if start + 50 > len(messages):
                dict_return['end'] = -1
            
            # Loops through all the dictionarys in messages within the range of start and start + 50 (end)
            for i in range(start, start + 50):
                # Appends message[i] within the range
                if i < len(messages):
                    dict_return['messages'].append(messages[-1 - i])
                else:
                    break
            return dict_return
    else:
        raise InputError(description="Channel ID is not valid")


    

def channel_join_v1(auth_user_id: int, channel_id: int) -> None:
    """
    If a channel allows a user to join (Public == True) then the user is added to the list of users in the channel
    Returns nothing as it should just store that data of the user's ID.

    Args:
        auth_user_id(int): The user ID of the user who wants to join the Channel
        channel_id(int): The channel ID of the channel the user wants to join

    Raises:
        InputError: The auth user is already in the channel (in channel->users)
        AccessError: Channel is not public and the authorised user is not already in the channel and is not a global owner
        InputError: Channel ID is not valid

    Returns:
        {}
    """
    data = data_store.get()

    for channel in data['channels']:
        if channel_id == channel['id']:
            # Checks if authorised user is already a member of the channel
            if auth_user_id in channel['users']:
                raise InputError(description="User is already in channel")

            print(is_global_owner(auth_user_id))
            # Raises error if Channel is private and authorised user is not a global owner
            if not channel['public'] and not is_global_owner(auth_user_id):
                raise AccessError(description="Channel is not public")

            channel['users'].append(auth_user_id)
            data_store.set(data)
            update_num_channels(auth_user_id)
            break
    else:
        # Raises Input Error if channel ID is not found
        raise InputError(description="Channel ID is not valid")
    return {
        
    }

def channel_leave(auth_user_id: int, channel_id: int) -> None:
    """
    If a member of an existing channel leaves it removes them from the users in the channel's user list
    Returns nothing as it should just store that data of the user's ID.

    Args:
        auth_user_id(int): The user ID of the user who wants to leave the Channel
        channel_id(int): The channel ID of the channel the user wants to leave

     Raises:
        InputError: Channel_id does not refer to a valid channel
        AccessError: The channel is valid but the user is not a member
    
    Returns:
        {}
    """
    data = data_store.get()

    for channel in data['channels']:
        if channel_id == channel['id']:
            # Checks if authorised user is not a member of the channel
            if auth_user_id not in channel['users']:
                raise AccessError(description="User not in channel")

            if auth_user_id in channel['owner']:
                channel['owner'].remove(auth_user_id)

            channel['users'].remove(auth_user_id)
            data_store.set(data)
            update_num_channels(auth_user_id)
            break
    else:
        # Raises Input Error if channel ID is not found
        raise InputError(description="Channel ID is not valid")
    return{

    }
    
def channel_addowner(token: str, channel_id: int, u_id: int) -> None:
    """
    This function allows an owner of the server to make another member an owner

    Args:
        token (string): The token string of the owner of the channel
        channel_id (int): The id of the channel we are adding the owner to
        u_id (int): The id of the member who is going to be turned into an owner

    Raises:
        AccessError: Channel is valid but the user does not have owner permissions in the channel
        InputError: Channel id does not refer to a valid channel
        InputError: Uid does not refer to a valid user
        InputError: Uid does not refer to a user in the channel
        InputError: The user being made the owner already is an owner

    Returns:
        {}
    """
    store = data_store.get()
    
    # Turns the token into a u_id
    owner_id = get_user_from_token(token)['u_id']
    
    # Finds the channel from the channel id
    for channel in store['channels']:
        if channel['id'] == channel_id:
            # If the user making the request is not an owner, it raises an access error   
            if owner_id not in channel['owner'] and not is_global_owner(owner_id):
                raise AccessError(description="User does not have owner permissions")
                
            # If the user making the request is a global owner but not in the channel, it raises
            # an access error
            if owner_id not in channel['users'] and is_global_owner(owner_id):
                raise AccessError(description="User does not have owner permissions")

            # If the user being made the owner is already an owner it raises an input error 
            if u_id in channel['owner']:
                raise InputError(description="User is already an owner")
            
            # If the user being made owner does not exist it raises an input error
            if not is_valid_user_id(u_id):
                raise InputError(description="Invalid user")

            # If the user being made owner is not in the channel it raises an input error
            if u_id not in channel['users']:
                raise InputError(description="User is not in the channel")

            channel['owner'].append(u_id)
            data_store.set(store)
            return {}
    else:
        # If the channel id does not exist it raises an input error
        raise InputError(description="Invalid channel id")

def channel_removeowner(token: str, channel_id: int, u_id: int) -> None:
    """
    This function allows an owner of the server to remove another owner

    Args:
        token (string): The token string of the owner of the channel
        channel_id (int): The id of the channel we are removing the owner from
        u_id (int): The id of the member who is going to be removed as the owner

    Raises:
        AccessError: Channel is valid but the user does not have owner permissions
        InputError: Channel id does not refer to a valid channel
        InputError: Uid does not refer to a valid user
        InputError: Uid does not refer to an owner in the channel
        InputError: The user being removed as owner is the only owner

    Returns:
        {}
    """
    store = data_store.get()
    
    # Turns the token into a u_id
    owner_id = get_user_from_token(token)['u_id']

    # Finds the channel from the channel id
    for channel in store['channels']:
        if channel['id'] == channel_id:
            # If the user making the request is not an owner, it raises an access error    
            if owner_id not in channel['owner'] and not is_global_owner(owner_id):
                raise AccessError(description="User does not have owner permissions")   

            # If the user making the request is a global owner but not in the channel, it raises
            # an access error
            if owner_id not in channel['users'] and is_global_owner(owner_id):
                raise AccessError(description="User does not have owner permissions")
                
            # If the owner being removed does not exist it raises an input error
            if not is_valid_user_id(u_id):
                raise InputError(description="Invalid user")

            # If the owner being removed is not an owner it raises an input error
            if u_id not in channel['owner']:
                raise InputError(description="User is not in the channel")

            # If the user being removed is the only owner
            if len(channel['owner']) == 1:
                raise InputError(description="User is the only owner")

            channel['owner'].remove(u_id)
            data_store.set(store)

            return {}
    else:
        # If the channel id does not exist it raises an input error
        raise InputError(description="Invalid channel id")
