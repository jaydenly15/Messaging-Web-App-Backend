import jwt
from src.data_store import data_store
from src.error import AccessError
from src.data_store import data_store
from typing import Dict, Union, List, Tuple

SECRET = 'CAMEL'

def reset_session_tracker():
    store = data_store.get()
    store['session_tracker'] = 0
    data_store.set(store)

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    store = data_store.get()
    store['session_tracker'] += 1
    data_store.set(store)
    return store['session_tracker']

# Creates unique token for user given the user ID
def generate_token(auth_user_id: int, session_id: int) -> str:
    user_info = {'u_id': auth_user_id, 'session_id': session_id}
    return jwt.encode(user_info, SECRET, algorithm='HS256')

def get_ids_from_token(token: str) -> Tuple[int]:
    """Get u_ids and session_id from token

    Args:
        token (string): User token (JWT-encoded string)

    Raises:
        AccessError: Token is invalid (non-jwt encoded string passed in)

    Returns:
        u_id: integer
        session_id: integer
    """
    try:
        user = jwt.decode(token, SECRET, algorithms=['HS256'])
        return (user['u_id'], user['session_id'])
    except Exception:
        raise AccessError(description="Invalid token") from None


def get_user_from_token(token: str) -> Dict[str, Union[int, str, List[int], bool, List[Dict[str, Union[int, str]]]]]:
    """Returns a dictionary containing a user's information given
    his/her unique token

    Args:
        token (string): User token (JWT-encoded string)

    Returns:
        user (dictionary): Contains user information
    """
    store = data_store.get()
    u_id, session_id = get_ids_from_token(token)
    for user in store['users']:
        if user['u_id'] == u_id and session_id in user['session_ids']:
            return user
    else:
        raise AccessError(description="Invalid token")
