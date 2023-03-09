from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import is_valid_user_id
from src.token import get_user_from_token
from src.channel import get_user_info
from src.notification import add_invite_notif
from typing import Dict, Union, List
from src.user import update_num_dms

def get_handle_from_id(u_id: int) -> str:
    """Given a authorised user's ID, returns user's handle_str. 

    Args:
        u_id (intger): User ID

    Raises:
        InputError: User ID passed in is invalid

    Returns:
        handle_str: String that is unique for each user
    """
    store = data_store.get()
    # Iterates through store to find user with user ID, u_id
    for user in store['users']:
        if user['u_id'] == u_id:
            handle = user['handle_str']
    return handle

def dm_create_v1(token: str, u_ids: int) -> Dict[str, int]:
    """Given a authorised user's token and a list of valid u_ids,
    creates a DM.
    
    Args:
        token (string): JWT-encoded string
        u_ids (list): List of user IDs

    Raises:
        InputError: An invalid u_id in u_ids

    Returns:
        {'dm_id': dm_id}: A key value pair containing the created DM's ID
    """
    store = data_store.get()

     # Gets owner_id from token
    owner_id = get_user_from_token(token)['u_id']

    # Checks if any user IDs in u_ids is invalid 
    if any([not is_valid_user_id(u_id) for u_id in u_ids]):
        raise InputError(description="Invalid user ID")

    # Gets user ID of all members including the owner
    all_member_ids = []
    all_member_ids.append(owner_id)
    all_member_ids += u_ids

    # Gets handle strings of all members
    all_hande_str = [get_handle_from_id(u_id) for u_id in all_member_ids]
    # Sorts handle_str alphabetically
    all_hande_str.sort()

    # Joins list into comma separated list of user handles
    name = ', '.join(all_hande_str)
    # Sets dm_id to number of existing DMS + 1
    dm_id = len(store['dms']) + 1

    new_dm = {
        'name': name,
        'dm_id': dm_id,
        'owner': owner_id,
        'members': all_member_ids,
        'messages': []        
    }

    store['dms'].append(new_dm)
    for u_id in u_ids:
        add_invite_notif(owner_id, u_id, dm_info=new_dm)
    data_store.set(store)

    for u_id in all_member_ids:
        update_num_dms(u_id)
        
    
    return {
        'dm_id': dm_id
    }

def dm_list_v1(token: str) -> Dict[str, List[Dict[str, Union[int, str]]]]:
    """Returns a list of DMs that the user is a member of

    Args:
        token (str): The token of the person whose dms list is being returned

    Returns:
        dms: list of dictionaries where each dictionary contains types
            {'dm_id': 'dm_id', 'name": 'name'}
    """
    # Gets user ID from token
    user_id = get_user_from_token(token)['u_id']

    store = data_store.get()

    user_dms = []

    # Loop to search for DMs user is a part of
    for dm in store['dms']:
        if user_id in dm['members']:
            # Appends a dictionary containing DM's ID and name 
            # to user_dms
            user_dms.append({
                'dm_id': dm['dm_id'],
                'name': dm['name']
            })    
    return {'dms': user_dms}

def dm_remove_v1(token: str, dm_id: int) -> None:
    """Remove an existing DM, so all members are no longer in the DM. 
    This can only be done by the original creator of the DM.

    Args:
        token (str): The string of the user calling the function
        dm_id (integer): The dmid that the user is apart of

    Raises:
        InputError: dmid does not refer to a valid dm
        AccessError: dmid is valid but the authorised user is not the 
                     original dm creator
    
    Returns:
        {}
    """
    store = data_store.get()

    # Gets user ID of authorised user 
    u_id = get_user_from_token(token)['u_id']

    owner_id = None

    # Loop to search for DM with ID, dm_id
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            all_members = dm['members']
            # Gets owner ID
            owner_id = dm['owner']
            # Sets rem_dm to the DM with ID, dm_id
            rem_dm = dm

    # Raises exception if dm_id does not exist
    if owner_id == None:
        raise InputError(description="dm_id does not refer to a valid DM")

    # Raises exception if the token passed in does not belong to the channel owner
    if owner_id != u_id:
        raise AccessError(description="Only DM's owner can remove DM")

    # Removes DM with ID, dm_id
    store['dms'].remove(rem_dm)
    data_store.set(store)

    for id in all_members:
        update_num_dms(id)

    return {}

