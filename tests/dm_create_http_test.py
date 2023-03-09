import json
import urllib
import requests
from requests.api import get
from src import config
import pytest
from tests.auth_http_test import clear_and_register_multiple_users, \
                                clear_and_register_single_user, NUM_USERS
from src.data_store import data_store
from json import dumps
from src.other import clear_v1

# Clears data, registers many users and returns their user_ids and tokens in a list.
@pytest.fixture
def get_u_ids_and_tokens(clear_and_register_multiple_users):
    users = clear_and_register_multiple_users
    u_ids = [user['auth_user_id'] for user in users]
    tokens = [user['token'] for user in users]

    return (u_ids, tokens)

# Creates a DM and returns the owner's token and the DM's ID.
@pytest.fixture()
def clear_and_create_single_dm(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    # Creates DM and returns dm_id
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': u_ids[1:],
                }).json()['dm_id']

    return (tokens[0], dm_create_id)

# Registers multiple users and creates multiple DMs,
# such that each user sends a DM to every other user.
@pytest.fixture
def clear_and_create_many_dms(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    dm_ids = []

    for i in range(len(tokens)):
        create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[i],
            'u_ids': [u_ids[j] for j in range(len(u_ids)) if j != i]
        }).json()

        dm_ids.append(create_dm_resp['dm_id'])
    
    return {
        'dm_ids': dm_ids,
        'tokens': tokens
    }

# Helper function to get the IDs of DMs a user is in 
# using GET HTTP requests.
def get_dm_ids_of_user(token):
    list_dm_resp = requests.get(config.url + 'dm/list/v1?token=' + token)
    dms = list_dm_resp.json()
    dm_ids = [dm['dm_id'] for dm in dms['dms']]
    
    return dm_ids

def test_dm_create_invalid_token(clear_and_register_single_user):
    token = clear_and_register_single_user['token']

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': token + '!',
            'u_ids': []
    })
    assert create_dm_resp.status_code == 403

def test_dm_create_invalid_ids1(clear_and_register_single_user):
    token = clear_and_register_single_user['token']
    u_id = clear_and_register_single_user['auth_user_id']

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': token,
            'u_ids': [u_id + i for i in range(3)]
    })
    assert create_dm_resp.status_code == 400

def test_dm_create_invalid_ids2(clear_and_register_single_user):
    token = clear_and_register_single_user['token']
    u_id = clear_and_register_single_user['auth_user_id']

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': token + '!',
            'u_ids': [u_id + i for i in range(3)]
    })
    assert create_dm_resp.status_code == 403

def test_dm_create_simple(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens
    dm_ids = []

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[0],
            'u_ids': u_ids[1:]
    })
    dm_ids.append(create_dm_resp.json()['dm_id'])

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[1],
            'u_ids': u_ids[2:] + [u_ids[0]]
    })
    dm_ids.append(create_dm_resp.json()['dm_id'])

    create_dm_resp = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[2],
            'u_ids': u_ids[3:] + [u_ids[0]]
    })
    dm_ids.append(create_dm_resp.json()['dm_id'])

    dm_ids_listed = get_dm_ids_of_user(tokens[0])
    assert dm_ids_listed == dm_ids

    dm_ids_listed = get_dm_ids_of_user(tokens[1])
    assert dm_ids_listed == dm_ids[:-1]

    dm_ids_listed = get_dm_ids_of_user(tokens[2])
    assert dm_ids_listed == dm_ids

def test_create_many_dms1(clear_and_create_many_dms):
    dm_ids_created = clear_and_create_many_dms['dm_ids']
    tokens = clear_and_create_many_dms['tokens']

    # Loops through each registered user
    for i in range(len(tokens)):
        dm_ids_listed = get_dm_ids_of_user(tokens[i])
        # Checks that each user is a member of every other DM
        assert dm_ids_listed == dm_ids_created

