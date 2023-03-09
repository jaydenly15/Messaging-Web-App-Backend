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
def user0_create_send(register_group_camel):
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
    new_msg = requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'message': 'Hello this is a new message'
    })
    assert new_msg.status_code == 200
    # create a dm with users[0] as the owner with users[1] and users[2]
    dm = requests.post(config.url + '/dm/create/v1', json = {
        'token': users[0]['token'],
        'u_ids': [users[1]['auth_user_id'], users[2]['auth_user_id']]
    })
    assert dm.status_code == 200
    return (users, channels, dm.json(), new_msg.json())


# BASIC TEST TO SEE IF SHARE IS WORKING FOR CHANNELS
def test_basic_channel_share(user0_create_send):
    users, channels, __, new_msg = user0_create_send # create channel and dm, with message from user[0] in the channel
    # user[0] shares valid message_id (valid)
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': new_msg['message_id'],
        'message': 'Look at this funny message HAHA!!',
        'channel_id': channels[1]['channel_id'], 
        'dm_id': -1
    })
    assert shared_msg.status_code == 200

    # check that shared channel message was sent
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[1]['channel_id'],
        'start': 0
    })
    assert len(messages.json()['messages']) == 1
    assert messages.json()['messages'][0]['message'] ==\
     "'Hello this is a new message' - Look at this funny message HAHA!!"

# BASIC TEST TO SEE IF SHARE IS WORKING FOR DMS
def test_basic_dm_share(user0_create_send):
    users, __, dm, __ = user0_create_send # create channel and dm, with message from user[0] in the channel
    # user[1] sends dm
    dm_msg = requests.post(config.url + '/message/senddm/v1', json = {
        'token': users[1]['token'],
        'dm_id': dm['dm_id'],
        'message': "hello my friend"
    })
    assert dm_msg.status_code == 200
    # user[2] shares dm to the same dm
    shared_dm = requests.post(config.url + '/message/share/v1', json = {
        'token': users[2]['token'],
        'og_message_id': dm_msg.json()['message_id'],
        'message': "I hath shared this message",
        'channel_id': -1,
        "dm_id": dm['dm_id']
    })
    assert shared_dm.status_code == 200

    # check that shared dm was sent
    messages = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0 
    })
    assert len(messages.json()['messages']) == 2
    assert messages.json()['messages'][0]['message'] ==\
    "'hello my friend' - I hath shared this message"


# InputError to test when: 
# BOTH channel_id and dm_id are invalid
# or neither channel_id NOR dm_id are -1
def test_invalid_channel_dm_id(user0_create_send):
    users, channels, dm, new_msg = user0_create_send
    # NEITHER CHANNEL_ID NOR DM_ID IS -1
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': new_msg['message_id'],
        'message': 'Look at this funny message HAHA!!',
        'channel_id': channels[0]['channel_id'], 
        'dm_id': dm['dm_id']
    })
    assert shared_msg.status_code == 400
    # invalid channel_id 
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': new_msg['message_id'],
        'message': 'Look at this funny message HAHA!!',
        'channel_id': 42, 
        'dm_id': -1
    })
    assert shared_msg.status_code == 400
    # invalid dm_id
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': new_msg['message_id'],
        'message': 'Look at this funny message HAHA!!',
        'channel_id': -1, 
        'dm_id': 42
    })
    assert shared_msg.status_code == 400

# InputError when og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_invalid_og_message_id(user0_create_send):
    users, channels, __, __ = user0_create_send # create channel and dm, with message from user[0] in the channel
    # user[0] shares invalid message_id (InputError)
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': 42,
        'message': 'Look at this funny message HAHA!!',
        'channel_id': channels[0]['channel_id'], 
        'dm_id': -1
    })
    assert shared_msg.status_code == 400

# InputError when length of message is more than 1000 characters
def test_invalid_message_length(user0_create_send):
    users, channels, __, new_msg = user0_create_send # create channel and dm, with message from user[0] in the channel
    # user[1] additional message is > 1000 characters (InputError)
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': new_msg['message_id'],
        'message': 'Look at this funny message HAHA!!'*1000,
        'channel_id': channels[0]['channel_id'], 
        'dm_id': -1
    })
    assert shared_msg.status_code == 400

# AccessError when both channel_id AND dm_id are valid but user has not joined the channel/DM they are tryign to share the message to
def test_channel_access_error(user0_create_send):
    users, channels, __, new_msg = user0_create_send # create channel and dm, with message from user[0] in the channel
    # users[1] joins channels[0]
    requests.post(config.url + '/channel/join/v2', json = {
        'token': users[1]['token'],
        'channel_id': channels[0]['channel_id']
    })
    # users[1] has not joined the channel he is trying to share the message to
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[1]['token'],
        'og_message_id': new_msg['message_id'],
        'message': 'Look at this funny message HAHA!!',
        'channel_id': channels[1]['channel_id'], 
        'dm_id': -1
    })
    assert shared_msg.status_code == 403

def test_dm_access_error(user0_create_send):
    users, channels, dm, __ = user0_create_send # create channel and dm, with message from user[0] in the channel
    # user[1] sends dm
    dm_msg = requests.post(config.url + '/message/senddm/v1', json = {
        'token': users[1]['token'],
        'dm_id': dm['dm_id'],
        'message': "hello my friend"
    })
    assert dm_msg.status_code == 200
    # user[2] shares dm to the channel that they are not in
    shared_dm = requests.post(config.url + '/message/share/v1', json = {
        'token': users[2]['token'],
        'og_message_id': dm_msg.json()['message_id'],
        'message': "I hath shared this message",
        'channel_id': channels[0]['channel_id'],
        "dm_id": -1
    })
    assert shared_dm.status_code == 403


    # create a dm with users[1] as the owner with users[3] 
    dm = requests.post(config.url + '/dm/create/v1', json = {
        'token': users[1]['token'],
        'u_ids': [users[0]['auth_user_id']]
    })
    assert dm.status_code == 200
    # user[2] shares dm msg to a dm that they are not in 
    shared_dm = requests.post(config.url + '/message/share/v1', json = {
        'token': users[2]['token'],
        'og_message_id': dm_msg.json()['message_id'],
        'message': "Please let me share this message ;(",
        'channel_id': -1,
        "dm_id": dm.json()['dm_id']
    })
    assert shared_dm.status_code == 403

def test_invalid_dm_og_message_id(user0_create_send):
    users, __, dm, __ = user0_create_send # create channel and dm, with message from user[0] in the channel

    dm_msg = requests.post(config.url + '/message/senddm/v1', json = {
        'token': users[1]['token'],
        'dm_id': dm['dm_id'],
        'message': "hello my friend"
    }).json()
    # user[0] shares invalid message_id (InputError)
    shared_msg = requests.post(config.url + '/message/share/v1', json = {
        'token': users[0]['token'],
        'og_message_id': dm_msg,
        'message': 'Look at this funny message HAHA!!',
        'channel_id': -1, 
        'dm_id': dm['dm_id']
    })
    assert shared_msg.status_code == 400