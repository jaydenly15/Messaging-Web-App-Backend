import pytest
from src import config
import json
import urllib
import requests
from src.token import generate_token
from src.error import InputError
from src.error import AccessError

# registers a single user, creates a channel with the user and sends a message
@pytest.fixture()
def register_user_create_channel_send_message():
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

    # send a message to the channel
    response = requests.post(config.url + '/message/send/v1', json = {
        'token': token,
        'channel_id': channel.json()['channel_id'],
        'message': 'Hello World!'
    })
    assert response.status_code == 200
    assert response.json()['message_id'] == 1

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


# tests invalid message_id
def test_invalid_message_id(register_user_create_channel_send_message):
    user, __ = register_user_create_channel_send_message
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': user['token'],
        'message_id': 1
    })
    assert response.status_code == 200
    for i in range(5):
        response = requests.delete(config.url + '/message/remove/v1', json = {
            'token': user['token'],
            'message_id': i
        })
        assert response.status_code == 400

def test_simple_user_access(register_group_camel):
    users = register_group_camel
     # create a channel, with users[1] as the owner
    channel = requests.post(config.url + '/channels/create/v2', json = {
        'token': users[1]['token'],
        'name': 'Bobs Channel',
        'is_public': True
    })
    # users[4] and users[3] joins the channel
    for i in range(3,5):
        requests.post(config.url + '/channel/join/v2', json = {
            'token': users[i]['token'],
            'channel_id': channel.json()['channel_id']
        })

    # users[4] sends a message in the channel
    message = requests.post(config.url + '/message/send/v1', json = {
        'token': users[4]['token'],
        'channel_id': channel.json()['channel_id'],
        'message': 'Hello World!'
    })
    assert message.status_code == 200
    # users[3] (invalid users) attemps to delete the message
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[3]['token'],
        'message_id': message.json()['message_id']
    })
    assert response.status_code == 403

    # user[4] deletes the message
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[4]['token'],
        'message_id': message.json()['message_id']
    })
    assert response.status_code == 200
    # all_messages = requests.get(config.url + '/channel/messages/v2', json = {
    #     'token': users[4]['token'],
    #     'channel_id': channel.json()['channel_id'],
    #     'start': 0
    # })
    # assert all_messages.json() == {
    #     'messages': [],
    #     'start': 0,
    #     'end': -1
    # }

# tests access errors for global_owner
def test_global_owner_access(register_group_camel):
    users = register_group_camel
    # create a channel, with users[1] as the owner
    channel = requests.post(config.url + '/channels/create/v2', json = {
        'token': users[1]['token'],
        'name': 'Bobs Channel',
        'is_public': True
    })
    # users[4] joins the channel
    requests.post(config.url + '/channel/join/v2', json = {
        'token': users[4]['token'],
        'channel_id': channel.json()['channel_id']
    })
    # users[4] sends a message in the channel
    message = requests.post(config.url + '/message/send/v1', json = {
        'token': users[4]['token'],
        'channel_id': channel.json()['channel_id'],
        'message': 'Hello World!'
    })
    # users[0] joins the channel
    requests.post(config.url + '/channel/join/v2', json = {
        'token': users[0]['token'],
        'channel_id': channel.json()['channel_id']
    })
    # user[0] deletes the message
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[0]['token'],
        'message_id': message.json()['message_id']
    })
    # should be OK even though user did not send message as user[0] is a global owner
    assert response.status_code == 200

# tests that a single message in channel is removed
def test_remove_single_channel_message(register_user_create_channel_send_message):
    user, __ = register_user_create_channel_send_message
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': user['token'],
        'message_id': 1
    })
    
    # all_messages = requests.get(config.url + '/channel/messages/v2', json = {
    #     'token': user['token'],
    #     'channel_id': channel['channel_id'],
    #     'start': 0
    # })
    # assert all_messages.json() == {
    #     'messages': [],
    #     'start': 0,
    #     'end': -1
    # }
    assert response.status_code == 200

# add multiple channel messages and remove dm message 
def test_remove_dm_message(register_user_create_channel_send_message):
    user, channel = register_user_create_channel_send_message
    for __ in range(50):
        requests.post(config.url + '/message/send/v1', json = {
            'token': user['token'],
            'channel_id': channel['channel_id'],
            'message': 'Hello World!' + 'i'
        })

    new_user = requests.post(config.url + '/auth/register/v2', json = {
            'email': 'Group_camel1@gmail.com',
            'password': 'camel_hump123',
            'name_first': 'Simon',
            'name_last': 'Camel'
    }).json()
    # create a dm between newly registered user and the first user
    new_dm = requests.post(config.url + '/dm/create/v1', json = {
        'token': user['token'],
        'u_ids': [new_user['auth_user_id']]
    })
    assert new_dm.status_code == 200

    # send dm from first user to newly registered user
    message = requests.post(config.url + '/message/senddm/v1', json = {
        'token': user['token'],
        'dm_id': new_dm.json()['dm_id'],
        'message': 'this is a new dm message'
    })

    # try to delete dm from new_users end (receiver)
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': new_user['token'],
        'message_id': message.json()['message_id']
    })
    assert response.status_code == 403

    # delete dm from first_users end (sender)
    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': user['token'],
        'message_id': message.json()['message_id']
    })
    assert response.status_code == 200

def test_invalid_user(register_group_camel):
    users = register_group_camel

    channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': users[0]['token'],
            'name': 'Test Channel',
            'is_public': True
    }).json()

    message = requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello World!'
    }).json()

    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': 'abcdefg',
        'message_id': message['message_id']
    })

    assert response.status_code == 403

def test_channel_owner_remove(register_group_camel):
    users = register_group_camel

    channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': users[3]['token'],
            'name': 'Test Channel',
            'is_public': True
    }).json()

    message = requests.post(config.url + '/message/send/v1', json = {
        'token': users[3]['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello World!'
    }).json()

    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[3]['token'],
        'message_id': message['message_id']
    })

    assert response.status_code == 200

def test_user_not_in_channel(register_group_camel):
    users = register_group_camel

    channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': users[3]['token'],
            'name': 'Test Channel',
            'is_public': False
    }).json()

    message = requests.post(config.url + '/message/send/v1', json = {
        'token': users[3]['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello World!'
    }).json()

    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[4]['token'],
        'message_id': message['message_id']
    })
    assert response.status_code == 400

def test_dm_msg_invalid(register_group_camel):
    users = register_group_camel

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': users[0]['token'],
        'u_ids': [users[1]['auth_user_id']]
    }).json()['dm_id']

    dm_msg = requests.post(config.url + 'message/senddm/v1', json={
        'token': users[1]['token'],
        'dm_id': dm,
        'message':'What is up!'
    }).json()

    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id'] + 200
    })
    assert response.status_code == 400

def test_user_not_in_dm(register_group_camel):
    users = register_group_camel

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': users[0]['token'],
        'u_ids': [users[1]['auth_user_id']]
    }).json()['dm_id']

    dm_msg = requests.post(config.url + 'message/senddm/v1', json={
        'token': users[1]['token'],
        'dm_id': dm,
        'message':'What is up!'
    }).json()

    response = requests.delete(config.url + '/message/remove/v1', json = {
        'token': users[2]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 400