import pytest
from src import config
import requests
from tests.dm_create_http_test import get_u_ids_and_tokens, clear_and_create_single_dm, \
                                 clear_and_create_many_dms
from tests.message_send_test import register_user_create_channel
from tests.auth_http_test import clear_and_register_multiple_users


@pytest.fixture()
def dm_create_simple(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens
    dm_ids1 = []

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[0],
            'u_ids': u_ids[:1]
        })
    dm_ids1.append(create_dm_resp.json()['dm_id'])

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[1],
            'u_ids': u_ids[0:]
        })
    dm_ids1.append(create_dm_resp.json()['dm_id'])

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[2],
            'u_ids': u_ids[0:]
        })
    dm_ids1.append(create_dm_resp.json()['dm_id'])

    return [dm_ids1, tokens]

def test_send_simple_dm(dm_create_simple):
    dm_id, user = dm_create_simple

    dm = requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0],
        'dm_id': dm_id[0],
        'message':'Hello world'
    }).json()
    assert dm['message_id'] == 1 

def test_send_invalid_dm(dm_create_simple):
    dm_id, user = dm_create_simple

    dm = requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0],
        'dm_id': dm_id[0] + 100,
        'message':'Hello world'
    })
    assert dm.status_code == 400

def test_send_invalid_message(dm_create_simple):
    dm_id, user = dm_create_simple

    dm = requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0],
        'dm_id': dm_id[0],
        'message':''
    })
    assert dm.status_code == 400

    dm = requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0],
        'dm_id': dm_id[0],
        'message':'a' * 1002
    }) 
    assert dm.status_code == 400

def test_user_not_in_dm(dm_create_simple):
    dm_id, user = dm_create_simple

    dm = requests.post(config.url + 'message/senddm/v1', json={
        'token': user[2],
        'dm_id': dm_id[0],
        'message':'Hello World'
    })
    assert dm.status_code == 403
    
# 50 messages edge case
def test_50_messages(clear_and_register_multiple_users):
    users = clear_and_register_multiple_users
    owner = users.pop(0)
    new_dm = requests.post(config.url + '/dm/create/v1', json = {
        'token': owner['token'],
        'u_ids': [user['auth_user_id'] for user in users]
    })
    assert new_dm.status_code == 200
    # all the users send messages
    for i in range(50):
        sent_dms = requests.post(config.url + '/message/senddm/v1', json = {
            'token': users[i % 9]['token'],
            'dm_id': new_dm.json()['dm_id'],
            'message': "hello this is message " + str(i)
        })
        assert sent_dms.status_code == 200
    
    requests.get(config.url + '/dm/messages/v1', params = {
        'token': owner['token'],
        'dm_id': new_dm.json()['dm_id'],
        'start': 0
    })

    # assert dms.json()['messages'] == {
    #     ["hello this is message " + str(i) for i in range(50)]
    # }
    