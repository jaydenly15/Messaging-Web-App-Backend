import pytest

from src.data_store import data_store
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

# Registers a single user
@pytest.fixture()
def clear_and_register():
    clear_v1()
    auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "Simon", "Camel")

# Registers multiple users at once
def clear_and_register_multiple_users():
    clear_v1()
    
    u_ids = []

    num_users = 10
    for i in range(num_users):
        user = auth_register_v1("Group_camel" + str(i) + "@gmail.com", "camel_hump123", "Simon", "Camel")
        u_ids.append(user['auth_user_id'])
    
    return u_ids

# Tests for invalid email according to provided regex expression
def test_register_invalid_email1():
    clear_v1()

    # Input error raised when trying to register an invalid email
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123", "camel_hump123", "Simon", "Camel")

def test_register_invalid_password():
    clear_v1()

    # Input error raised when trying to register with an invalid password
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123@gmail.com", "bad", "Simon", "Camel")

def test_invalid_first_name():
    clear_v1()

    # Input error raised when trying to register with an invalid first name less than 1 character
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "", "Camel")
    
    # Input error raised when trying to register with an invalid first name over 50 characters
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "averyverylongfirstnamethatisjustabitoverfiftycharacters", "Camel")

def test_invalid_last_name():
    clear_v1()

    #Input error raised when trying to reigster with an invalid last name less than 1 character
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "Simon", "")

    # Input error raised when trying to register with an invalid last name over 50 characters
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "Simon", "averyverylonglastnamethatisjustabitoverfiftycharacters")

def test_register_no_duplicates1(clear_and_register):
    # Input Error raised when duplicate email is entered
    with pytest.raises(InputError):
        auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "Simon", "Camel")

def test_register_no_duplicates2():    
    clear_and_register_multiple_users()
    for i in range(10):
        with pytest.raises(InputError):
            # Email is duplicate and should raise Input Error
            auth_register_v1("Group_camel" + str(i) + "@gmail.com", "camel_hump123", "Simon", "Camel")
    
    # Should execute without issue since email is not a duplicate
    auth_register_v1("Group_camel11@gmail.com", "camel_hump123", "Simon", "Camel")

# Checks that auth_register and auth_login are compatible
def test_user_id_works():
    clear_v1()
    auth_id = auth_register_v1("Group_camel123@gmail.com", "camel_hump123", "Simon", "Camel")['auth_user_id']
    login_id = auth_login_v1("Group_camel123@gmail.com", "camel_hump123")['auth_user_id']

    # Checks user_id returned from registering and logging in is the same
    assert auth_id == login_id

def test_unique_user_ids():
    current_user_ids = clear_and_register_multiple_users()

    # Checks that user ids are returned
    assert len(current_user_ids) != 0

    # Checks that every user_id returned is unique
    assert len(current_user_ids) == len(set(current_user_ids))

def test_login_wrong_pw(clear_and_register):
    # Input error raised when logging in with an unregistered email
    with pytest.raises(InputError):
        auth_login_v1("Group_camel123@gmail.com", "cmel_hump123")

def test_login_unregistered_email(clear_and_register):

    # Input error raised when logging in with an unregistered email
    with pytest.raises(InputError):
        auth_login_v1("Group_camel234@gmail.com", "camel_hump123")

    # Input error rasied when trying to login with an invalid email according to regex
    with pytest.raises(InputError):
        auth_login_v1("Group_camel123gmail.com", "camel_hump123")

    with pytest.raises(InputError):
        auth_login_v1("Group_camel123@gmailcom", "camel_hump123")



