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

from tests.admin_reset_password_test import User
from tests.message_send_test import register_user_create_channel
from hypothesis import given, strategies, settings, Verbosity

ACCESS_ERROR = 403
INPUT_ERROR = 400
OK = 200

def join_channel(token, channel_id):
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': token,
        'channel_id': channel_id
    }).json()
    return resp

def view_channel_messages(token, channel_id, start):
    print('Checking value and type of start', start, type(start))
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': token,
        'channel_id': channel_id,
        'start': start
    }).json()
    return resp

def create_channel(token, name, is_public):
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': token,
        'name': name,
        'is_public': is_public
    }).json()
    return resp['channel_id']

def send_message_later(token, channel_id, message, time_sent):
    resp = requests.post(config.url + 'message/sendlater/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent
    })
    return resp

# Generates timestamps that have already passed
@given(strategies.datetimes(min_value=datetime(1971, 1, 1), max_value=datetime.now() - timedelta(seconds=1)))
def test_sendlater_invalid_time(invalid_datetime):
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    channel_id = create_channel(token, 'Test Channel', True)
    invalid_timestamp = invalid_datetime.timestamp()
    resp = send_message_later(token, channel_id, 'Test message', invalid_timestamp)
    assert resp.status_code == INPUT_ERROR

# Generates valid future timestamps, offset at least 0.1 seconds from current time
@given(strategies.datetimes(min_value=datetime.now() + timedelta(seconds=0.1), \
    max_value=datetime.now() + timedelta(seconds=1)))
def test_invalid_channel(time_sent):
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    channel_id = create_channel(token, 'Test Channel', True)

    # Produces error because of invalid channel ID
    resp = send_message_later(token, channel_id + 1, 'Example message', time_sent.timestamp())
    assert resp.status_code == INPUT_ERROR

@given(strategies.text(min_size=1001))
@settings(verbosity=Verbosity.verbose, max_examples=3)
def test_channel_message_too_long(long_message):
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    channel_id = create_channel(token, 'Test Channel', True)

    # Calculates the time 1 second before current time
    curr_time = datetime.now()
    time_change = timedelta(seconds=1)
    timestamp = (curr_time + time_change).timestamp()

    resp = send_message_later(token, channel_id, long_message, timestamp)
    assert resp.status_code == INPUT_ERROR

def test_message_send_later_basic():
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    channel_id = create_channel(token, 'Test Channel', True)

    # Calculates the time 1 second after now
    curr_time = datetime.now()
    print(curr_time.timestamp())
    time_change = timedelta(seconds=1)
    time_sent = (curr_time + time_change).timestamp()

    resp = send_message_later(token, channel_id, 'Test message', time_sent)
    assert resp.status_code == OK

    messages = view_channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 0

    sleep(0.1)

    messages = view_channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 0

    sleep(0.9)

    messages = view_channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 1


def test_threading():
    requests.delete(config.url + 'clear/v1', json={})
    _, token = User('groupcamel123@gmail.com', 'password', 'Group', 'Camel')
    channel_id = create_channel(token, 'Test Channel', True)

    # Calculates the time 1 second after now
    curr_time = datetime.now()
    time_change = timedelta(seconds=100)
    time_sent = (curr_time + time_change).timestamp()

    send_message_later(token, channel_id, 'Test message', time_sent)

    messages = view_channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 0

    sleep(1)

    messages = view_channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 0

    sleep(1)

    User('groupcamel1234@gmail.com', 'password', 'Group', 'Camel')

    