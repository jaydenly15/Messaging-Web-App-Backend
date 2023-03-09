import pytest

from src.data_store import data_store
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1

channel_name = 'Test name'
count = 0

def get_handle_string(email, first_name, last_name):
    """Used to return handle string of registered user without accessing stored data.

    Args:
        email (string): A valid email
        first_name (string): A valid first name
        last_name (string): A valid last name

    Returns:
        handle_str: Unique handle generated for each user
    """
    global channel_name
    global count

    # Registers 'user' and creates channel with 'user' as owner
    id = auth_register_v1(email, 'password', first_name, last_name)['auth_user_id']
    channel_id = channels_create_v1(id, channel_name, True)['channel_id']

    # Uses channel_details to get handle_str of 'user'
    handle = channel_details_v1(id, channel_id)['owner_members'][0]['handle_str']

    # Generates different channel_name to avoid name conflict
    channel_name += str(count)
    count += 1

    # Returns handle of 'user'
    return handle

def test_handle_string_limit():
    clear_v1()

    # Tests for >20 word limit for first name to make handle 
    handle_1 = get_handle_string("test_1@gmail.com","Simonwithalongfirstname", "Camel")
    assert handle_1 == 'simonwithalongfirstn'

    # Tests for >20 word limit for last name to make handle 
    handle_2 = get_handle_string("test_2@gmail.com","Simon", "Camelwithalonglastname")
    assert handle_2 == 'simoncamelwithalongl'

    # Tests for >20 word limit for first name + last name to make handle
    handle_3 = get_handle_string("test_3@gmail.com", "Simonwitha", "Camelbetween")
    assert handle_3 == 'simonwithacamelbetwe'

def test_handle_string_limit_with_numbers():
    clear_v1()

    # Tests for string concatenation string limit with appended numbers
    handle_1 = get_handle_string("test_1@gmail.com", "Simonwithalongfirstname", "Camel")
    assert handle_1 == 'simonwithalongfirstn'

    handle_2 = get_handle_string("test_2@gmail.com", "Simonwithalongfirstname", "Camel")
    assert handle_2 == 'simonwithalongfirstn0'
        
    handle_3 = get_handle_string("test_3@gmail.com", "Simonwithalongfirstname", "Camel")
    assert handle_3 == 'simonwithalongfirstn1'

def test_valid_handle_chars_and_same_handle():
    clear_v1()

    # Tests if the handle gets rid of non-alphanumeric characters
    handle_1 = get_handle_string("test_1@gmail.com", " ", "!")
    assert handle_1 == ''

    # Tests if the handle appends a number if the handle already exists for the same name
    handle_2 = get_handle_string("test_2@gmail.com", " ", "!")
    assert handle_2 == '0'

    # Tests if the handle appends a number if the handle already exists for different names
    handle_3 = get_handle_string("test_3@gmail.com", "@@@@@@@@@@@@", "###########")
    assert handle_3 == '1'