def test_create_many_dms2(clear_and_create_many_dms):
    dm_ids_created = clear_and_create_many_dms['dm_ids']
    tokens = clear_and_create_many_dms['tokens']

    # User with token, tokens[0] leaves every other DM, but his own.
    for i in range(1, len(dm_ids_created)):
        requests.post(config.url + 'dm/leave/v1', json={
            'token': tokens[0],
            'dm_id': dm_ids_created[i] 
        })

    # Only DM the 0th user will be in is his own
    dm_ids_listed = get_dm_ids_of_user(tokens[0])
    assert dm_ids_listed == [dm_ids_created[0]]

    # 0th user leaves his own dm
    requests.post(config.url + 'dm/leave/v1', json={
            'token': tokens[0],
            'dm_id': dm_ids_created[0] 
        })

    # 0th user will now be in no DM
    dm_ids_listed = get_dm_ids_of_user(tokens[0])
    assert dm_ids_listed == []

def test_dm_list_empty(get_u_ids_and_tokens):
    _, tokens = get_u_ids_and_tokens

    for i in range(len(tokens)):
        dm_ids_listed = get_dm_ids_of_user(tokens[i])

        assert dm_ids_listed == []

def test_dm_name1():
    # Resets server data 
    requests.delete(config.url + '/clear/v1')

    # Registers user with a purely numeric handle string
    user1 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel1@gmail.com',
        'password': 'camel_hump123',
        'name_first': '1',
        'name_last': '2'
    }).json()
    user1_token = user1['token']

    # Registers user with an empty handle string
    user2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel2@gmail.com',
        'password': 'camel_hump123',
        'name_first': '@',
        'name_last': '!'
    }).json()
    user2_id = user2['auth_user_id']

    # Register user with handle string starting with 'a'
    user3_id = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel3@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Annette',
        'name_last': '!'
    }).json()['auth_user_id']
    
    # Register user with handle string starting with 'b'
    user4_id = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel4@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'Bernard',
        'name_last': '!'
    }).json()['auth_user_id']

    requests.post(config.url + 'dm/create/v1', json={
            'token': user1_token,
            'u_ids': [user2_id, user3_id, user4_id]
    })

    dms_list = requests.get(config.url + 'dm/list/v1?token=' + user1_token)

    assert dms_list.json()['dms'][0]['name'] == ', 12, annette, bernard'

    dms_list = requests.post(config.url + 'dm/create/v1', json={
            'token': user1_token,
            'u_ids': [user3_id, user4_id]
    })

    dms_list = requests.get(config.url + 'dm/list/v1?token=' + user1_token)

    assert dms_list.json()['dms'][1]['name'] == '12, annette, bernard'

def test_dm_name2():
    # Resets server data 
    requests.delete(config.url + '/clear/v1', json={})

    # Registers user with handle 'simoncowel'
    user1 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel1@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'simon',
        'name_last': 'cowel'
    }).json()
    user1_token = user1['token']

    # Registers user with handle 'simoncowel0'
    user2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel2@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'simon',
        'name_last': 'cowel'
    }).json()
    user2_id = user2['auth_user_id']

    # Registers user with handle 'simoncowel1'
    user3_id = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel3@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'simon',
        'name_last': 'cowel'
    }).json()['auth_user_id']
    
    # Registers user with handle 'simoncowel2'
    user4_id = requests.post(config.url + 'auth/register/v2', json={
        'email': 'Group_camel4@gmail.com',
        'password': 'camel_hump123',
        'name_first': 'simon',
        'name_last': 'cowel'
    }).json()['auth_user_id']

    requests.post(config.url + 'dm/create/v1', json={
            'token': user1_token,
            'u_ids': [user2_id, user3_id, user4_id]
    })

    dms_list = requests.get(config.url + 'dm/list/v1?token=' + user1_token)

    assert dms_list.json()['dms'][0]['name'] == 'simoncowel, simoncowel0, simoncowel1, simoncowel2'
    

