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
import datetime

# Registers single user
@pytest.fixture()
def clear_and_register_multiple_user():
    # Resets server data 
    requests.delete(config.url + '/clear/v1', json={})

    users = []

    user = requests.post(config.url + '/auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    })

    users.append(user.json())

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'jayden.ly@mail.com',
        'password': '123456',
        'name_first': 'jayden',
        'name_last': 'ly'
    })

    users.append(user1.json())

    user2 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'jayden1.ly@mail.com',
        'password': '123456',
        'name_first': 'jayden',
        'name_last': 'ly'
    })

    users.append(user2.json())

    return users

def test_standup_start_negative(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id':channel['channel_id'], 
        'length': -1
    })

    assert resp.status_code == 400

def test_standup_start_user_not_int_channel(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + '/channels/create/v2', json={
        'token': user[1]['token'],
        'name': 'dodo',
        'is_public': True
    }).json()

    resp = requests.post(config.url + "/standup/start/v1", json={
        'token': user[1]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 1
    })

    assert resp.status_code == 403

def test_standup_start_invalid_channel_id(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'] + 1000, 
        'length': 1
    })

    assert resp.status_code == 400

def test_active_standup_start_running(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 5
    })

    resp = requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 1
    })

    assert resp.status_code == 400

def test_standup_start_runs(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    current_time = round(datetime.datetime.now().timestamp())

    time_finish_standup = requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 5
    }).json()['time_finish']

    assert round(time_finish_standup) == current_time + 5

def test_standup_active_invalid_channel_id(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    resp = requests.get(config.url + "/standup/active/v1", params={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'] + 1000, 
    })

    assert resp.status_code == 400

def test_standup_active_user_doesnt_exist(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + '/channels/create/v2', json={
        'token': user[1]['token'],
        'name': 'dodo',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    resp = requests.get(config.url + "/standup/active/v1", params={
        'token': user[1]['token'], 
        'channel_id': channel['channel_id'], 
    })

    assert resp.status_code == 403

def test_standup_active_false(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.get(config.url + "/standup/active/v1", params={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
    }).json()

    assert resp == {'is_active': False, 'time_finish': None}

def test_standup_active_true(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    resp = requests.get(config.url + "/standup/active/v1", params={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
    }).json()

    assert resp['is_active'] == True

def test_standup_send_invalid_channel_id(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    resp = requests.post(config.url + "/standup/send/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'] + 1000,
        'message': "done"
    })

    assert resp.status_code == 400

def test_standup_send_user_doesnt_exist(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[2]['token'],
        'name': channel['channel_id'],
    }).json()

    requests.post(config.url + '/channels/create/v2', json={
        'token': user[1]['token'],
        'name': 'dodo',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[2]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    requests.post(config.url + "/standup/send/v1", json={
        'token': user[2]['token'], 
        'channel_id': channel['channel_id'],
        'message': 'doney'
    })

    resp = requests.post(config.url + "/standup/send/v1", json={
        'token': user[1]['token'], 
        'channel_id': channel['channel_id'],
        'message': 'done'
    })

    assert resp.status_code == 403

def test_standup_send_invalid_message_length(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    resp = requests.post(config.url + "/standup/send/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'],
        'message': '1'*1001
    })

    assert resp.status_code == 400

def test_standup_send_no_active_standup(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    resp = requests.post(config.url + "/standup/send/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'],
        'message': 'done'
    })

    assert resp.status_code == 400

def test_standup_send_return(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'], 
        'length': 3
    })

    resp = requests.post(config.url + "/standup/send/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel['channel_id'],
        'message': 'done'
    }).json()

    assert resp == {}

def test_standup_send_multiple_channels_return(clear_and_register_multiple_user):
    user = clear_and_register_multiple_user

    requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    channel1 = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'Turkey',
        'is_public': True
    }).json()

    requests.post(config.url + "/standup/start/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel1['channel_id'], 
        'length': 3
    })

    resp = requests.post(config.url + "/standup/send/v1", json={
        'token': user[0]['token'], 
        'channel_id': channel1['channel_id'],
        'message': 'done'
    }).json()

    assert resp == {}