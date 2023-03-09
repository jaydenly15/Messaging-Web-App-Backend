# import json
import urllib
import requests
from src import config
import pytest
from src.data_store import data_store
import pytest
from src import config
import requests
from src.channel import channel_details_v1
from src.error import AccessError, InputError

# Registers single user
@pytest.fixture()
def clear_and_register_single_user():
    # Resets server data 
    requests.delete(config.url + '/clear/v1', json={})

    user = requests.post(config.url + '/auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    })

    return user.json()

@pytest.fixture()
def clear_and_create_single_channel(clear_and_register_single_user):
    requests.delete(config.url + '/clear/v1', json={})
    user = clear_and_register_single_user
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'channel_1',
        'is_public': True
    })

    return channel.json()


@pytest.fixture()
def create_input(clear_and_register_single_user,clear_and_create_single_channel):
    requests.delete(config.url + '/clear/v1', json={})
    user = clear_and_register_single_user
    channel = clear_and_create_single_channel
    # Send 10 messages to First Channel
    for i in range(0, 10):
        requests.post(config.url + '/message/send/v1', json = {
        'token': user[i]['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello World!' + str(i)
    })

    return [clear_and_register_single_user, clear_and_create_single_channel]

#__________________________________tests___________________________________

# def test_start_greater_than_total_messages(create_input):
#     token = create_input[0][0]["token"]
#     channel_id = create_input[1][0]["channel_id"]
#     error = requests.get(config.url + '/channel/messages/v2', params = {
#         'token': token,
#         'channel_id': channel_id,
#         'message': 'Hello World!' + str(555)
#     })

#     assert error.status_code == 400

def test_invalid_channel(clear_and_register_single_user):
    user = clear_and_register_single_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': user['token'], 
        'channel_id': channel['channel_id'] + 200, 
        'start': 0
    })
    assert resp.status_code == 400

def test_user_doesnt_exist(clear_and_register_single_user):
    user = clear_and_register_single_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': 'abcd', 
        'channel_id': channel['channel_id'], 
        'start': 0
    })

    assert resp.status_code == 403

def test_start_index_error(clear_and_register_single_user):
    user = clear_and_register_single_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': user['token'], 
        'channel_id': channel['channel_id'], 
        'start': 1
    })

    assert resp.status_code == 400

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': user['token'], 
        'channel_id': channel['channel_id'], 
        'start': -1
    })

    assert resp.status_code == 400

def test_max_50_messages(clear_and_register_single_user):
    user = clear_and_register_single_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    for _ in range(60):
        requests.post(config.url + '/message/send/v1', json = {
            'token': user['token'],
            'channel_id': channel['channel_id'],
            'message': 'BYE!'
        })

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': user['token'], 
        'channel_id': channel['channel_id'], 
        'start': 1
    }).json()['messages']

    assert len(resp) == 50