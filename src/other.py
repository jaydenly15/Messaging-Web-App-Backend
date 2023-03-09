from src.data_store import data_store
from src.token import get_user_from_token
from json import dump
import hashlib
from typing import Dict, Union

# Writes data as JSON string into new file
def save():
    store = data_store.get()
    with open('src/data_store.json', 'w') as file:
        dump(store, file)

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['message_num'] = 0
    store['session_tracker'] = 0
    store['num_global_owners'] = 0
    data_store.set(store)
    return {}

def is_valid_user_id(id: int) -> bool:
    store = data_store.get()

    user_id_found = False

    for user in store['users']:
        user_exists = not user.get('is_removed', False)
        if user['u_id'] == id and user_exists:
            user_id_found = True

    return user_id_found

def get_user_info(key: Union[int, str]) -> Dict[str, Union[int, str]]:
    """
    Gets the information about a user given the user ID

    Args:
        key (int/string): either the handle_str or ID of the user

    Returns:
        Dict: user info (a dictionary that holds all information about a user)
    """
    store = data_store.get()
    for user in store['users']:
        if key == user['u_id'] or key == user['handle_str']:
            user_info = {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str']
            }
    return user_info

def get_handle_from_id(u_id):
    return get_user_info(u_id)['handle_str']

def hash(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()


