import json
import pytest
import requests
from src import config
from tests.auth_http_test import clear_and_register_multiple_users

INPUT_ERROR = 400

def test_users_all(clear_and_register_multiple_users):
    users = clear_and_register_multiple_users

    user_list = requests.get(config.url + '/users/all/v1', params={
        'token' : users[0]['token'], 
    }).json()

    assert len(user_list['users']) == 10

def test_valid_user_profile():
    requests.delete(config.url + '/clear/v1', json={})

    user = requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()

    profile = requests.get(config.url + '/user/profile/v1', params={
        'token' : user['token'], 
        'u_id' : user['auth_user_id']
    }).json()['user']

    assert profile['u_id'] == user['auth_user_id']
    assert profile['email'] == 'example@mail.com'
    assert profile['name_first'] == 'one'
    assert profile['name_last'] == 'two'
    assert profile['handle_str'] == 'onetwo'

#Testing user_profile_v2 error raising by passing in an invalid u_id
def test_user_invalid_u_id():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={ 
        'name_first' : 'jordan', 
        'name_last' : 'Belfort', 
        'email' : 'jordan.Belfort@gmail.com', 
        'password' : '1234566666'
    }).json()

    output = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id'] + 1
    })
    assert output.status_code == INPUT_ERROR

def test_valid_name_persistence():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={ 
        'name_first' : 'jordan', 
        'name_last' : 'Belfort', 
        'email' : 'jordan.Belfort@gmail.com', 
        'password' : '1234566666'
    }).json()

    output_1 = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id']
    }).json()['user']

    assert output_1['name_first'] == 'jordan'
    assert output_1['name_last'] == 'Belfort' 

    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': user1['token'],
        'name': 'camel',
        'is_public': True
    }).json()

    details = requests.get(config.url + 'channel/details/v2', params={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['all_members'] == [{'u_id': user1['auth_user_id'],     
                                        'name_first': 'jordan',
                                        'name_last': 'Belfort',
                                        'email': 'jordan.Belfort@gmail.com',
                                        'handle_str': 'jordanbelfort',}]

    requests.put(config.url + '/user/profile/setname/v1', json={
        'token' : user1['token'], 
        'name_first' : 'new', 
        'name_last' : 'name'
    })

    output_2 = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id']
    }).json()['user']

    assert output_2['name_first'] == 'new'
    assert output_2['name_last'] == 'name'

    details = requests.get(config.url + 'channel/details/v2', params={
        'token': user1['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['all_members'] == [{'u_id': user1['auth_user_id'],     
                                        'name_first': 'new',
                                        'name_last': 'name',
                                        'email': 'jordan.Belfort@gmail.com',
                                        'handle_str': 'jordanbelfort',}]


def test_invalid_first_name():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={ 
        'name_first' : 'one', 
        'name_last' : 'two', 
        'email' : 'example@mail.com', 
        'password' : '12345666'
    }).json()

    output1 = requests.put(config.url + '/user/profile/setname/v1', json={
        'token' : user1['token'], 
        'name_first' : 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 
        'name_last' : 'two'
    })
    assert output1.status_code == INPUT_ERROR
    
def test_invalid_last_name():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={ 
        'name_first' : 'one',
        'name_last' : 'two', 
        'email' : 'example@mail.com', 
        'password' : '123466666'
    }).json()

    output1 = requests.put(config.url + '/user/profile/setname/v1', json={
        'token' : user1['token'], 
        'name_last' : 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 
        'name_first' : 'one'
    })
    assert output1.status_code == INPUT_ERROR

def test_valid_email():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'name_first' : 'one', 
        'name_last' : 'aye', 
        'email' : 'first@gmail.com', 
        'password' : '12345666'
    }).json()

    requests.put(config.url + '/user/profile/setemail/v1', json={
        'token' : user1['token'], 
        'email' : 'newemail@mail.com'
    })

    output = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id']
    }).json()['user']

    assert output['email'] == 'newemail@mail.com'

def test_invalid_email():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'name_first' : 'one', 
        'name_last' : 'aye', 
        'email' : 'first@gmail.com', 
        'password' : '12345666'
    }).json()

    op1 = requests.put(config.url + '/user/profile/setemail/v1', json={
        'token' : user1['token'], 
        'email' : 'jordanmilchgmail.com'
    })
    assert op1.status_code == INPUT_ERROR
    
def test_email_in_use():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'name_first' : 'one', 
        'name_last' : '1234', 
        'email' : 'first@mail.com', 
        'password' : '123456666'
    }).json()

    op1 = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id']
    })
    assert op1.status_code == 200

    requests.post(config.url + '/auth/register/v1', json={ 
        'name_first' : 'one', 
        'name_last' : '1234', 
        'email' : 'second@mail.com', 
        'password' : '12345666'
    })
    
    op1 = requests.put(config.url + '/user/profile/setemail/v1', json={
        'token' : user1['token'], 
        'email' : 'first@mail.com'
    })
    assert op1.status_code == INPUT_ERROR

def test_valid_handle():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'name_first' : 'one', 
        'name_last' : 'aaa', 
        'email' : 'first@mail.com', 
        'password' : '12346666'
    }).json()    

    output = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id']
    }).json()['user']

    assert output['handle_str'] == 'oneaaa'

    requests.put(config.url + '/user/profile/sethandle/v1', json={
        'token' : user1['token'], 
        'handle_str' : 'newhandle'
    })

    output = requests.get(config.url + '/user/profile/v1', params={
        'token' : user1['token'], 
        'u_id' : user1['auth_user_id']
    }).json()['user']

    assert output['handle_str'] == 'newhandle'

def test_handle_in_use():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'name_first' : 'one', 
        'name_last' : 'aaa', 
        'email' : 'first@mail.com', 
        'password' : '12346666'
    }).json()

    requests.post(config.url + '/auth/register/v2', json={ 
        'name_first' : 'two', 
        'name_last' : 'bbb', 
        'email' : 'second@mail.com', 
        'password' : '12346666'
    })

    op1 = requests.put(config.url + '/user/profile/sethandle/v1', json={
        'token' : user1['token'], 
        'handle_str' : 'twobbb'
    })
    
    assert op1.status_code == INPUT_ERROR
    
def test_handle_less_than_three():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json = { 
        'name_first' : 'o', 
        'name_last' : 'a', 
        'email' : 'first@mail.com', 
        'password' : '123456666'
    }).json()

    op1 = requests.put(config.url + '/user/profile/sethandle/v1', json={
        'token' : user1['token'], 
        'handle_str' : 'oa'
    })
    
    assert op1.status_code == INPUT_ERROR

def test_non_alphanumeric_handle():
    requests.delete(config.url + '/clear/v1', json={})

    user1 = requests.post(config.url + '/auth/register/v2', json={
        'name_first' : 'one', 
        'name_last' : 'aaa', 
        'email' : 'first@mail.com', 
        'password' : '12346666'
    }).json()

    op1 = requests.put(config.url + '/user/profile/sethandle/v1', json={
        'token' : user1['token'], 
        'handle_str' : 'oa@!@#$'
    }).status_code

    assert op1 == INPUT_ERROR
