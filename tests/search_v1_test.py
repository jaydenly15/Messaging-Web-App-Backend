import pytest
from src import config
import json
import urllib
import requests

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

# fixture to create channels and dms
@pytest.fixture()
def create_channels_dms(register_group_camel):
    users = register_group_camel
    channels = []
    # all users make a channel
    for i in range(len(users)):
        new_channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': users[i]['token'],
            'name': "Channel " + str(i),
            'is_public': True
        })
        assert new_channel.status_code == 200
        channels.append(new_channel.json())

    dms = []
    for i in range(len(users)):
        # create dms for each user with users[0] and users[1] inside
        new_dm = requests.post(config.url + '/dm/create/v1', json = {
            'token': users[i]['token'],
            'u_ids': [users[i]['auth_user_id'] for i in range(2)]
        })
        assert new_dm.status_code == 200
        dms.append(new_dm.json())
    return users, channels, dms

# if query_str is less than 1 or over 1000 characters
def test_invalid_input(register_group_camel):
    users = register_group_camel
    # if query_str length is too small
    response = requests.get(config.url + '/search/v1', params = {
        'token': users[0]['token'],
        'query_str': ""
    })
    assert response.status_code == 400
    # if query_str length is too large
    response = requests.get(config.url + '/search/v1', params = {
        'token': users[2]['token'],
        'query_str': "Super Duper Uber Zuber Long Message" * 1000        
    })
    assert response.status_code == 400

# search in dms and channels for substring
def test_basic_search(create_channels_dms):
    # create dms for each user with users[0] and users[1] inside, channels only have their owner inside
    users, channels, dms = create_channels_dms
    requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'message': "hello baby shark"
    })
    # send message to all dms 
    for i in range(len(dms)):
        requests.post(config.url + '/message/senddm/v1', json = {
            'token': users[0]['token'],
            'dm_id': dms[i]['dm_id'],
            'message': 'my favourite song is baby shark doo doo doo' + str(i)
        })
    search_msg = requests.get(config.url + '/search/v1', params = {
        'token': users[0]['token'],
        'query_str': "baby shark"
    })
    assert search_msg.status_code == 200
    # count down from len(dms) + 1 to 0
    for i in range(len(dms), 0, -1):
        if i == range(len(dms) + 1):
            assert search_msg.json()['messages'][i]['message'] == "hello baby shark"
        else:
            assert search_msg.json()['messages'][i]['message'] == "my favourite song is baby shark doo doo doo" + str(i - 1)

def test_message_not_exist(create_channels_dms):
    users, channels, dms = create_channels_dms
    requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'message': "hello baby shark"
    })

    requests.post(config.url + '/message/senddm/v1', json = {
        'token': users[0]['token'],
        'dm_id': dms[0]['dm_id'],
        'message': 'my favourite song is baby shark doo doo doo'
    })

    search_msg = requests.get(config.url + '/search/v1', params = {
        'token': users[0]['token'],
        'query_str': "crab"
    }).json()['messages']

    assert search_msg == []

def test_user_not_in(create_channels_dms):
    users, channels, dms = create_channels_dms

    requests.post(config.url + '/message/send/v1', json = {
        'token': users[0]['token'],
        'channel_id': channels[0]['channel_id'],
        'message': "hello baby shark"
    })

    requests.post(config.url + '/message/senddm/v1', json = {
        'token': users[0]['token'],
        'dm_id': dms[0]['dm_id'],
        'message': 'my favourite song is baby shark doo doo doo'
    })

    jummy = requests.post(config.url + '/auth/register/v2', json = {
        'email': 'jummyshark@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    search_msg = requests.get(config.url + '/search/v1', params = {
        'token': jummy['token'],
        'query_str': "shark"
    }).json()['messages']

    assert search_msg == []