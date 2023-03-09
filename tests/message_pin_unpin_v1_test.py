import pytest
from src import config
import json
import urllib
import requests
from src.token import generate_token
from src.error import InputError
from src.error import AccessError

# fixture to register 3 users
@pytest.fixture()
def register_group_camel():
   # Resets server data 
    requests.delete(config.url + '/clear/v1', json={})
    users = []
    num_users = 3
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


# fixture - user[0] creates two channels and a dm, and sends a message to the channel
@pytest.fixture()
def create_send(register_group_camel):
    users = register_group_camel
    # users[0] creates two channels
    channels = []
    for i in range(2):
        channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': users[0]['token'],
            'name': 'Channel ' + str(i + 1),
            'is_public': True
        })
        assert channel.status_code == 200
        channels.append(channel.json())
    channel_msg = requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'message': 'Hello this is a new message'
    })
    assert channel_msg.status_code == 200
    # create a dm with users[0] as the owner with users[1] and users[2]
    dm = requests.post(config.url + '/dm/create/v1', json = {
        'token': users[0]['token'],
        'u_ids': [users[1]['auth_user_id'], users[2]['auth_user_id']]
    })
    assert dm.status_code == 200
    # user[1] sends a message
    dm_msg = requests.post(config.url + '/message/senddm/v1', json = {
        'token': users[1]['token'],
        'dm_id': dm.json()['dm_id'],
        'message': 'hey guys!!'
    })
    assert dm_msg.status_code == 200
    return (users, channels, dm.json(), channel_msg.json(), dm_msg.json())

# ********************************************************PIN ERROR TESTS*****************************************************************
# message_id is not a valid message within a channel or DM that the authorised user has joined
def test_pin_invalid_message_id(create_send):
    users, __, __, __, __ = create_send
    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': 999
    })
    assert response.status_code == 400

# if message is already pinned
def test_already_pinned_channel(create_send):
    users, __, __, channel_msg, __ = create_send
    for i in range(3):
        response = requests.post(config.url + '/message/pin/v1', json = {
            'token': users[0]['token'],
            'message_id': channel_msg['message_id']
        })
        if i > 0:
            assert response.status_code == 400
        else:
            assert response.status_code == 200

# message_id is valid, user is in channel/dm but the authorised user doesn't have owner permissions in the channel/DM
def test_pin_invalid_permissions(create_send):
    users, channels, __, channel_msg, __ = create_send
    # users[1] joins the channel but he does not have owner permissions
    response = requests.post(config.url + '/channel/join/v2', json = {
        'token': users[1]['token'],
        'channel_id': channels[0]['channel_id']
    })
    assert response.status_code == 200
    # users[1] tries to pin the message
    response = requests.post(config.url + '/message/pin/v1', json = {
            'token': users[1]['token'],
            'message_id': channel_msg['message_id']
    })
    assert response.status_code == 403

def test_user_not_in_channel(create_send):
    users, __, __, channel_msg, __ = create_send

    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 400

def test_owner_pin_msg_not_global(create_send):
    users, channels, __, channel_msg, __ = create_send

    requests.post(config.url + '/channel/join/v2', json={
        'token': users[1]['token'],
        'channel_id': channels[0]['channel_id']
    })

    requests.post(config.url + 'channel/addowner/v1', json={
      'token' : users[0]['token'], 
      'channel_id' : channels[0]['channel_id'],
      'u_id' : users[1]['auth_user_id']
    })

    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 200

    # check that message is now pinned
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[1]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0 
    })
    assert messages.json()['messages'][0]['is_pinned'] == True

def test_user_not_owner_in_dm_1(create_send):
    users, __, __, __, dm_msg = create_send

    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[1]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 403

def test_user_not_owner_in_dm_2(create_send):
    __, __, __, __, dm_msg = create_send

    jummy = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jummyshark@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': jummy['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 400

