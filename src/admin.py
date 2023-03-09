from src.data_store import data_store
from src.error import AccessError, InputError
from src.global_owners import decrement_num_global_owners, get_num_global_owners, \
    increment_num_global_owners
from src.token import get_user_from_token
from src.other import is_valid_user_id
    
def admin_user_remove_v1(token: str, u_id: int) -> None:
    """
    Given a token with global owner permissions, remove the specified u_id
    from the streams

    Args:
        token (str): The token of the person who is calling the function
        u_id (int): The uid of the person being removed

    Raises:
        AccessError: The authorised user is not a global owner
        InputError: The uid does not refer to a valid user
        InputError: The uid refers to the only global owner

    Returns:
        {}
    """
    store = data_store.get()

    # Raises Access error if authorised user is not a
    # global owner
    if not get_user_from_token(token)['is_global_owner']:
       raise AccessError(description="The authorised user is not a global owner")

    # Raises Input Error if u_id is not valid
    if not is_valid_user_id(u_id):
        raise InputError(description="u_id does not refer to a valid user")

    # Loop to find user with user ID, u_id
    for user in store['users']:
        if user['u_id'] == u_id:    
            # Checks if u_id refers to the only global owner
            # remaining
            if user['is_global_owner'] and get_num_global_owners() == 1:
                raise InputError(description="u_id refers to a user who is \
                    the only global owner")

            # Decrements NUM_GLOBAL_OWNER if a global owner is removed
            if user['is_global_owner']:
                decrement_num_global_owners()

            # Changes name to 'Removed user'
            user['name_first'] = 'Removed'
            user['name_last'] = 'user'
            user['session_ids'] = []
            user['is_removed'] = True

    # Loops through channel
    for channel in store['channels']:
        # Removes user from any channels that user is in
        if u_id in channel['users']:
            channel['users'].remove(u_id)

        if u_id in channel['owner']:
            channel['owner'].remove(u_id)

        # Replace content of messages to 'Removed user'
        for message in channel['messages']:
            if u_id == message['u_id']:
                message['message'] = 'Removed user'

    # Removes user from any DMs that user is a part of
    for dm in store['dms']:
        if u_id in dm['members']:
            dm['members'].remove(u_id)

        for message in dm['messages']:
            if u_id == message['u_id']:
                message['message'] = 'Removed user'

    # Saves any changes to data_store
    data_store.set(store)
    return {}

def admin_user_permission_change_v1(token: str, u_id: int, permission_id: int) -> None: 
    """
    Given a user by their uid, it changes their permissions
    as described by the permissionid

    Args:
        token (str): The token of the person calling the function
        u_id (int): The uid of the person whose permissions are being changed 
        permission_id (int): The permissionid they are being changed to (global owner or user)

    Raises:
        AccessError: Authorised user is not a global owner
        InputError: uid does not refer to a valid user
        InputError: uid refers to the only global owner and they are being demoted to a user
        InputError: permissionid is invalid

    Returns:
        {}
    """
    # Raises Access error if authorised user is not a
    # global owner
    if not get_user_from_token(token)['is_global_owner']:
        raise AccessError(description="The authorised user is not a global owner")

    if permission_id not in [1, 2]:
        raise InputError(description="permission_id is invalid")

    store = data_store.get()

    for user in store['users']:
        if user['u_id'] == u_id:
            break

    # Raises Input Error if u_id is not valid
    if not is_valid_user_id(u_id):
        raise InputError(description="u_id does not refer to a valid user")

    permissions = {1: True, 2: False}

    # Does nothing if user's permission is already permission_id
    if user['is_global_owner'] == permissions[permission_id]:
        return {}
    
    # Checks if u_id refers to the only global owner
    # remaining
    if user['is_global_owner'] and get_num_global_owners() == 1:
        raise InputError(description="u_id refers to a user who is \
            the only global owner")
    print('before', user['is_global_owner'])
    # Updates user permissions
    if permission_id == 1:
        user['is_global_owner'] = True
        increment_num_global_owners()
    else:
        user['is_global_owner'] = False
        decrement_num_global_owners()
    print('after', user['is_global_owner'])
    data_store.set(store)

    return {}
