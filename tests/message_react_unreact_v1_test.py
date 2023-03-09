import re
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

# users[0] reacts to message
@pytest.fixture()
def user0_react(create_send):
    users, channels, dm, channel_msg, dm_msg = create_send
    response = requests.post(config.url + '/message/react/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200
    return (users, channels, dm, channel_msg, dm_msg )

# ********************************************************REACT ERROR TESTS*****************************************************************

# message_id is not a valid message within a channel/DM the user has joined
def test_invalid_message_id(create_send):
    users, __, __, __, __  = create_send
    response = requests.post(config.url + '/message/react/v1', json = {
        'token': users[0]['token'],
        'message_id': 999999,
        'react_id': 1
    })
    assert response.status_code == 400

# react_id is not a valid react ID (currently the only react_id the frontend has is 1)
def test_invalid_react_id(create_send):
    users, __, __, channel_msg, __  = create_send
    response = requests.post(config.url + '/message/react/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 3
    })
    assert response.status_code == 400


# the message already contains a react with ID react_id from the authorised user
def test_duplicate_react_id(create_send):
    users, __, __, channel_msg, __ = create_send
    for i in range(4):
        response = requests.post(config.url + '/message/react/v1', json = {
            'token': users[0]['token'],
            'message_id': channel_msg['message_id'],
            'react_id': 1
        })
        if i > 0:
            assert response.status_code == 400
        else:   
            assert response.status_code == 200

def test_user_already_reacted_dm(user0_react):
    users, __, __, __, dm_msg = user0_react

    requests.post(config.url + '/message/react/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })

    resp = requests.post(config.url + '/message/react/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })

    assert resp.status_code == 400

def test_user_not_in_react(user0_react):
    users, __, __, channel_msg, dm_msg = user0_react

    react = requests.post(config.url + '/message/react/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 1
    })
    assert react.status_code == 400

    jummy = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jummyshark@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    react = requests.post(config.url + '/message/react/v1', json = {
        'token': jummy['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })
    assert react.status_code == 400

        
# ********************************************************UNREACT ERROR TESTS*****************************************************************

# message_id is not a valid message with a channel or DM that the authorised user has joined
def test_unreact_invalid_message_id(user0_react):
    users, __, __, __, __ = user0_react
    response = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[0]['token'],
        'message_id': 999,
        'react_id': 1
    })
    assert response.status_code == 400

# react_id is not a valid react ID
def test_unreact_invalid_react_id(user0_react):
    users, __, __, channel_msg, __ = user0_react
    response = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 42
    })
    assert response.status_code == 400


# the message does not contain a react with ID react_id from the authorised user
def test_unreact_not_from_authorised_user(user0_react):
    users, __, __, channel_msg, __ = user0_react
    response = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[1]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 1
    })
    assert response.status_code == 400

def test_basic_channel_react(create_send):
    users, channels, __, channel_msg, __ = create_send
    # CHECK THAT MESSAGE IS INITIALLY UNREACTED TO
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    # check that no one has reacted
    assert len(messages.json()['messages'][0]['reacts'][0]['u_ids']) == 0
    # check that there is only one available react
    assert len(messages.json()['messages'][0]['reacts']) == 1
    # check that the only available react_id is 1
    assert messages.json()['messages'][0]['reacts'][0]['react_id'] == 1

    # user[0] reacts to message
    response = requests.post(config.url + '/message/react/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200

    # CHECK THAT MESSAGE IS NOW REACTED TO
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    # check that user has reacted 
    assert len(messages.json()['messages'][0]['reacts'][0]['u_ids']) == 1
    assert users[0]['auth_user_id'] in messages.json()['messages'][0]['reacts'][0]['u_ids']
    assert messages.json()['messages'][0]['reacts'][0]['react_id'] == 1


def test_basic_dm_react(create_send):
    users, __, dm, __, dm_msg = create_send
    # CHECK THAT DM IS INITALLY NOT REACTED TO
    dms = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert dms.status_code == 200

    # check that no one has reacted
    assert len(dms.json()['messages'][0]['reacts'][0]['u_ids']) == 0
    # check that there is only one available react
    assert len(dms.json()['messages'][0]['reacts']) == 1
    # check that the only available react_id is 1
    assert dms.json()['messages'][0]['reacts'][0]['react_id'] == 1

    # user[2] reacts to the dm
    requests.post(config.url + '/message/react/v1', json = {
        'token': users[2]['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })
    # CHECK THAT DM IS NOW REACTED TO
    dms = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert dms.status_code == 200
    # check that user has reacted 
    assert len(dms.json()['messages'][0]['reacts'][0]['u_ids']) == 1
    assert users[2]['auth_user_id'] in dms.json()['messages'][0]['reacts'][0]['u_ids']
    assert dms.json()['messages'][0]['reacts'][0]['react_id'] == 1


# react to message, unreact and check that message is now unreacted
def test_react_unreact_channel(user0_react):    
    # user 0 reacts to message
    users, channels, __, channel_msg, __ = user0_react
    response = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200
    # CHECK THAT MESSAGE IS NOW UNREACTED
    messages = requests.get(config.url + '/channel/messages/v2', params = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'start': 0
    })
    assert messages.status_code == 200
    assert len(messages.json()['messages'][0]['reacts'][0]['u_ids']) == 0


# react to dm, use dm/messages to check that it is actually reacted then unreact and check that dm is now unreacted
def test_react_unreact_dm(create_send):
    users, __, dm, __, dm_msg = create_send
    resp = requests.post(config.url + '/message/react/v1', json = {
        'token': users[1]['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })
    assert resp.status_code == 200

    resp = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[1]['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })
    assert resp.status_code == 200

    # CHECK THAT DM IS NOW UNREACTED
    dms = requests.get(config.url + '/dm/messages/v1', params = {
        'token': users[0]['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert dms.status_code == 200
    assert len(dms.json()['messages'][0]['reacts'][0]['u_ids']) == 0


def test_unreact_msg_no_react(create_send):
    users, __, __, channel_msg, dm_msg = create_send

    resp = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[0]['token'],
        'message_id': channel_msg['message_id'],
        'react_id': 1
    })
    assert resp.status_code == 400

    resp = requests.post(config.url + '/message/unreact/v1', json = {
        'token': users[0]['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })
    assert resp.status_code == 400

def test_user_not_in_unreact(create_send):
    __, __, __, __, dm_msg = create_send

    jummy = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jummyshark@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    resp = requests.post(config.url + '/message/unreact/v1', json = {
        'token': jummy['token'],
        'message_id': dm_msg['message_id'],
        'react_id': 1
    })
    assert resp.status_code == 400
