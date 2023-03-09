# import pytest
# from src.user import user_stats_v1, users_stats_v1
# from src.auth import auth_register_v1
# from src.channels import channels_create_v1
# from src.channel import channel_invite_v1, channel_join_v1, channel_addowner, channel_leave, channel_removeowner 
# from src.dm import dm_create_v1, dm_leave_v1, dm_remove_v1
# from src.message import message_send_v1, message_senddm_v1, message_remove_v1, message_edit_v1
# from src.other import clear_v1
# from src.error import AccessError, InputError
# import requests
# from src import config

# INPUT_ERROR = 400
# ACCESS_ERROR = 403


# def test_invalid_token():
#     requests.delete(config.url + '/clear/v1', json={})
#     result1 = requests.post(config.url + '/auth/register/v2', json={ 
#         'email' : 'example@mail.com', 
#         'password' : '123466666',
#         'name_first' : 'one',
#         'name_last' : 'two'
#     }).json()  
#     requests.post(config.url + '/auth/register/v2', json={ 
#         'email' : 'example2@mail.com', 
#         'password' : '123466666',
#         'name_first' : 'one',
#         'name_last' : 'two'
#     }).json()
#     requests.post(config.url + '/channels/create/v2', json={
#         'token': result1['token'],
#         'name': 'channel_1',
#         'is_public': True
#     }).json()
#     requests.post(config.url + '/channels/create/v2', json={
#         'token': result1['token'],
#         'name': 'channel_1',
#         'is_public': True
#     }).json()
#     react = requests.get(config.url + '/user/stats/v1', json = {
#         'token' : 'aabbcc'
#     })
#     assert react.status_code == ACCESS_ERROR
    
# def test_channels_create_stat():
#     requests.delete(config.url + '/clear/v1', json={})
#     # result1 = auth_register_v1('firstemail@gmail.com', 'password', 'comp', 'student')
#     user1 = requests.post(config.url + 'auth/register/v2', json={
#         'email': 'Group_camel123@gmail.com',
#         'password': 'camel_hump123',
#         'name_first': 'Simon',
#         'name_last': 'Camel'
#     }).json()
#     # auth_register_v1('secondemail@gmail.com', 'password', 'comp', 'student')
#     user2 = requests.post(config.url + 'auth/register/v2', json={
#         'email': 'Group_camel1234444@gmail.com',
#         'password': 'camel_hump123',
#         'name_first': 'Sim',
#         'name_last': 'Caml'
#     }).json()
#     # channels_create_v1(result1['token'], "The party channel 1", True)
#     channel1 = requests.post(config.url + '/channels/create/v2', json={
#         'token': user1['token'],
#         'name': 'channel_1',
#         'is_public': True
#     }).json()
#     requests.post(config.url + '/channel/invite/v2', json={
#         'token': user1['token'],
#         'channel_id': channel1['channel_id'],
#         'u_id': user2['auth_user_id']
#     }).json()
    
#     # react = user_stats_v1(result1['token'])
#     react = requests.get(config.url + '/user/stats/v1', json = {
#         'token' : user2['token']
#     })
    
#     assert react.status_code == 200
    
# def test_dm_create_stat():
#     requests.delete(config.url + '/clear/v1', json={})
#     user1 = requests.post(config.url + 'auth/register/v2', json={
#         'email': 'Group_camel123@gmail.com',
#         'password': 'camel_hump123',
#         'name_first': 'Simon',
#         'name_last': 'Camel'
#     }).json()
#     # auth_register_v1('secondemail@gmail.com', 'password', 'comp', 'student')
#     user2 = requests.post(config.url + 'auth/register/v2', json={
#         'email': 'Group_camel1234444@gmail.com',
#         'password': 'camel_hump123',
#         'name_first': 'Sim',
#         'name_last': 'Caml'
#     }).json()
#     requests.post(config.url + 'dm/create/v1', json={
#             'token': user1['token'],
#             'u_ids': [user1['auth_user_id'] + user2['auth_user_id']]
#     })
#     requests.post(config.url + '/channels/create/v2', json={
#         'token': user1['token'],
#         'name': 'channel_1',
#         'is_public': True
#     }).json()
    
#     react = requests.get(config.url + '/user/stats/v1', json = {
#         'token' : user2['token']
#     })
    
#     assert react.status_code == 200

    


