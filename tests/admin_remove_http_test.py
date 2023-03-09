import pytest
import json
import urllib
import requests
from requests.api import get
from src import config

from src.admin import admin_user_permission_change_v1, admin_user_remove_v1
from tests.auth_http_test import clear_and_register_single_user
from tests.dm_create_http_test import get_u_ids_and_tokens, clear_and_register_multiple_users
from tests.dm_detail_http_test import get_dm_details

@pytest.fixture()
def clear_and_register_group():
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

def get_all_user_ids():
    users = requests.get(config.url + "users/all/v1").json()['users']
    user_ids = [user['u_id'] for user in users]
    return user_ids

def get_all_member_ids_from_channel(token, channel_id):
    all_members = requests.get(config.url + 'channel/details/v2', params={
        'token': token,
        'channel_id': channel_id
    }).json()['all_members']

    return [member['u_id'] for member in all_members]

def get_all_member_ids_from_dm(token, dm_id):
    _, all_members = get_dm_details(token, dm_id)
    return [member['u_id'] for member in all_members]

def test_admin_remove_simple(clear_and_register_single_user):
    user1 = clear_and_register_single_user

    user2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel1234@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Simon',
        'name_last': 'Camel'
    }).json()

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': user1['token'],
        'u_id': user2['auth_user_id']
    })

    users = requests.get(config.url + '/users/all/v1', params={
        'token' : user1['token'], 
    }).json()['users']

    assert users == [
        {
        'u_id': 1,
        'email': 'Group_camel123@gmail.com',
        'name_first': 'Simon',
        'name_last': 'Camel',
        'handle_str': 'simoncamel'
        },
        {'u_id': 2,
        'email': 'Group_camel1234@gmail.com',
        'name_first': 'Removed',
        'name_last': 'user',
        'handle_str': 'simoncamel0' 
        },
    ]


def test_admin_remove_with_dms(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    # This dm_create is just to populate data_store with dms
    # to increase coverage
    requests.post(config.url + 'dm/create/v1', json={
        'token': tokens[2],
        'u_ids': u_ids[3:],
    })

    dm_create_id2 = requests.post(config.url + 'dm/create/v1', json={
        'token': tokens[0],
        'u_ids': u_ids[1:],
    }).json()['dm_id']

    member_ids = get_all_member_ids_from_dm(tokens[0], dm_create_id2)
    assert member_ids == u_ids

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': tokens[0],
        'u_id': u_ids[1]
    })

    member_ids = get_all_member_ids_from_dm(tokens[0], dm_create_id2)
    assert (u_ids[1] not in member_ids) == True

def test_global_owner_removes_self(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': tokens[0],
        'u_id': u_ids[0]
    })

    assert resp.status_code == 400

def test_admin_remove_with_channels(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    # This channel_create is just to populate data_store
    requests.post(config.url + '/channels/create/v2', json = {
            'token': tokens[0],
            'name': 'Test Channel',
            'is_public': True
    }).json()['channel_id']

    channel_create_id2 = requests.post(config.url + '/channels/create/v2', json = {
            'token': tokens[1],
            'name': 'Example Channel',
            'is_public': True
    }).json()['channel_id']

    requests.post(config.url + '/channel/invite/v2', json={
        'token': tokens[1],
        'channel_id': channel_create_id2,
        'u_id': u_ids[2]
    }).json()

    member_ids = get_all_member_ids_from_channel(tokens[2], channel_create_id2)
    assert member_ids == [u_ids[1], u_ids[2]]

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': tokens[0],
        'u_id': u_ids[1]
    })

    member_ids = get_all_member_ids_from_channel(tokens[2], channel_create_id2)
    assert member_ids == [u_ids[2]]

def test_removed_user_message(clear_and_register_group):
    user = clear_and_register_group

    channel = requests.post(config.url + '/channels/create/v2', json = {
            'token': user[0]['token'],
            'name': 'Test Channel',
            'is_public': True
    }).json()

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    })

    requests.post(config.url + '/message/send/v1', json = {
        'token': user[1]['token'],
        'channel_id': channel['channel_id'],
        'message': 'HELLO!'
    })

    requests.post(config.url + '/message/send/v1', json = {
        'token': user[0]['token'],
        'channel_id': channel['channel_id'],
        'message': 'BYE!'
    })

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id']
    })

    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': user[0]['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    }).json()['messages']

    assert resp[1]['message'] == 'Removed user'

