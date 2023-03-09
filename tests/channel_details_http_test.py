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

    resp = requests.post(config.url + '/auth/register/v2', json={
        'email': 'Group_camel123@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    })

    return resp.json()

# Registers multiple users at once
@pytest.fixture()
def clear_and_register_multiple_users():
    requests.delete(config.url + '/clear/v1', json={})
    
    users = []

    resp_1 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'ruosong.pan@mail.com',
        'password': '123456',
        'name_first': 'ruosong',
        'name_last': 'pan'
    })
    users.append(resp_1.json())

    resp_2 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'jayden.ly@mail.com',
        'password': '123456',
        'name_first': 'jayden',
        'name_last': 'ly'
    })
    users.append(resp_2.json())

    resp_3 = requests.post(config.url + '/auth/register/v2', json={
        'email': 'james.teng@mail.com',
        'password': '123456',
        'name_first': 'james',
        'name_last': 'teng'
    })
    users.append(resp_3.json())

    return users

def test_channel_details_public(clear_and_register_single_user):
    """ Simple test that tests for a single user inside a public channel
    """
    user = clear_and_register_single_user

    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    details = requests.get(config.url + 'channel/details/v2', params={
        'token': user['token'],
        'channel_id': channel['channel_id']
    }).json()
    
    assert details['name'] == 'camel'
    assert details['is_public'] == True
    assert details['owner_members'] == [{'u_id': user['auth_user_id'],     
                                        'name_first': 'Simon',
                                        'name_last': 'Camel',
                                        'email': 'Group_camel123@gmail.com',
                                        'handle_str': 'simoncamel',}]
    assert details['all_members'] == [{'u_id': user['auth_user_id'],     
                                        'name_first': 'Simon',
                                        'name_last': 'Camel',
                                        'email': 'Group_camel123@gmail.com',
                                        'handle_str': 'simoncamel',}]

def test_channel_details_private(clear_and_register_single_user):
    """ Simple test that tests for a single user inside a private channel
    """
    user = clear_and_register_single_user

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': False
    }).json()

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': user['token'],
        'channel_id': channel['channel_id']
    }).json()
    
    assert details['name'] == 'camel'
    assert details['is_public'] == False
    assert details['owner_members'] == [{'u_id': user['auth_user_id'],     
                                        'name_first': 'Simon',
                                        'name_last': 'Camel',
                                        'email': 'Group_camel123@gmail.com',
                                        'handle_str': 'simoncamel',}]
    assert details['all_members'] == [{'u_id': user['auth_user_id'],     
                                        'name_first': 'Simon',
                                        'name_last': 'Camel',
                                        'email': 'Group_camel123@gmail.com',
                                        'handle_str': 'simoncamel',}]

def test_multiple_users_pub(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    })

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['owner_members'] ==  [{
                                            'u_id': user[0]['auth_user_id'],     
                                            'name_first': 'ruosong',
                                            'name_last': 'pan',
                                            'email': 'ruosong.pan@mail.com',
                                            'handle_str': 'ruosongpan',  
                                        }]

    assert details['all_members'] ==    [{
                                            'u_id': user[0]['auth_user_id'],     
                                            'name_first': 'ruosong',
                                            'name_last': 'pan',
                                            'email': 'ruosong.pan@mail.com',
                                            'handle_str': 'ruosongpan', 
                                        },
                                        {
                                            'u_id': user[1]['auth_user_id'],
                                            'name_first': 'jayden',
                                            'name_last': 'ly',
                                            'email': 'jayden.ly@mail.com',
                                            'handle_str': 'jaydenly',
                                        }]


def test_multiple_users_priv(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[1]['token'],
        'name': 'camel',
        'is_public': False
    }).json()

    requests.post(config.url + '/channel/invite/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id'],
        'u_id': user[2]['auth_user_id']
    })

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['owner_members'] ==  [{
                                            'u_id': user[1]['auth_user_id'],     
                                            'name_first': 'jayden',
                                            'name_last': 'ly',
                                            'email': 'jayden.ly@mail.com',
                                            'handle_str': 'jaydenly', 
                                        }]

    assert details['all_members'] ==    [{
                                            'u_id': user[1]['auth_user_id'],
                                            'name_first': 'jayden',
                                            'name_last': 'ly',
                                            'email': 'jayden.ly@mail.com',
                                            'handle_str': 'jaydenly',
                                        },
                                        {
                                            'u_id': user[2]['auth_user_id'],
                                            'name_first': 'james',
                                            'name_last': 'teng',
                                            'email': 'james.teng@mail.com',
                                            'handle_str': 'jamesteng',
                                        }]


def test_invalid_channel_id(clear_and_register_single_user):
    user = clear_and_register_single_user
    
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': user['token'],
        'channel_id': channel['channel_id'] + 100
    }).status_code

    assert details == 400

def test_user_not_in_channel(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': False
    }).json()

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).status_code

    assert details == 403

def test_user_does_not_exist(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'camel',
        'is_public': False
    }).json()

    details = requests.get(config.url + '/channel/details/v2', params={
        'token': 'abcdefg',
        'channel_id': channel['channel_id']
    }).status_code

    assert details == 403    
    