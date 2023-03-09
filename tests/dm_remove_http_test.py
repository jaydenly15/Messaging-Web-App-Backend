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
from tests.dm_create_http_test import get_dm_ids_of_user, get_u_ids_and_tokens, clear_and_create_single_dm, \
                                clear_and_create_many_dms
from src.token import generate_token
        
def test_dm_remove_invalid_token1(clear_and_create_single_dm):
    owner_token, dm_create_id = clear_and_create_single_dm

    # Removes recently created DM
    dm_remove_resp = requests.delete(config.url + "dm/remove/v1", json={
        'token': owner_token + '!',
        'dm_id': dm_create_id
    })

    # Raises Access error when invalid token is passed in
    assert dm_remove_resp.status_code == 403

    # Removes recently created DM
    dm_remove_resp = requests.delete(config.url + "dm/remove/v1", json={
        'token': owner_token,
        'dm_id': dm_create_id
    })
    
    assert len(get_dm_ids_of_user(owner_token)) == 0


def test_dm_remove_invalid_token2(get_u_ids_and_tokens):
    u_ids, tokens = get_u_ids_and_tokens

    # Creates DM and returns dm_id
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
                'token': tokens[0],
                'u_ids': u_ids[1:],
                }).json()['dm_id']
    
    # Every user should be a part of exactly one DM
    assert len(get_dm_ids_of_user(tokens[0])) == 1
    assert len(get_dm_ids_of_user(tokens[1])) == 1
    assert len(get_dm_ids_of_user(tokens[2])) == 1

    # Attempt to remove DM by unauthorised user 
    dm_remove_resp = requests.delete(config.url + "dm/remove/v1", json={
        'token': tokens[1],
        'dm_id': dm_create_id
    })

    # Raises Access error when invalid token is passed in
    assert dm_remove_resp.status_code == 403

    # Removes recently created DM
    dm_remove_resp = requests.delete(config.url + "dm/remove/v1", json={
        'token': tokens[0],
        'dm_id': dm_create_id
    })
    
    assert len(get_dm_ids_of_user(tokens[0])) == 0
    assert len(get_dm_ids_of_user(tokens[1])) == 0
    assert len(get_dm_ids_of_user(tokens[2])) == 0


def test_dm_remove_invalid_dm_id(clear_and_create_single_dm):
    owner_token, dm_create_id = clear_and_create_single_dm

    # Attempt to remove invalid dm_id
    dm_remove_resp = requests.delete(config.url + "dm/remove/v1", json={
        'token': owner_token,
        'dm_id': dm_create_id + 1
    })

    assert dm_remove_resp.status_code == 400

def test_dm_remove_invalid_token_and_id(clear_and_create_single_dm):
    owner_token, dm_create_id = clear_and_create_single_dm

    # Attempt to remove invalid dm_id
    # Invalid token is passed in 
    dm_remove_resp = requests.delete(config.url + "dm/remove/v1", json={
        'token': owner_token + "@",
        'dm_id': dm_create_id + 1
    })

    assert dm_remove_resp.status_code == 403

def test_dm_remove_simple(clear_and_create_single_dm):
    owner_token, dm_id = clear_and_create_single_dm

    assert len(get_dm_ids_of_user(owner_token)) == 1

    # User with token[0] successfully removes DM
    requests.delete(config.url + "/dm/remove/v1", json={
        'token': owner_token,
        'dm_id': dm_id
    })
    # Gets list of current DMs after removing
    assert len(get_dm_ids_of_user(owner_token)) == 0

def test_remove_many_dms1(clear_and_create_many_dms):
    dm_ids_created = clear_and_create_many_dms['dm_ids']
    tokens = clear_and_create_many_dms['tokens']

    dm_ids_after_remove = dm_ids_created.copy()
    # User with token[0] is initally in every DM created 
    assert get_dm_ids_of_user(tokens[0]) == dm_ids_created

    for i in range(len(tokens)):
        # User with token[i] successfully removes DM
        requests.delete(config.url + "/dm/remove/v1", json={
            'token': tokens[i],
            'dm_id': dm_ids_created[i]
        })
        # After removing get list of dm_ids again
        dms_ids_listed = get_dm_ids_of_user(tokens[i])
        dm_ids_after_remove.remove(dm_ids_created[i])
        assert dms_ids_listed == dm_ids_after_remove


def test_remove_many_dms2(clear_and_create_many_dms):
    dm_ids_created = clear_and_create_many_dms['dm_ids']
    tokens = clear_and_create_many_dms['tokens']

    # Tracker list - the expected result 
    dm_ids_after_removing = dm_ids_created.copy()

    # Before removing, checks that every user is in every other DM
    assert get_dm_ids_of_user(tokens[0]) == dm_ids_created
    assert get_dm_ids_of_user(tokens[1]) == dm_ids_created
    assert get_dm_ids_of_user(tokens[2]) == dm_ids_created

    # Removes DM with dm_id, dm_ids_created[0]
    requests.delete(config.url + "/dm/remove/v1", json={
        'token': tokens[0],
        'dm_id': dm_ids_created[0]
    })

    # Updates tracker list to remove DM with ID, dm_ids_created[0]
    dm_ids_after_removing.remove(dm_ids_created[0])

    assert get_dm_ids_of_user(tokens[0]) == dm_ids_after_removing
    assert get_dm_ids_of_user(tokens[1]) == dm_ids_after_removing
    assert get_dm_ids_of_user(tokens[2]) == dm_ids_after_removing

