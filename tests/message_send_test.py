import pytest
from src import config
import json
import urllib
import requests
from src.token import generate_token
from src.error import InputError
from src.error import AccessError
from datetime import datetime
import time

# registers a single user and creates a channel with the user
@pytest.fixture()
def register_user_create_channel():
    # Resets server data 
    requests.delete(config.url + '/clear/v1', json={})
    user = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'bob@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Bob',
        'name_last': 'Camel'
    })
    assert user.status_code == 200
    token = user.json()['token']
    # create a channel
    channel = requests.post(config.url + '/channels/create/v2', json = {
        'token': token,
        'name': 'Bobs Channel',
        'is_public': True
    })
    assert channel.status_code == 200
    return (user.json(), channel.json())

# registers 5 users
@pytest.fixture()
def register_group_camel():
   # Resets server data 
    requests.delete(config.url + '/clear/v1', json={})
    
    users = []
    num_users = 5
    for i in range(num_users):
        response = requests.post(config.url + '/auth/register/v2', json = {
            'email': 'Group_camel' + str(i) + '@gmail.com',
            'password': 'camel_hump123',
            'name_first': 'Simon',
            'name_last': 'Camel'
        })
        users.append(response.json())
        assert response.status_code == 200
    return users

# tests sending a message
def test_send_basic_message(register_user_create_channel):
    user, channel = register_user_create_channel
    
    # send a message to the channel
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello World!'
    })
    assert response.status_code == 200
    assert response.json()['message_id'] == 1

    time.sleep(1)
    
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello World I am James!'
    })
    assert response.status_code == 200
    assert response.json()['message_id'] == 2
    # messages = requests.post(config.url + '/channel/messages/v2', json = {
    #     'token': user['token'],
    #     'channel_id': channel['channel_id'],
    #     'start': 0
    # })
    # assert messages.json()["messages"][0]["message"] == "Hello World!"


# tests invalid channel id
def test_invalid_channel(register_user_create_channel):
    user, __ = register_user_create_channel
    # send message to invalid channel
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': user['token'],
        'channel_id': 3459834958,
        'message': ''
    })
    assert response.status_code == 400


# tests when length of message is invalid
def test_invalid_message(register_user_create_channel):
    user, channel = register_user_create_channel
    # send an invalid short message to the channel
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': ''
    })
    assert response.status_code == 400
    # send an invalid long message to the channel
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'LongMessage'*100
    })
    assert response.status_code == 400

# channel_id is valid but authorised user is not a member of the channel
def test_invalid_access(register_user_create_channel):
    __, channel = register_user_create_channel
    # register a new person who is not in the channel
    user_2 = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jimmythebozo@gmail.com',
        'password': 'averystrongpassword',
        'name_first': 'jim',
        'name_last': 'jenkins'
    })
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': user_2.json()['token'],
        'channel_id': channel['channel_id'],
        'message': "just a normal message lol"
    })
    assert response.status_code == 403

# send multiple messages in different channels and check that each message has a unique id
def test_send_unique_messages(register_group_camel):
    users = register_group_camel
    # creates 100 channels and returns their channel ids in a list
    # user[0] owns channels 0, 5, 10, 15 etc..
    # user[1] owns channels 1, 6, 11, 16 etc..
    # etc...
    channel_ids = [
        requests.post(config.url + '/channels/create/v2', json = {
            'token': users[count % 5]['token'],
            'name': 'Example Channel' + str(count),
            'is_public': True
        }).json() for count in range(100)
    ]

    message_id = []
    for i in range(100):
        # send messages to these 100 channels
        response = requests.post(config.url + '/message/send/v1', json = {
            'token': users[i % 5]['token'],
            'channel_id': channel_ids[i]['channel_id'],
            'message': 'an epic cool message'
        })
        assert response.status_code == 200
        message_id.append(response.json()['message_id'])
    assert len(message_id) == len(set(message_id))

def test_invalid_channel_id(register_group_camel):
    user = register_group_camel

    channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': user[0]['token'],
            'name': 'Test Channel',
            'is_public': True
    }).json()

    resp = requests.post(config.url + '/message/send/v1', json = {
        'token': user[1]['token'],
        'channel_id': channel['channel_id'] + 20,
        'message': 'HELLO!'
    })

    assert resp.status_code == 400