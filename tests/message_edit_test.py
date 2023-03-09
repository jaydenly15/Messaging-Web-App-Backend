import pytest
from src import config
import json
import urllib
import requests
from src.token import generate_token, get_user_from_token
from src.error import InputError
from src.error import AccessError
from src.channel import is_global_owner

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

# test if length of message is over 1000
def test_invalid_message_length(register_user_create_channel_send_message):
    user, __ = register_user_create_channel_send_message

    result = requests.put(config.url + "/message/edit/v1", json = {
        'token': user['token'],
        'message_id': 1,
        'message': "a really long message"*1000,
    })
    assert result.status_code == 400
    

# if message_id does not refer to a valid message with the channel that the authorised user has joined
def test_invalid_message_id(register_user_create_channel_send_message):
    user, __ = register_user_create_channel_send_message
    result = requests.put(config.url + "/message/edit/v1", json = {
        'token': user['token'],
        'message_id': 3,
        'message': "an edited message",
    })
    assert result.status_code == 400

# testing if authorised user is not a member of the channel
def test_invalid_access(register_group_camel):
    users = register_group_camel
    # user 2 creates a channel
    token = users[2]['token']
    channel = requests.post(config.url + '/channels/create/v2', json = {
        'token': token,
        'name': 'Bobs Channel',
        'is_public': True
    })
    assert channel.status_code == 200
    # user 2 sends message in channel 
    message = requests.post(config.url + '/message/send/v1', json = {
        'token': token,
        'channel_id':channel.json()['channel_id'],
        'message': "this is a message hello"
    }).json()
    # invalid user 1 edits message
    response = requests.put(config.url + '/message/edit/v1', json = {
        'token': users[1]['token'],
        'message_id': message['message_id'],
        'message': "an edited message",
    })
    # access error
    assert response.status_code == 400
    # valid user 2 edits message
    response = requests.put(config.url + '/message/edit/v1', json = {
        'token': token,
        'message_id': message['message_id'],            
        'message': "an edited message",
    })
    assert response.status_code == 200

    # get messages in the channel
    # messages = requests.post(config.url + '/channel/messages/v2', json = {
    #     'token': token,
    #     'channel_id': channel.json()['channel_id'],
    #     'start': 0
    # })
    # assert messages.json()['messages'][0]['message'] == "an edited message"

# testing for global owner
def test_global_owner(register_group_camel):
    users = register_group_camel
    # user 2 creates a channel
    token = users[2]['token']
    channel = requests.post(config.url + '/channels/create/v2', json = {
        'token': token,
        'name': 'Bobs Channel',
        'is_public': True
    })
    assert channel.status_code == 200
    # user 2 sends message in channel 
    message = requests.post(config.url + '/message/send/v1', json = {
        'token': token,
        'channel_id':channel.json()['channel_id'],
        'message': "this is a message hello"
    }).json()
    # user 0 joins channel
    response = requests.post(config.url + '/channel/join/v2', json = {
        'token': users[0]['token'],
        'channel_id': channel.json()['channel_id']
    })
    assert response.status_code == 200
    # global owner user 0 edits message
    response = requests.put(config.url + '/message/edit/v1', json = {
        'token': users[0]['token'],
        'message_id': message['message_id'],            
        'message': "an edited message",
    })
    assert response.status_code == 200
    # get messages in the channel
    # messages = requests.post(config.url + '/channel/messages/v2', json = {
    #     'token': token,
    #     'channel_id': channel.json()['channel_id'],
    #     'start': 0
    # })
    # assert messages.json()['messages'][0]['message'] == "an edited message"
    
# check if message is deleted if string is empty
def test_delete_message(register_user_create_channel_send_message):
    user, __ = register_user_create_channel_send_message
    response = requests.put(config.url + '/message/edit/v1', json = {
        'token': user['token'],
        'message_id': 1,            
        'message': "",
    })
    assert response.status_code == 200
    # get messages in the channel
    # messages = requests.post(config.url + '/channel/messages/v2', json = {
    #     'token': token,
    #     'channel_id': channel.json()['channel_id'],
    #     'start': 0
    # })
    # assert messages.json() == {
    #     'messages': [],
    #     'start': 0,
    #     'end': -1
    # }

def test_works_in_dm(register_group_camel):
    users = register_group_camel
    create_response = requests.post(config.url + 'dm/create/v1', json={
        'token': users[0]['token'], 
        'u_ids': [users[1]['auth_user_id']]
    })
    dm_id = create_response.json()['dm_id']

    senddm = requests.post(config.url + 'message/senddm/v1', json = {
        'token': users[0]['token'], 
        'dm_id': dm_id, 
        'message': 'Hello'
    })
    message_id = senddm.json()['message_id']

    edit_1 = requests.put(config.url + 'message/edit/v1', json={
        'token': users[1]['token'], 
        'message_id': message_id, 
        'message': 'World'
    })
    assert edit_1.status_code == 403

    edit_2 = requests.put(config.url + 'message/edit/v1', json={
        'token': users[0]['token'], 
        'message_id': message_id, 
        'message': 'World'
    })
    assert edit_2.status_code == 200

def test_invalid_dm_message(register_group_camel):
    users = register_group_camel

    channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': users[0]['token'],
            'name': 'Test Channel',
            'is_public': True
    }).json()

    resp = requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channel['channel_id'],
        'message': 'HELLO!'
    }).json()['message_id']

    requests.post(config.url + 'dm/create/v1', json={
        'token': users[0]['token'], 
        'u_ids': [users[1]['auth_user_id']]
    })

    edit = requests.put(config.url + 'message/edit/v1', json={
        'token': users[1]['token'], 
        'message_id': resp, 
        'message': 'World'
    })
    assert edit.status_code == 400

def test_no_owner_perms(register_group_camel):
    users = register_group_camel

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': users[0]['token'], 
        'u_ids': [users[1]['auth_user_id']]
    }).json()['dm_id']

    dm_msg = requests.post(config.url + 'message/senddm/v1', json={
        'token': users[0]['token'],
        'dm_id': dm,
        'message':'Hello World'
    }).json()['message_id']

    edit = requests.put(config.url + 'message/edit/v1', json={
        'token': users[2]['token'], 
        'message_id': dm_msg, 
        'message': 'Hello!'
    })

    assert edit.status_code == 400

    edit = requests.put(config.url + 'message/edit/v1', json={
        'token': users[1]['token'], 
        'message_id': dm_msg + 200, 
        'message': 'Hello!'
    })
    assert edit.status_code == 400