def test_already_pinned_dm(create_send):
    users, __, __, __, dm_msg = create_send

    requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })

    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 400

# ********************************************************UNPIN ERROR TESTS*****************************************************************
def test_unpin_invalid_message_id(create_send):
    users, __, __, __, __ = create_send
    response = requests.post(config.url + '/message/unpin/v1', json = {
            'token': users[0]['token'],
            'message_id': 888
    })
    assert response.status_code == 400


def test_already_unpinned(create_send):
    users, __, __, channel_msg, __ = create_send
    for __ in range(2):
        # message is already unpinned
        response = requests.post(config.url + '/message/unpin/v1', json = {
            'token': users[0]['token'],
            'message_id': channel_msg['message_id']
        })
        assert response.status_code == 400

# message_id is valid, user is in channel/dm but the authorised user doesn't have owner permissions in the channel/DM
def test_unpin_invalid_permissions(create_send):
    users, channels, __, channel_msg, __ = create_send
    # users[0] pins message
    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 200

    # check that message is now pinned
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0 
    })
    assert messages.json()['messages'][0]['is_pinned'] == True


    # users[1] joins the channel but he does not have owner permissions
    response = requests.post(config.url + '/channel/join/v2', json = {
        'token': users[1]['token'],
        'channel_id': channels[0]['channel_id']
    })
    assert response.status_code == 200

    # users[1] tries to unpin the message
    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 403


def test_basic_channel_pin(create_send):
    users, channels, dm, channel_msg, dm_msg = create_send
    # users[0] pin message
    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 200
    # check that message is now pinned
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0 
    })
    assert messages.json()['messages'][0]['is_pinned'] == True

    return (users, channels, dm, channel_msg, dm_msg)

def test_basic_dm_pin(create_send):
    users, channels, dm, channel_msg, dm_msg = create_send
    # users[0] pins dm
    response = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 200

    # check that message is now pinned
    messages = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[1]['token'],
        'dm_id': dm['dm_id'],
        'start': 0 
    })
    assert messages.json()['messages'][0]['is_pinned'] == True

    return (users, channels, dm, channel_msg, dm_msg)

def test_pin_unpin_channel(create_send):  
    users, channels, __, channel_msg, __ = test_basic_channel_pin(create_send)
    # users[0] unpins the message
    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 200

    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == False


def test_pin_unpin_dm(create_send):
    users, __, dm, __, dm_msg = test_basic_dm_pin(create_send)
    # users[0] unpins the message
    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 200

    messages = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == False

def test_unpin_owner(create_send):
    users, channels, __, channel_msg, __ = create_send

    requests.post(config.url + '/channel/join/v2', json={
        'token': users[1]['token'],
        'channel_id': channels[0]['channel_id']
    })

    requests.post(config.url + 'channel/addowner/v1', json={
      'token' : users[0]['token'], 
      'channel_id' : channels[0]['channel_id'],
      'u_id' : users[1]['auth_user_id']
    })

    requests.post(config.url + '/message/pin/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id']
    })
    
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == True
    
    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 200
    
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == False

def test_user_not_in_channel_unpin(create_send):
    users, channels, __, channel_msg, __ = create_send

    jummy = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jummyshark@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    resp = requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id']
    })
    assert resp.status_code == 200
    
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == True

    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': jummy['token'],
        'message_id': channel_msg['message_id']
    })
    assert response.status_code == 400

def test_user_not_in_dm_unpin(create_send):
    users, __, dm, __, dm_msg = create_send

    jummy = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jummyshark@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    
    messages = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == True

    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': jummy['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 400

def test_already_unpinned_dm(create_send):
    users, __, dm, __, dm_msg = create_send

    requests.post(config.url + '/message/pin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    
    messages = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == True

    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 200
    
    messages = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert messages.json()['messages'][0]['is_pinned'] == False

    response = requests.post(config.url + '/message/unpin/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id']
    })
    assert response.status_code == 400
