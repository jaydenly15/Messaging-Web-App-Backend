import json
import urllib
import requests
from src import config
import pytest
from src.data_store import data_store

@pytest.fixture()
def clear_and_register_multiple_users():
    requests.delete(config.url + '/clear/v1', json={})
    
    users = []

    resp_1 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'ruosong.pan@mail.com',
        'password': '123456',
        'name_first': 'ruosong',
        'name_last': 'pan'
    })
    users.append(resp_1.json())

    resp_2 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'jayden.ly@mail.com',
        'password': '123456',
        'name_first': 'jayden',
        'name_last': 'ly'
    })
    users.append(resp_2.json())

    resp_3 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'james.teng@mail.com',
        'password': '123456',
        'name_first': 'james',
        'name_last': 'teng'
    })
    users.append(resp_3.json())

    return users

def test_join_public(clear_and_register_multiple_users):

    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': True
    }).json()

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': user[0]['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['all_members'] ==    [{
        'u_id': user[0]['auth_user_id'],     
        'name_first': 'ruosong',
        'name_last': 'pan',
        'email': 'ruosong.pan@mail.com',
        'handle_str': 'ruosongpan', 
    },
    {
        'u_id': user[1]['auth_user_id'],
        'name_first': 'jayden',
        'name_last': 'ly',
        'email': 'jayden.ly@mail.com',
        'handle_str': 'jaydenly',
    }]

def test_join_private(clear_and_register_multiple_users):

    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': False
    }).json()

    join = requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).status_code

    assert(join == 403)

def test_invalid_channel(clear_and_register_multiple_users):

    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': False
    }).json()

    join = requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id'] + 1
    }).status_code

    assert(join == 400)

def test_channel_member(clear_and_register_multiple_users):

    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': False
    }).json()

    join = requests.post(config.url + '/channel/join/v2', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id']
    }).status_code
    
    assert(join == 400)

def test_wrong_token(clear_and_register_multiple_users):

    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': False
    }).json()

    join = requests.post(config.url + '/channel/join/v2', json={
        'token': 'invalid_token',
        'channel_id': channel['channel_id']
    }).status_code
    
    assert(join == 403)

