import json
import pytest
from src.user import user_profile_uploadphoto_v1, user_profile_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from tests.auth_http_test import clear_and_register_multiple_users
import requests
from src import config

INPUT_ERROR = 400
ACCESS_ERROR = 403

def test_invalid_token():
    # clear_v1()    
    # auth_register_v1('firstemail@gmail.com', 'password', 'comp', 'student')
    # with pytest.raises(AccessError):
    #     user_profile_uploadphoto_v1('abcdef', 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',0,0,200,200)
    requests.delete(config.url + '/clear/v1', json={})
    requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()
    
    user_photoupload = requests.post(config.url + '/user/profile/uploadphoto/v1', json= {
        'token' : '1234',
        'img_url' : 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',
        'x_start' : 0,
        'y_start' : 0,
        'x_end' : 0,
        'y_end' : 0
    })
    assert user_photoupload.status_code == ACCESS_ERROR
    
def test_crop_error():
    requests.delete(config.url + '/clear/v1', json={})
    result1 = requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()
    # with pytest.raises(InputError):
    #     user_profile_uploadphoto_v1(result1['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',-1,0,200,200)
    # with pytest.raises(InputError):
    #     user_profile_uploadphoto_v1(result1['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',0,-1,200,200)
    # with pytest.raises(InputError):
    #     user_profile_uploadphoto_v1(result1['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',0,0,100000,200)
    # with pytest.raises(InputError):
    #     user_profile_uploadphoto_v1(result1['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',-1,0,100000,100000)
    user_photoupload = requests.post(config.url + '/user/profile/uploadphoto/v1', json = {
        'token' : result1['token'],
        'img_url' : 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',
        'x_start' : -1,
        'y_start' : 0,
        'x_end' : 200,
        'y_end' : 200
    })
    
    assert user_photoupload.status_code == INPUT_ERROR
    
    
def test_not_jpg():
    requests.delete(config.url + '/clear/v1', json={})
    result1 = requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()
    # with pytest.raises(InputError):
    #     user_profile_uploadphoto_v1(result1['token'], 'http://i.imgur.com/sd3tV.gif',0,0,200,200)
    user_photoupload =  requests.post(config.url + '/user/profile/uploadphoto/v1', json= {
        'token' : result1['token'],
        'img_url' : 'http://i.imgur.com/sd3tV.gif',
        'x_start' : 0,
        'y_start' : 0,
        'x_end' : 200,
        'y_end' : 200
    })
    assert user_photoupload.status_code == INPUT_ERROR

def test_invalid_url():
    requests.delete(config.url + '/clear/v1', json={})
    result1 = requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()
    # with pytest.raises(InputError):
    #     user_profile_uploadphoto_v1(result1['token'], 'abcdef',0,0,200,200)
    user_photoupload =  requests.post(config.url + '/user/profile/uploadphoto/v1', json = {
        'token' : result1['token'],
        'img_url' : 'abcde',
        'x_start' : 0,
        'y_start' : 0,
        'x_end' : 200,
        'y_end' : 200
    })
    assert user_photoupload.status_code == INPUT_ERROR
    
    
def test_simple():
    requests.delete(config.url + '/clear/v1', json={})   
    result1 = requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()
    
    # user_profile_uploadphoto_v1(result1['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',0,0,860,573)
    requests.post(config.url + '/user/profile/uploadphoto/v1', json = {
        'token' : result1['token'],
        'img_url' : 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',
        'x_start' : 0,
        'y_start' : 0,
        'x_end' : 860,
        'y_end' : 573
    })
    user1 = requests.get(config.url + '/user/profile/v1', params={
        'token' : result1['token'], 
        'u_id' : result1['auth_user_id']
    }).json()
    result2 = requests.post(config.url + '/auth/register/v2', json={ 
        'email' : 'example2@mail.com', 
        'password' : '123466666',
        'name_first' : 'one',
        'name_last' : 'two'
    }).json()
    user2 = requests.get(config.url + '/user/profile/v1', params={
        'token' : result2['token'], 
        'u_id' : result2['auth_user_id']
    }).json()
    assert user1['user']['profile_img_url'] != user2['user']['profile_img_url']

# def test_multiple():
#     clear_v1()    
#     result1 = auth_register_v1('firstemail@gmail.com', 'password', 'comp', 'student')
#     result2 = auth_register_v1('secondemail@gmail.com', 'password', 'comp', 'student')
#     user1 = user_profile_v1(result1['token'], result1['auth_user_id'])
#     user2 = user_profile_v1(result1['token'], result2['auth_user_id'])
#     user_profile_uploadphoto_v1(result1['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',0,0,860,573)
#     user_profile_uploadphoto_v1(result2['token'], 'http://img.lovepik.com/photo/50073/2736.jpg_wh860.jpg',0,0,860,573)
#     user2 = user_profile_v1(result1['token'], result1['auth_user_id'])
#     assert user1['user']['profile_img_url'] != user2['user']['profile_img_url']
#     clear_v1()