import pytest
from src import config
import requests


# Registers 5 users and returns a tuple of their IDS
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

# Creates multiple channels and returns a list of user_ids and channel_ids ([user_ids], [channel_ids])
@pytest.fixture()
def create_multiple_channels(register_group_camel):
    channels = []
    channel_num = 5
    users = register_group_camel
    for i in range(channel_num):
        response =  requests.post(config.url + '/channels/create/v2', json = {
             'token': users[i]['token'],
             'name': 'Example Channel' + str(i),
             'is_public': True
         })
        channels.append(response.json())
        assert response.status_code == 200
    return channels
    

def test_invalid_channel_name(register_group_camel):
    users = register_group_camel
    # test too short invalid channel name
    response = requests.post(config.url + '/channels/create/v2', json = {
        'token': users[0]['token'],
        'name': '',
        'is_public': True
    })
    assert response.status_code == 400
    # tests too long invalid channel name
    response = requests.post(config.url + '/channels/create/v2', json =  {
        'token': users[1]['token'],
        'name': 'ReallyLongInvalidChannelNameLOL',
        'is_public': True
    })
    assert response.status_code == 400
    # tests normal valid channel name
    response = requests.post(config.url + '/channels/create/v2', json = {
        'token': users[1]['token'],
        'name': 'NormalName',
        'is_public': True
    })
    assert response.status_code == 200

def test_channel_id_uniqueness(register_group_camel):
    users = register_group_camel

    # creates 100 channels with random owners and returns their channel ids in a list
    channel_ids = [
        requests.post(config.url + '/channels/create/v2', json = {
            'token': users[count % 5]['token'],
            'name': 'Example Channel' + str(count),
            'is_public': True
        }).json()['channel_id'] for count in range(100)
    ]
    # check that all returned channel_ids are unique
    assert len(channel_ids) == len(set(channel_ids))


#Tests channels_list_v2() with channel_join
def test_channels_list(create_multiple_channels, register_group_camel):
    users = register_group_camel
    channels = create_multiple_channels
    # get users[0] to join all other channels
    for i in range(0, 4):
        requests.post(config.url + '/channel/join/v2', json = {
            'token': users[0]['token'],
            'channel_id': channels[i]['channel_id']
        })

    channels = requests.get(config.url + '/channels/list/v2', params = {
                                    'token' : users[0]['token']})
    assert channels.status_code == 200
    
    
    
def test_channles_lestall(register_group_camel, create_multiple_channels):
    users = register_group_camel
    create_multiple_channels
    #pass in user0 token and get all channels
    channels = requests.get(config.url + '/channels/listall/v2', params = {
                                    'token' : users[0]['token']})
    assert channels.status_code == 200
    

