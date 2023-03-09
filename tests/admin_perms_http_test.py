import json
import urllib
import requests
from requests import status_codes
from src import config
import pytest
from src.user import users_all_v1
from src.token import get_user_from_token
from tests.admin_remove_http_test import get_all_member_ids_from_channel

def get_owner_ids_from_channel(token, channel_id):
    owners = requests.get(config.url + 'channel/details/v2', params={
        'token': token,
        'channel_id': channel_id
    }).json()['owner_members']

    return [member['u_id'] for member in owners]

# Register three users and return a list of dictionary of type
# {token, auth_user_id}
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

# """
# Permission_id: 1 (Owners)
# Permission_id: 2 (Members)
# """

def test_only_global_owner_left(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    # Makes user[1] a global owner
    resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[0]['auth_user_id'],
        'permission_id': 2
    })

    assert resp.status_code == 400

def test_admin_permsission_change_to_global(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users
    
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': True
    }).json()

    requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 1
    }).json()

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[1]['token'],
      'channel_id': channel['channel_id'],
      'u_id': user[1]['auth_user_id']
    })

    details = requests.get(config.url + 'channel/details/v2', params={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['owner_members'] == [{
                                            'u_id': user[0]['auth_user_id'],     
                                            'name_first': 'ruosong',
                                            'name_last': 'pan',
                                            'email': 'ruosong.pan@mail.com',
                                            'handle_str': 'ruosongpan'},
                                        {
                                            'u_id': user[1]['auth_user_id'],     
                                            'name_first': 'jayden',
                                            'name_last': 'ly',
                                            'email': 'jayden.ly@mail.com',
                                            'handle_str': 'jaydenly' 
                                        }]

def test_admin_permsission_change_to_member(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users
    
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': False
    }).json()

    requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 1
    })

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    })

    details = requests.get(config.url + 'channel/details/v2', params={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['all_members'] ==    [{
                                            'u_id': user[0]['auth_user_id'],     
                                            'name_first': 'ruosong',
                                            'name_last': 'pan',
                                            'email': 'ruosong.pan@mail.com',
                                            'handle_str': 'ruosongpan'},
                                        {
                                            'u_id': user[1]['auth_user_id'],     
                                            'name_first': 'jayden',
                                            'name_last': 'ly',
                                            'email': 'jayden.ly@mail.com',
                                            'handle_str': 'jaydenly' 
                                        }]

    requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[1]['token'],
        'u_id': user[0]['auth_user_id'],
        'permission_id': 2
    }).json()

    requests.post(config.url + '/channel/leave/v1', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id']
    })

    resp = requests.post(config.url + '/channel/join/v2', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id']
    })
    assert resp.status_code == 403

    details = requests.get(config.url + 'channel/details/v2', params={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    }).json()

    assert details['all_members'] ==    [{
                                            'u_id': user[1]['auth_user_id'],     
                                            'name_first': 'jayden',
                                            'name_last': 'ly',
                                            'email': 'jayden.ly@mail.com',
                                            'handle_str': 'jaydenly'
                                        }]


def test_global_owner_removeowner(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users
    
    # User[0] creates public channel
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_1',
        'is_public': True
    }).json()

    # Makes user[1] a global owner
    requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 1
    })

    # User[1] joins created channel and attains owner permission
    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    })

    # User[1] attempts to remove user[0] as channel owner but is unsucessful
    # since user[0] is only owner
    remove_owner_resp = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': channel['channel_id'],
      'u_id': user[0]['auth_user_id']
    })
    assert remove_owner_resp.status_code == 400

    # User[1] adds himself as channel owner
    requests.post(config.url + '/channel/addowner/v1', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id'],
        'u_id': user[1]['auth_user_id']
    })

    # User[1] removes user[0] as channel owner 
    # and does so succesfully
    remove_owner_resp = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': channel['channel_id'],
      'u_id': user[0]['auth_user_id']
    })
    assert remove_owner_resp.status_code == 200

    # Checks that user[0] is no longer an owner
    owner_ids = get_owner_ids_from_channel(user[0]['token'], channel['channel_id'])
    assert (user[0]['auth_user_id'] in owner_ids) == False 

def test_global_owner_not_joined(clear_and_register_multiple_users):
    users = clear_and_register_multiple_users
    
    # Gets invalid u_id by summing existing user IDs
    sum = 0
    for user in users:
        sum += user['auth_user_id']

    remove_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': users[0]['token'],
        # Passes in invalid user ID
        'u_id': 2000,
        'permission_id': 1
    })
    assert remove_resp.status_code == 400

def test_invalid_permission_id(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    change_perms_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 5
    }).status_code

    assert change_perms_resp == 400

def test_invalid_token(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    change_perms_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[1]['token'],
        'u_id': user[0]['auth_user_id'],
        'permission_id': 1
    }).status_code

    assert change_perms_resp == 403

def test_perms_no_change(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    change_perms_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 2
    })
    assert change_perms_resp.status_code == 200

def test_remove_permission_first_user(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    change_perms_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[1]['auth_user_id'],
        'permission_id': 1
    })
    assert change_perms_resp.status_code == 200

    change_perms_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[1]['token'],
        'u_id': user[0]['auth_user_id'],
        'permission_id': 2
    })
    assert change_perms_resp.status_code == 200

    change_perms_resp = requests.post(config.url + '/admin/userpermission/change/v1', json={
        'token': user[0]['token'],
        'u_id': user[2]['auth_user_id'],
        'permission_id': 1
    })
    assert change_perms_resp.status_code == 403
