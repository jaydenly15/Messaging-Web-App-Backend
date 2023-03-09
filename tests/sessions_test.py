import json
import requests
from requests.api import get
from src import auth, config
import pytest

from tests.auth_http_test import clear_and_register_multiple_users, \
                                clear_and_register_single_user, NUM_USERS
from tests.dm_create_http_test import clear_and_create_many_dms, clear_and_create_single_dm, \
                                    get_u_ids_and_tokens, get_dm_ids_of_user
from tests.dm_detail_http_test import clear_and_register_user_by_name, get_dm_details
from src.token import get_ids_from_token, generate_token

def test_sessions1(clear_and_register_single_user):
    # User logs in on tab 1
    login_token1 = requests.post(config.url + '/auth/login/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
    }).json()['token']

    # User logs in on tab 2
    login_token2 = requests.post(config.url + '/auth/login/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
    }).json()['token']

    # User on tab 1 is authorised to create DM 
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': login_token1,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 200

    # User logs out on tab 1
    requests.post(config.url + '/auth/logout/v1', json={
        'token': login_token1
    })

    # User on tab 1 is no longer authorised to create DM 
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': login_token1,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 403

    # User on tab 2 is still authorised to create DM, despite logging
    # out on tab 1
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': login_token2,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 200

def test_sessions2(clear_and_register_single_user):
    # User gets token from registering on tab 1
    auth_token = clear_and_register_single_user['token']

    # User gets token from logging in on tab 2
    login_token = requests.post(config.url + '/auth/login/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
    }).json()['token']

    # User on tab 2 is authorised to create DM
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': login_token,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 200

    # User on tab2 logs out 
    requests.post(config.url + '/auth/logout/v1', json={
        'token': login_token
    })

    # User on tab 2 is no longer authorised to create DM
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': login_token,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 403

    # User on tab 1 is still authorised to create DM
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': auth_token,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 200

def test_auth_logout(clear_and_register_single_user):
    # User gets auth token from registering
    auth_token = clear_and_register_single_user['token']

    # Authorised user successfully create DM
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': auth_token,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 200

   # Authorised user is logged out 
    requests.post(config.url + '/auth/logout/v1', json={
        'token': auth_token
    })

    # User is no longer authorised to create DM
    dm_create_resp = requests.post(config.url + 'dm/create/v1', json={
                'token': auth_token,
                'u_ids': [],
    })
    assert dm_create_resp.status_code == 403

def test_auth_logout_invalid_token(clear_and_register_single_user):
    # User gets auth token from registering
    u_id = clear_and_register_single_user['auth_user_id']

    invalid_token = generate_token(u_id + 1, 1)

    resp = requests.post(config.url + '/auth/logout/v1', json={
        'token': invalid_token
    })

    assert resp.status_code == 403



