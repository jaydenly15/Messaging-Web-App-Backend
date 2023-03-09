import json
import requests
from requests.api import get
from src import config
import pytest

from tests.auth_http_test import clear_and_register_multiple_users, \
                                clear_and_register_single_user, NUM_USERS
from tests.dm_create_http_test import clear_and_create_many_dms, clear_and_create_single_dm, \
                                    get_u_ids_and_tokens, get_dm_ids_of_user
from tests.dm_detail_http_test import get_dm_details

def test_dm_leave_simple(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    # Creates DM with all registered users
    # The user with token, token[0] is the owner
    # Returns dm_id
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': u_ids[1:],
                }).json()['dm_id']     
    
    # Gets the list of IDs of current members
    members = get_dm_details(tokens[0], dm_create_id)[1]
    member_ids = [member['u_id'] for member in members]

    # Checks thats every user is in the DM
    for i in range(len(u_ids)):
        assert (u_ids[i] in member_ids) == True

    # Owner leaves DM
    requests.post(config.url + 'dm/leave/v1', json={
        'token': tokens[0],
        'dm_id': dm_create_id 
    })

    # After user (former owner) leaves, he is no longer
    # unauthorised to get details
    status_code = get_dm_details(tokens[0], dm_create_id)
    # Access error is raised
    assert status_code == 403 

    # Get details by passing in an authorised token
    members = get_dm_details(tokens[1], dm_create_id)[1]
    member_ids = [member['u_id'] for member in members]

    # Owner should no longer be in member_ids
    assert (u_ids[0] in member_ids) == False

    # Checks that every other user is still in the DM
    for i in range(1, len(u_ids)):
        assert (u_ids[i] in member_ids) == True
    
def test_empty_dm_after_user_leaves(get_u_ids_and_tokens):
    tokens = get_u_ids_and_tokens[1]

    # Creates DM with only one member, who is the owner
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': [],
                }).json()['dm_id']  

    # Owner leaves DM
    requests.post(config.url + 'dm/leave/v1', json={
        'token': tokens[0],
        'dm_id': dm_create_id 
    })

    # After owner leaves, gets the list of IDs of current members 
    status_code = get_dm_details(tokens[0], dm_create_id)
    assert status_code == 403

def test_leave_invalid_dm_id(get_u_ids_and_tokens):
    tokens = get_u_ids_and_tokens[1]

    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': [],
                }).json()['dm_id']

    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': tokens[0],
        'dm_id': dm_create_id + 1
    })

    assert resp.status_code == 400

def test_dm_leave_invalid_token(get_u_ids_and_tokens):
    tokens = get_u_ids_and_tokens[1]

    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
            'token': tokens[0],
            'u_ids': [],
            }).json()['dm_id']

    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': tokens[1],
        'dm_id': dm_create_id
    })

    resp.status_code == 403


