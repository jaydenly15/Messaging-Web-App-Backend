import hypothesis
import pytest
import json
import urllib
import requests
from requests.api import get
from src import config
import string
import time

from hypothesis import given, strategies, settings, Verbosity
from src.auth import auth_password_reset_request_v1

def User(email, password, name_first, name_last):
    resp = requests.post(config.url + 'auth/register/v2', json={
            'email': email,
            'password': password,
            'name_first': name_first,
            'name_last': name_last
    }).json()

    return resp['auth_user_id'], resp['token']

def reset_password_request(email):
    resp = requests.post(config.url + 'auth/passwordreset/request/v1', json={
            'email': email
    })
    return resp.status_code

def reset_password(reset_code, new_password):
    resp = requests.post(config.url + 'auth/passwordreset/reset/v1', json={
            'reset_code': reset_code,
            'new_password': new_password
    })
    return resp.status_code

@given(strategies.from_regex(regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'))
@settings(verbosity=Verbosity.verbose, deadline=None, max_examples=5)
def test_password_reset_invalid_email(email):
    requests.delete(config.url + 'clear/v1', json={})
    # Registers user
    User(email, 'password', 'Simon', 'Camel')
    # Attempt to reset password, passing in invalid email
    assert reset_password_request(email + '!') == 200

def test_password_reset_logged_out():
    requests.delete(config.url + 'clear/v1', json={})
    # Registers user
    email = 'testemail123@gmail.com'
    password = 'password'
    _, auth_token = User(email, password, 'Simon', 'Camel')
    
    # User logs in on different device
    resp = requests.post(config.url + 'auth/login/v2', json={
        'email': email,
        'password': password,
    })
    assert resp.status_code == 200
    # Gets token from login
    login_token = resp.json()['token']

    # Submits reset password request
    assert reset_password_request(email) == 200

    # Tokens associated with user should now be invalid
    resp = requests.post(config.url + '/auth/logout/v1', json={
        'token': auth_token
    })
    assert resp.status_code == 403

    resp = requests.post(config.url + '/auth/logout/v1', json={
        'token': login_token
    })
    assert resp.status_code == 403

@given(strategies.text(alphabet=string.ascii_letters, max_size=9))
@settings(verbosity=Verbosity.verbose, deadline=None, max_examples=5)
def test_password_reset_invalid_reset_code(invalid_code):
    requests.delete(config.url + 'clear/v1', json={})
    email = "groupcamel123@gmail.com"
    User(email, 'password', 'Simon', 'Camel')
    assert reset_password_request(email) == 200
    # Reset code always has length 10, so any string with len <10 
    # is guaranteed to be invalid
    assert reset_password(invalid_code,'valid_password') == 400

# Password is guaranteed to be invalid since less than 6 characters
@given(strategies.text(alphabet=string.ascii_letters, max_size=5))
@settings(verbosity=Verbosity.verbose, deadline=None, max_examples=5)
def test_password_reset_invalid_password(invalid_password):
    requests.delete(config.url + 'clear/v1', json={})
    email = 'testemail123@gmail.com'
    User(email, 'password', 'Simon', 'Camel')
    time.sleep(0.25)
    # Whitebox test to test functionality of reset
    reset_token = auth_password_reset_request_v1(email)
    time.sleep(0.25)
    # Fails since password too short
    assert reset_password(reset_token, invalid_password) == 400
    # Password succesfully reset
    assert reset_password(reset_token, 'new_password') == 200
    
    # Checks that new password works
    resp = requests.post(config.url + 'auth/login/v2', json={
        'email': email,
        'password': 'new_password',
    })
    assert resp.status_code == 200

    # Checks that old password fails
    resp = requests.post(config.url + 'auth/login/v2', json={
        'email': email,
        'password': 'password',
    })
    assert resp.status_code == 400