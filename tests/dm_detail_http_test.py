import json
import urllib
import requests
from requests.api import get
import jwt
from src import config
import pytest
from tests.auth_http_test import clear_and_register_multiple_users, \
                                clear_and_register_single_user, NUM_USERS
from src.data_store import data_store
from json import dumps
from src.other import clear_v1
from tests.dm_create_http_test import get_dm_ids_of_user, get_u_ids_and_tokens, clear_and_create_single_dm, \
                                clear_and_create_many_dms

# Register some users with names given in a list
# Returns list of u_ids and list of tokens
def clear_and_register_user_by_name(names):
    requests.delete(config.url + '/clear/v1', json={})
    u_ids = []
    tokens = []
    
    # Loop to register users
    for i in range(len(names)): 
        user = {
                'email': 'Group_camel' + str(i) + '@gmail.com',
                'password': 'camel_hump123',
                'name_first': names[i],
                'name_last': '!'
        }

        register_resp = requests.post(config.url + 'auth/register/v2', \
                                    json=user)

        u_id = register_resp.json()['auth_user_id']
        token = register_resp.json()['token']
        u_ids.append(u_id)
        tokens.append(token)
    
    return (u_ids, tokens)

# Uses HTTP request to get DM's details
def get_dm_details(token, dm_id):
    resp = requests.get(f"{config.url}dm/details/v1?token={token}&dm_id={dm_id}")
    try:
        name, members = resp.json()['name'], resp.json()['members']
        return (name, members)
    except:
        return resp.status_code

def test_dm_details_single_member(clear_and_register_single_user):
    owner_token = clear_and_register_single_user['token']

    # Creates DM and returns dm_id
    dm_id = requests.post(config.url + 'dm/create/v1', json={
                'token': owner_token,
                'u_ids': [],
                }).json()['dm_id']

    name, members = get_dm_details(owner_token, dm_id)
    
    assert members == [{
        'u_id': 1, 
        'email': 'Group_camel123@gmail.com', 
        'name_first': 'Simon', 
        'name_last': 'Camel', 
        'handle_str': 'simoncamel'
    }]
    assert name == 'simoncamel'

def test_dm_details_many_members():
    names = ['ruosong', 'ruosong', 'eric', 'james', 'jayden', 'william']

    u_ids, tokens = clear_and_register_user_by_name(names)

    # Creates DM and returns dm_id
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': u_ids[1:]
    }).json()['dm_id']

    name, members = get_dm_details(tokens[0], dm_create_id)

    assert name == "eric, james, jayden, ruosong, ruosong0, william"
    assert len(members) == 6

    # Check that members are listed in the right order (see assumptions)
    # assert members[0]['name_first'] == 'ruosong'
    # assert members[1]['name_first'] == 'ruosong'
    # assert members[2]['name_first'] == 'eric' ...
    # Or equivalently using list comprehension
    members_first_names = [member['name_first'] for member in members]
    assert members_first_names == names

def test_ordering_of_members_listed():
    names = ['ruosong', 'eric', 'james', 'jayden', 'william']

    u_ids, tokens = clear_and_register_user_by_name(names)

    # Creates DM and returns dm_id
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[3],
                'u_ids': u_ids[:3] + u_ids[4:]
    }).json()['dm_id']

    _, members = get_dm_details(tokens[0], dm_create_id)

    # Checks that owner is listed first
    assert members[0]['name_first'] == 'jayden'
    assert members[1]['name_first'] == 'ruosong'
    assert members[2]['name_first'] == 'eric'
    assert members[3]['name_first'] == 'james'
    assert members[4]['name_first'] == 'william'

def test_dm_details_invalid_token(clear_and_create_single_dm):
    owner_token, dm_create_id = clear_and_create_single_dm

    # DM ID is valid but token is invalid
    status_code = get_dm_details(owner_token + '!', dm_create_id)
    assert status_code == 403

    status_code = get_dm_details(owner_token[:-1], dm_create_id)
    assert status_code == 403

    tampered_jwt = jwt.encode({'u_id': 1}, 'BAD', algorithm='HS256')
    status_code = get_dm_details(tampered_jwt, dm_create_id)
    assert status_code == 403
    

def test_dm_details_invalid_dm_id(clear_and_create_single_dm):
    owner_token, dm_create_id = clear_and_create_single_dm

    # Valid token but invalid dm_id
    status_code = get_dm_details(owner_token, dm_create_id + 1)
    assert status_code == 400

    status_code = get_dm_details(owner_token, dm_create_id - 1)
    assert status_code == 400

    status_code = get_dm_details(owner_token, 0)
    assert status_code == 400


# Helper function to test generated DM names
def get_generated_dm_name(names):
    u_ids, tokens = clear_and_register_user_by_name(names)

    # Creates DM and returns dm_id
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': u_ids[1:]
    }).json()['dm_id']

    name, _ = get_dm_details(tokens[0], dm_create_id)

    return name

def test_generated_name1():
    names = ['1camel', 'camel1', 'c@mel', 'camel1', '1camel']
    assert get_generated_dm_name(names) == \
        '1camel, 1camel0, camel1, camel10, cmel'

def test_generated_name2():
    names = ['@', '@', '@', '@', '@']
    assert get_generated_dm_name(names) == \
        ', 0, 1, 2, 3'