def dm_details_v1(token: str, dm_id: int) -> Dict[str, Union[str, List[int]]]:
    """ Given a DM with ID dm_id that the authorised user is a member of,
        provide basic details about the DM.

    Args:
        token (string): token of the user calling the function
        dm_id (integer): dmid of the dm they want to get the details of

    Raises:
        AccessError: dm_id is valid and the authorised user is 
                    not a member of the channel
        InputError: dm_id does not refer to a valid DM

    Returns:
        name (string): the name of the dm name
        members (list of type user): the members in the dm

    """
    store = data_store.get()

    # Gets user ID of authorised user 
    u_id = get_user_from_token(token)['u_id']

    # Dictionary of type 'user'
    all_members = []

    for dm in store['dms']:
        # Checks if dm_id is valid
        if dm_id == dm['dm_id']:
            # Raises error of authorised user is not a member of the DM
            if u_id not in dm['members']:
                raise AccessError(description="Authorised user is not a member of the DM")

            # Append other users' info to all members
            members = [get_user_info(member) for member in dm['members']]
            all_members += members

            return {
                'name': dm['name'],
                'members': all_members
            }
    else:
        raise InputError(description="dm_id does not refer to a valid DM")
        

def dm_leave_v1(token: str, dm_id: int) -> None:
    """Given a DM ID, the user is removed as a member of this DM. 
    The creator is allowed to leave and the DM will still exist 
    if this happens. This does not update the name of the DM.

    Args:
        token (string): token of the user calling the function
        dm_id (integer): dmid of the dm they want to leave

    Raises:
        AccessError: dm_id is valid and the authorised user 
                     is not a member of the DM
        InputError: dm_id does not refer to a valid DM

    Returns:
        {}
    """
    store = data_store.get()

    # Gets user ID from token
    u_id = get_user_from_token(token)['u_id']

    # Loop to find dm with ID, dm_id
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            # Raises error if the authorised user is not a member of the DM
            if u_id not in dm['members']:
                raise AccessError(description="Authorised user is not a member of the DM")

            dm['members'].remove(u_id)
            data_store.set(store)
            update_num_dms(u_id)
            return {}
    else:
        raise InputError(description="dm_id does not refer to a valid DM")

def dm_messages_v1(token: str, dm_id: int, start: int) -> Dict[str, Union[List[str], int]]:
    """Given a DM with ID dm_id that the authorised user is a member of, 
    return up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the DM. 
    This function returns a new index "end" which is the value of 
    "start + 50", or, if this function has returned the least recent 
    messages in the DM, returns -1 in "end" to indicate there are no 
    more messages to load after this return.

    Args:
        token (string): token of the user calling the function
        dm_id (integer): dmid of the dm the user want the messages from
        start (integer): the number of the message that the user wants to see from

    Raises:
        InputError: dm_id does not refer to a valid DM
        InputError: start is greater than the total number of 
                    messages in the channel
        AccessError: Authorised user is not a member of the DM

    Returns:
        messages (list of type message): the message
        start (integer): the number from where the messages starts
        end (integer): the number for where the messages ends
    """
    store = data_store.get()

    user = get_user_from_token(token)

    # Loop to find dm with ID, dm_id
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            if user['u_id'] not in dm['members']:
                raise AccessError(description="Authorised user is not a\
                     member of the DM")

            num_messages = min(50, len(dm['messages']) - start)
            end = start + 50

            # Raises error if start is greater than total number of messages
            # in channel
            if num_messages < 0:
                raise InputError(description="start is greater \
                    than the total number of messages in the channel")
            
            # Sets end to equal -1 if not less than 50 messages to return
            if start + num_messages >= len(dm['messages']):
                end = -1

            messages = []

            # Loops through and append num_messages of messages to messages
            for i in range(start, start + num_messages): 
                messages.append(dm['messages'][-1 - i])

            return {
                'messages': messages,
                'start': start,
                'end': end
            }
    raise InputError(description="dm_id does not refer \
        to a valid DM")
