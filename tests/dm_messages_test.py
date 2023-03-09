import json
import urllib
import requests
from requests.api import get
from src import config
import pytest
from src.data_store import data_store
from json import dumps
from src.other import clear_v1

# Registers multiple users at once
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

def test_invalid_dm(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    dm = requests.post(config.url + 'dm/create/v1', json={
            'token': user[0]['token'],
            'u_ids': [user[1]['auth_user_id']]
    }).json()['dm_id']

    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': user[0]['token'],
        'dm_id': dm + 2,
        'start': 0
    })

    assert resp.status_code == 400

def test_invalid_start(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    dm = requests.post(config.url + 'dm/create/v1', json={
            'token': user[0]['token'],
            'u_ids': [user[1]['auth_user_id']]
    }).json()['dm_id']

    requests.post(config.url + 'message/senddm/v1', json={
        'token': user[1]['token'],
        'dm_id': dm,
        'message':'What is up!'
    })

    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': user[0]['token'],
        'dm_id': dm,
        'start': 10
    })

    assert resp.status_code == 400

def test_user_not_authorised(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[1]['auth_user_id']]
    }).json()['dm_id']

    requests.post(config.url + 'message/senddm/v1', json={
        'token': user[1]['token'],
        'dm_id': dm,
        'message':'What is up!'
    })

    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': user[2]['token'],
        'dm_id': dm,
        'start': 0
    })

    assert resp.status_code == 403

def test_50_max_messages(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[1]['auth_user_id']]
    }).json()['dm_id']

    for _ in range(60):
        requests.post(config.url + 'message/senddm/v1', json={
            'token': user[1]['token'],
            'dm_id': dm,
            'message':'What is up!'
        })
    
    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': user[1]['token'],
        'dm_id': dm,
        'start': 0
    }).json()['messages']

    assert len(resp) == 50
    

