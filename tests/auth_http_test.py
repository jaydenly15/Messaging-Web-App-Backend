import json
import urllib
import requests
from src import config
from src.auth import auth_register_v1, auth_login_v1
import pytest
from json import dumps
from src.data_store import data_store
from src.other import clear_v1
import time

NUM_USERS = 10

# Registers single user
@pytest.fixture()
def clear_and_register_single_user():
    # Resets server data 
    requests.delete(config.url + 'clear/v1', json={})

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    })
    
    return resp.json()

# Registers multiple users at once
@pytest.fixture()
def clear_and_register_multiple_users():
    requests.delete(config.url + 'clear/v1', json={})
    users = []
    global NUM_USERS
    for i in range(NUM_USERS):
        resp = requests.post(config.url + 'auth/register/v2', json={
            'email': 'Group_camel' + str(i) + '@gmail.com',
            'password': 'camel_hump123',
            'name_first': 'Simon',
            'name_last': 'Camel'
        })
        users.append(resp.json())
    return users

def test_register_no_duplicates1(clear_and_register_single_user):

    # Registers a duplicate user
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    })

    assert resp.status_code == 400

def test_register_no_duplicates2(clear_and_register_multiple_users):
    global NUM_USERS    
    # Registers 1000 duplicate users 
    for i in range(NUM_USERS):
        resp = requests.post(config.url + 'auth/register/v2', json={
            'email': 'Group_camel' + str(i) + '@gmail.com',
            'password': 'camel_hump123',
            'name_first': 'Simon',
            'name_last': 'Camel'
        })
        # Each register call should raise an input error
        resp.status_code == 400

    # Should execute without issue since email is not a duplicate
    resp = requests.post(config.url + 'auth/register/v2', json={
            'email': 'Group_camel' + str(NUM_USERS) + '@gmail.com',
            'password': 'camel_hump123',
            'name_first': 'Simon',
            'name_last': 'Camel'
    })
    resp.status_code == 200

# Tests for invalid email according to provided regex expression
def test_register_invalid_email1():
    requests.delete(config.url + '/clear/v1', json={})

    # Input error raised when trying to register an invalid email
    resp = requests.post(config.url + '/auth/register/v2', json={
            'email': 'Group_camel123',
            'password': 'camel_hump123',
            'name_first': 'Simon',
            'name_last': 'Camel'
        })

    assert resp.status_code == 400

def test_register_invalid_password():
    requests.delete(config.url + 'clear/v1', json={})

    # Input error raised when password is too short
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'c',
        'name_first': 'Simon',
        'name_last': 'Camel'
    })

    assert resp.status_code == 400

def test_invalid_first_name():
    requests.delete(config.url + 'clear/v1', json={})

    # Register user with first name with length < 1
    resp1 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123',
        'password': 'camel_hump123',
        'name_first': '',
        'name_last': 'Camel'
    })

    # Register user with first name with length < 50
    resp2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'averyverylongfirstnamethatisjustabitoverfiftycharacters',
        'name_last': 'Camel'
    })

    # Raises error when name is not between 1 and 50 characters
    assert resp1.status_code == 400
    assert resp2.status_code == 400

def test_invalid_last_name():
    requests.delete(config.url + 'clear/v1', json={})

    # Register user with last name with length < 1
    resp1 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': ''
    })

    # Register user with last name with length < 50
    resp2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'averyverylonglastnamethatisjustabitoverfiftycharacters'
    })

    # Raises Input error when name is not between 1 and 50 characters
    assert resp1.status_code == 400
    assert resp2.status_code == 400

def test_unique_user_keys(clear_and_register_multiple_users):
    users = clear_and_register_multiple_users
    # List of current user IDs
    current_user_ids = [user['auth_user_id'] for user in users]
    # List of current tokens
    current_tokens = [user['token'] for user in users]

    # Checks that list is not empty
    assert len(current_user_ids) != 0
    assert len(current_tokens) != 0

    # Checks that every user_id/token returned is unique
    assert len(current_user_ids) == len(set(current_user_ids))
    assert len(current_tokens) == len(set(current_tokens))

def test_login_wrong_pw(clear_and_register_single_user):
    resp = requests.post(config.url + 'auth/login/v2', json={
        'email': "Group_camel123@gmail.com",
        'password': "cmel_hump123",
    })
    # Input error raised when logging in with an unregistered email
    assert resp.status_code == 400

def test_login_unregistered_email(clear_and_register_single_user):

    login_attempt_1 = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Group_camel234@gmail.com',
        'password': 'cmel_hump123'
    })  

    login_attempt_2 = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Group_camel123gmail.com',
        'password': 'cmel_hump123'
    })    

    login_attempt_3 = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Group_camel123@gmailcom',
        'password': 'cmel_hump123'
    })    

    # Input error raised when logging in with an unregistered email
    assert login_attempt_1.status_code == 400

    # Input error rasied when trying to login with an invalid email according to regex
    assert login_attempt_2.status_code == 400
    assert login_attempt_3.status_code == 400

def test_handle_string_length():
    requests.delete(config.url + '/clear/v1', json={})

    resp = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simonwithalongfirst',
        'name_last': 'Camelname'
    }).json()
    
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': resp['token'],
        'name': 'camel',
        'is_public': False
    }).json()

    handle_str = requests.get(config.url + 'channel/details/v2', params={
        'token': resp['token'],
        'channel_id': channel['channel_id']
    }).json()['owner_members'][0]['handle_str']

    assert handle_str == 'simonwithalongfirstc'