def test_removed_user_message_dm(clear_and_register_group):
    user = clear_and_register_group

    dm = requests.post(config.url + 'dm/create/v1', json={
            'token': user[0]['token'],
            'u_ids': [user[1]['auth_user_id']]
    }).json()['dm_id']

    requests.post(config.url + 'message/senddm/v1', json={
        'token': user[1]['token'],
        'dm_id': dm,
        'message':'What is up!'
    })

    requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0]['token'],
        'dm_id': dm,
        'message':'HI'
    })

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id']
    })

    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': user[0]['token'],
        'dm_id': dm,
        'start': 0
    }).json()['messages']

    assert resp[1]['message'] == 'Removed user'

def test_admin_user_remove2(clear_and_register_group):
    #sets all users
    user = clear_and_register_group
   
    requests.delete(config.url + '/admin/user/remove/v1', json={
        #gets token of person removing the other
        'token': user[0]['token'],
        #gets u_id of the person getting removed
        'u_id': user[1]['auth_user_id']
    })

    users = requests.get(config.url + "users/all/v1?token=" + user[0]['token']).json()['users']
    #gets the amount of users found in the return of user_all (hopefully targeting length of users)
    assert users == [
        {
        'u_id': 1,
        'email': 'ruosong.pan@mail.com',
        'name_first': 'ruosong',
        'name_last': 'pan',
        'handle_str': 'ruosongpan'
        },
        {
        'u_id': 2,
        'email': 'jayden.ly@mail.com',
        'name_first': 'Removed',
        'name_last': 'user',
        'handle_str': 'jaydenly'
        },
        {
        'u_id': 3,
        'email': 'james.teng@mail.com',
        'name_first': 'james',
        'name_last': 'teng',
        'handle_str': 'jamesteng'
        }
    ]

def test_global_owner2(clear_and_register_group):

    user = clear_and_register_group

    remove_user_resp = requests.delete(config.url + '/admin/user/remove/v1', json={
        #Supposedly user 1 isn't a global owner which will be checked in the function
        'token': user[1]['token'],
        'u_id': user[2]['auth_user_id']
    }).status_code

    assert(remove_user_resp == 403)

def test_invalid_user(clear_and_register_group):
    users = clear_and_register_group

    # Gets invalid u_id by summing existing user IDs
    sum = 0
    for user in users:
        sum += user['auth_user_id']

    remove_user_resp = requests.delete(config.url + '/admin/user/remove/v1', json={
        'token': users[0]['token'],
        'u_id': sum
    })
    assert remove_user_resp.status_code == 400

def test_remove_only_global_owner(clear_and_register_group):

    user = clear_and_register_group

    remove_resp = requests.delete(config.url + '/admin/user/remove/v1', json={
        #Supposedly user 1 is the only global owner which will be checked in the function and is trying to remove himself
        'token': user[0]['token'],
        'u_id': user[0]['auth_user_id']
    }).status_code

    assert remove_resp == 400

def test_remove_global_owner_success(clear_and_register_group):
    user = clear_and_register_group

    requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 1
    })

    remove_resp = requests.delete(config.url + '/admin/user/remove/v1', json={
        'token': user[1]['token'],
        'u_id': user[0]['auth_user_id']
    })

    assert remove_resp.status_code == 200

def test_email_reusable():
    requests.delete(config.url + 'clear/v1', json={})

    user1 = requests.post(config.url + 'auth/register/v2', json={
        "email": "globalowner@gmail.com",
        "password": "camel_hump123",
        "name_first": "Simon",
        "name_last": "Camel"
    }).json()

    user2 = requests.post(config.url + 'auth/register/v2', json={
        "email": "remove_me@gmail.com",
        "password": "camel_hump123",
        "name_first": "Ben",
        "name_last": "Camel"
    }).json()

    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': user1['token'],
        'u_id': user2['auth_user_id']
    })

    resp = requests.post(config.url + 'auth/register/v2', json={
        "email": "remove_me@gmail.com",
        "password": "camel_hump123",
        "name_first": "Ben",
        "name_last": "Camel"
    })

    assert resp.status_code == 200


   