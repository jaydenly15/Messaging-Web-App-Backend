import pytest
from src.channel import get_user_info

from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import clear_v1, hash, is_valid_user_id
from src.token import generate_token, generate_new_session_id, get_ids_from_token, get_user_from_token, \
                    get_ids_from_token
from src.global_owners import increment_num_global_owners
import re
from src.token import generate_token
import secrets
from src.email_secret import email_secret_code
from typing import Dict, Union

regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

def auth_login_v1(email: str, password:str) -> Dict[str, Union[str, int]]:
    """
    Given a registered user's email and password, returns their `auth_user_id` value.

    Args:
        email (string): A registered email 
        password (string): The correct password associated with 'email'

    Raises:
        InputError: email entered does not belong to a user
        InputError: password is not correct

    Returns:
        int: User ID
    """
    store = data_store.get()

    for user in store['users']:
        # Checks that the email used to login is registered
        if email == user['email']:
            # Raises error if incorrect password
            if user['password'] != hash(password):
                raise InputError(description="Wrong Password")
            else:
                session_id = generate_new_session_id()
                user['session_ids'].append(session_id)
                data_store.set(store)

                return {
                    'token': generate_token(user['u_id'], session_id),
                    'auth_user_id': user['u_id']
                }

    # Raises Input Error if email not found
    raise InputError(description="Email not found")


def auth_register_v1(email: str, password: str, name_first: str, name_last: str) -> Dict[str, Union[str, int]]:
    """
    Registers user and stores user data (e.g email, password, name_first, name_last) as a dictionary into data_store. 
    Returns a unique user ID for a particular user.

    Args:
        email (string): A string satisfying the regular expression given by 
                        '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'
        password (string): A string over six characters 
        name_first (string): A string with length between 1 and 50 characters inclusive
        name_last (string): A string with length between 1 and 50 characters inclusive

    Raises:
        InputError: email entered is not a valid email
        InputError: email address is already being used by another user
        InputError: length of password is less than 6 characters
        InputError: length of name_first is not between 1 and 50 characters inclusive
        InputError: length of name_last is not between 1 and 50 characters inclusive

    Returns:
        integer: Unique user ID
    """
    # Checks if email is valid
    if not re.match(regex, email):
        raise InputError(description="Invalid email")

    # Checks if first and last name is valid 
    if len(name_first) > 50 or len(name_first) == 0:
        raise InputError(description="Name has to be between 1 and 50 characters long")

    if len(name_last) > 50 or len(name_last) == 0:
        raise InputError(description="Name has to be between 1 and 50 characters long")

    # Checks if password is valid
    if len(password) < 6:
        raise InputError(description="Password is too short")
        
    store = data_store.get()

    # Creates list of existing emails
    existing_emails = [user['email'] for user in store['users'] \
        if not user['is_removed']]
    
    # Checks for duplicate emails
    if email in existing_emails:
        raise InputError(description="Email already in use")

    # User id is equal to the number of existing users plus 1
    id = len(store['users']) + 1

    # Converts concatenated name to all lowercase
    handle_str = (name_first + name_last).lower()

    # Makes sure the handle string only has alphanumeric characters
    handle_str = ''.join(char for char in handle_str if char.isalnum())

    # Keeps the string length at most 20 characters
    if len(handle_str) > 20:
        handle_str = handle_str[:20]
    
    # Creates list of current handles
    current_handles = [user['handle_str'] for user in store['users'] \
        if not user['is_removed']]

    # Appends 1, 2, 3 ... to handle if duplicate exists
    if handle_str in current_handles:
        count = 0
        while handle_str + str(count) in current_handles:
            count += 1
        handle_str += str(count)

    session_id = generate_new_session_id()

    # Dictionary containing user information
    new_user = {
        'u_id': id,
        'email': email,
        'password': hash(password),
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle_str,
        'profile_img_url' : ' ',
        'session_ids': [session_id],
        'is_global_owner': False,
        'is_removed': False,
        'notifications': []
    }

    if len(store['users']) == 0:
        new_user['is_global_owner'] = True
        increment_num_global_owners()
    
    store['users'].append(new_user)
    data_store.set(store)

    return {
        'token': generate_token(id, session_id),
        'auth_user_id': id
    }

def auth_logout_v1(token: str) -> None:
    """Given an active token, invalidates the token to log the user out.

    Args:
        token (str): The token of the user who is trying to log out

    Raises:
        AccessError: Token passed in is not valid or inactive

    Returns:
        {}
    """
    u_id, session_id = get_ids_from_token(token)

    store = data_store.get()

    user_found = 0
    for user in store['users']:
        if user['u_id'] == u_id and session_id in user['session_ids']:
            user['session_ids'].remove(session_id)
            user_found = 1

    if not user_found:
        raise AccessError(description="Token passed in is not valid or \
             inactive")

    data_store.set(store)

    return {}

def auth_password_reset_request_v1(email: str) -> None:
    """Given an email address, if the user is a registered user, sends them an email containing a specific secret code,
       that when entered in auth/passwordreset/reset, shows that the user trying to reset
       the password is the one who got sent this email.
       No error should be raised when passed an invalid email, as that would pose a security/privacy concern. 
       When a user requests a password reset, they should be logged out of all current sessions.

    Args:
        email (str): Email where the request is being sent

    Returns:
        {}
    """
    store = data_store.get()

    for user in store['users']:
        if user['email'] == email and not user['is_removed']:
            # Generates unique secret code
            secret_code = secrets.token_hex(10) + str(user['u_id'])
            user['reset'] = secret_code
            user['session_ids'] = []
            email_secret_code(email, secret_code)
            data_store.set(store)
            # Only for testing
            return secret_code
    return 

def auth_password_reset_v1(reset_code, new_password):
    """Given a reset code for a user, set that user's new password to the password provided.

    Args:
        reset_code (str): The code sent to the email of the user
        new_password (str): New password provided by the user

    Raises:
        InputError: Length of the password is less than 6 characters long
        InputError: Reset code is not a valid reset code
    Returns:
        {}
    """
    store = data_store.get()

    if len(new_password) < 6:
        raise InputError(description='Length of password is too short')

    for user in store['users']:
        if user.get('reset', None) == reset_code:
            user['password'] = hash(new_password)
            data_store.set(store)
            return 
    raise InputError(description='Reset code entered is invalid')