from email import message
from hypothesis import strategies
import pytest
from src import config
import json
import urllib
import requests
from src.error import InputError
from src.error import AccessError
from datetime import datetime, timedelta
from time import sleep
from tests.channel_invite_http_test import clear_and_register_multiple_users

from tests.admin_reset_password_test import User
from hypothesis import given, strategies, settings, Verbosity


def dm_create(token, u_ids):
    dm_create_id = requests.post(config.url + 'dm/create/v1', json={
        'token': token,
        'u_ids': u_ids
    }).json()['dm_id']

    return dm_create_id

def dm_send_later(token, dm_id, message, time_sent):
    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent
    })
    return resp

def view_dm_messages(token, dm_id, start):
    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': token, 
        'dm_id': dm_id,
        'start': start
    }).json()['messages']

    return resp

def test_dm_send_later_basic():
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')

    curr_time = datetime.now()
    time_change = timedelta(seconds=1)
    time_sent = (curr_time + time_change).timestamp()

    dm_create_id = dm_create(token, [])
    resp = dm_send_later(token, dm_create_id, 'Test message', time_sent)
    assert resp.status_code == 200

    messages = view_dm_messages(token, dm_create_id, 0)
    assert len(messages) == 0

    sleep(1)

    messages = view_dm_messages(token, dm_create_id, 0)
    assert len(messages) == 1
    assert messages[0]['message_id'] == dm_create_id

# Generates timestamps that have already passed
@given(strategies.datetimes(max_value=datetime.now() - timedelta(seconds=1)))
def test_sendlater_invalid_time(invalid_datetime):
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    dm_create_id = dm_create(token, [])
    invalid_timestamp = invalid_datetime.timestamp()
    resp = dm_send_later(token, dm_create_id, 'Test message', invalid_timestamp)
    assert resp.status_code == 400

@given(strategies.text(min_size=1001))
@settings(verbosity=Verbosity.verbose, max_examples=3)
def test_message_name_too_long(long_message):
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    dm_id = dm_create(token, [])

    # Calculates the time 1 second from now
    curr_time = datetime.now()
    time_change = timedelta(seconds=1)
    time_stamp = (curr_time + time_change).timestamp()

    resp = dm_send_later(token, dm_id, long_message, time_stamp)
    assert resp.status_code == 400

# Generates valid future timestamps, offset at least 0.1 seconds from current time
@given(strategies.datetimes(min_value=datetime.now() + timedelta(seconds=0.1), \
    max_value=datetime.now() + timedelta(seconds=1)))
def test_invalid_dm(time_sent):
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    dm_id = dm_create(token, [])

    # Produces error because of invalid channel ID
    resp = dm_send_later(token, dm_id + 1, 'Example message', time_sent.timestamp())
    assert resp.status_code == 400

def test_dm_more_than_one(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[2]['auth_user_id']],
    }).json()
    
    requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[2]['auth_user_id'], user[1]['auth_user_id']],
    }).json()

    curr_time = datetime.now()
    time_change = timedelta(seconds=2)
    time_sent = (curr_time + time_change).timestamp()

    requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[1]['auth_user_id']],
    }).json()

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user[1]['token'],
        'dm_id': dm['dm_id'] + 2,
        'message':'Hello',
        'time_sent': time_sent
    })
    assert resp.status_code == 200


def test_user_not_in_dm(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[2]['auth_user_id']],
    }).json()

    curr_time = datetime.now()
    time_change = timedelta(seconds=1)
    time_sent = (curr_time + time_change).timestamp()

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user[1]['token'],
        'dm_id': dm['dm_id'],
        'message':'Hello',
        'time_sent': time_sent
    })
    sleep(1)
    assert resp.status_code == 403