# import pytest
# import requests
# import datetime
# from time import sleep
# from src import config
# OK = 200
# ACCESS_ERROR = 403

# '''
# Changes to data store
#     - general
#         - num_users_who_have_joined_at_least_one_channel_or_dm
#     - user 
#         - stats: {
#             channels_joined
#             dms_joined
#             messages_sent
#         }
#         - dont store involvement rate
#         - calculate it when we need it so we dont need to update it constantly
# Changes to other functions
#     - DONE initialise new data
#         - auth_register 
#     - clear 
#         - num_users_who_have_joined_at_least_one_channel_or_dm
#     - update user stats:
#         - channels_joined, num_users_who_have_joined_at_least_one_channel_or_dm:
#             - DONE channels/create + 1          
#             - DONE channel/join    + 1
#             - DONE channel/leave   - 1
#             - DONE channel/invite  + 1
#         - dms_joined, num_users_who_have_joined_at_least_one_channel_or_dm
#             - DONE dm/create       + 1
#             - DONE dm/leave        - 1
#             - DONE dm/remove       - 1
#         - messages_sent
#             - DONE message/send/v1           + 1
#             - DONE message/senddm/v1         + 1
#             - DONE message/send_later/v1     + 1
#             - DONE message/sendlaterdm/v1    + 1
#             - standup/send/v1 ????      + 1
#             - message/share             + 1
# '''

# @pytest.fixture
# def clear():
#     requests.delete(config.url + 'clear/v1')

# @pytest.fixture
# def user1():
#     resp = requests.post(config.url + 'auth/register/v2', json = 
#                          {'email': 'user1@gmail.com', 'password': 'password', 
#                           'name_first': 'Jayden', 'name_last': 'Huang'})
#     return resp.json()

# @pytest.fixture
# def user2():
#     resp = requests.post(config.url + 'auth/register/v2', json = 
#                          {'email': 'user2@gmail.com', 'password': 'password', 
#                           'name_first': 'Codey', 'name_last': 'Suh'})
#     return resp.json()

# # def test_invalid_token(clear, user1):
# #     resp = requests.get(config.url + 'user/stats/v1', params={'token': '-1'})
# #     assert resp.status_code == ACCESS_ERROR

# # def test_channels_joined(clear, user1, user2):
# #     # test channels/create/v2
# #     # user1 creates channel
# #     requests.post(config.url + 'channels/create/v2', json = {'token': user1['token'], 'name': 'Channel Name', 'is_public': True})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     channels_joined = stats_resp.json()['user_stats']['channels_joined']
# #     assert len(channels_joined) == 2
# #     assert channels_joined[-1]['num_channels_joined'] == 1

# #     # test channel/join/v2
# #     # user2 creates channel which user1 joins
# #     channel_id = requests.post(config.url + 'channels/create/v2', json = {'token': user2['token'], 'name': 'Channel Name', 'is_public': True}).json()['channel_id']
# #     requests.post(config.url + 'channel/join/v2', json = {'token': user1['token'], 'channel_id': channel_id})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     channels_joined = stats_resp.json()['user_stats']['channels_joined']
# #     assert len(channels_joined) == 3
# #     assert channels_joined[-1]['num_channels_joined'] == 2
    
# #     # test channel/leave/v1
# #     # user1 leaves user2's channel
# #     requests.post(config.url + 'channel/leave/v1', json={'token': user1['token'], 'channel_id': channel_id})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     channels_joined = stats_resp.json()['user_stats']['channels_joined']
# #     assert len(channels_joined) == 4
# #     assert channels_joined[-1]['num_channels_joined'] == 1

# #     # test channel/invite/v2
# #     # user2 invites user1 back into their channel
# #     requests.post(config.url + 'channel/invite/v2', json={'token': user2['token'], 'channel_id': channel_id, 'u_id': user1['auth_user_id']})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     channels_joined = stats_resp.json()['user_stats']['channels_joined']
# #     assert len(channels_joined) == 5
# #     assert channels_joined[-1]['num_channels_joined'] == 2

# # def test_dms_joined(clear, user1, user2):
# #     # test dm/create/v1
# #     # user1 creates dm with user2
# #     dm_id = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     dms_joined = stats_resp.json()['user_stats']['dms_joined']
# #     assert len(dms_joined) == 2
# #     assert dms_joined[-1]['num_dms_joined'] == 1

# #     # test dm/remove/v1
# #     # remove dm
# #     requests.delete(config.url + 'dm/remove/v1', json={'token': user1['token'], 'dm_id': dm_id})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     dms_joined = stats_resp.json()['user_stats']['dms_joined']
# #     assert len(dms_joined) == 3
# #     assert dms_joined[-1]['num_dms_joined'] == 0

# #     # test dm/leave/v1
# #     # user1 creates dm with user2
# #     # user1 leaves
# #     dm_id = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
# #     requests.post(config.url + 'dm/leave/v1', json={'token': user1['token'], 'dm_id': dm_id})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     dms_joined = stats_resp.json()['user_stats']['dms_joined']
# #     assert len(dms_joined) == 5
# #     assert dms_joined[-1]['num_dms_joined'] == 0

# def test_messages_sent(clear, user1, user2):
#     # test message/send
#     channel_id = requests.post(config.url + 'channels/create/v2', json = {'token': user1['token'], 'name': 'Channel Name', 'is_public': True}).json()['channel_id']
#     message_id = requests.post(config.url + 'message/send/v1', json = {'token': user1['token'], 'channel_id': channel_id, 'message': 'hi'}).json()['message_id']
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 2
#     assert messages_sent[-1]['num_messages_sent'] == 1

#     # test message/sendlater
#     time = datetime.datetime.now().timestamp()
#     requests.post(config.url + 'message/sendlater/v1', json = {'token': user1['token'], 'channel_id': channel_id, 'message': 'hi', 'time_sent': time + 2})
#     sleep(2.5)
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 3
#     assert messages_sent[-1]['num_messages_sent'] == 2

#     # test message/senddm
#     dm_id = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
#     requests.post(config.url + 'message/senddm/v1', json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 4
#     assert messages_sent[-1]['num_messages_sent'] == 3

#     # test message/sendlaterdm
#     time = datetime.datetime.now().timestamp()
#     requests.post(config.url + 'message/sendlaterdm/v1', json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hi', 'time_sent': time + 2})
#     sleep(2.5)
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 5
#     assert messages_sent[-1]['num_messages_sent'] == 4  

#     # test message/share
#     # for channel
#     requests.post(config.url + 'message/share/v1', json={'token': user1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': channel_id, 'dm_id': -1})
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 6
#     assert messages_sent[-1]['num_messages_sent'] == 5

#     # for dm  
#     requests.post(config.url + 'message/share/v1', json={'token': user1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': -1, 'dm_id': dm_id})
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 7
#     assert messages_sent[-1]['num_messages_sent'] == 6

#     # test standup/send
#     requests.post(config.url + 'standup/start/v1', json={'token': user1['token'], 'channel_id': channel_id, 'length': 2})
#     requests.post(config.url + 'standup/send/v1', json={'token': user1['token'], 'channel_id': channel_id, 'message': 'hi'})
#     sleep(2.5)
#     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
#     messages_sent = stats_resp.json()['user_stats']['messages_sent']
#     assert len(messages_sent) == 8
#     assert messages_sent[-1]['num_messages_sent'] == 7


# # def test_involvement_rate_1(clear, user1, user2):
# #     # test involvement_rate == 1

# #     # user1 creates channel and dm
# #     # sends message in both
# #     channel_id = requests.post(config.url + 'channels/create/v2', json = {'token': user1['token'], 'name': 'Channel Name', 'is_public': True}).json()['channel_id']
# #     requests.post(config.url + 'message/send/v1', json = {'token': user1['token'], 'channel_id': channel_id, 'message': 'hi'})
# #     dm_id = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
# #     requests.post(config.url + 'message/senddm/v1', json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     involvement_rate = stats_resp.json()['user_stats']['involvement_rate']
# #     assert involvement_rate == 1

# # def test_involvement_rate_0(clear, user1, user2):
# #     # test involvement_rate == 0

# #     # numerator and denominator is 0
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     involvement_rate = stats_resp.json()['user_stats']['involvement_rate']
# #     assert involvement_rate == 0

# #     # numerator is 0
# #     # user2 creates channel and dm
# #     # sends message in both
# #     channel_id = requests.post(config.url + 'channels/create/v2', json = {'token': user2['token'], 'name': 'Channel Name', 'is_public': True}).json()['channel_id']
# #     requests.post(config.url + 'message/send/v1', json = {'token': user2['token'], 'channel_id': channel_id, 'message': 'hi'})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     involvement_rate = stats_resp.json()['user_stats']['involvement_rate']
# #     assert involvement_rate == 0

# #     # denominator is 0
# #     # user1 creates dm, sends a message and deletes dm
# #     requests.delete(config.url + 'clear/v1')
# #     user1 = requests.post(config.url + 'auth/register/v2', json = 
# #                     {'email': 'user1@gmail.com', 'password': 'password', 
# #                     'name_first': 'Jayden', 'name_last': 'Huang'}).json()
# #     user2 = requests.post(config.url + 'auth/register/v2', json = 
# #                     {'email': 'user2@gmail.com', 'password': 'password', 
# #                     'name_first': 'Codey', 'name_last': 'Suh'}).json()
# #     dm_id = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
# #     requests.post(config.url + 'message/senddm/v1', json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
# #     requests.delete(config.url + 'dm/remove/v1', json={'token': user1['token'], 'dm_id': dm_id})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     involvement_rate = stats_resp.json()['user_stats']['involvement_rate']
# #     assert involvement_rate == 0

# # def test_involvement_rate_over_1(clear, user1, user2):
# #     # test involvement_rate capped at 1
# #     # user1 creates channel and dm
# #     # sends message in both
# #     # dm is deleted
# #     channel_id = requests.post(config.url + 'channels/create/v2', json = {'token': user1['token'], 'name': 'Channel Name', 'is_public': True}).json()['channel_id']
# #     requests.post(config.url + 'message/send/v1', json = {'token': user1['token'], 'channel_id': channel_id, 'message': 'hi'})
# #     dm_id = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
# #     resp = requests.post(config.url + 'message/senddm/v1', json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
# #     assert resp.status_code == 200
# #     requests.delete(config.url + 'dm/remove/v1', json={'token': user1['token'], 'dm_id': dm_id})
# #     stats_resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     involvement_rate = stats_resp.json()['user_stats']['involvement_rate']
# #     assert involvement_rate == 1

# # def test_initial_datapoint(clear):
# #     # metrics 0 at time when user is created
# #     time = datetime.datetime.now().timestamp()
# #     user_token = requests.post(config.url + 'auth/register/v2', json = 
# #                          {'email': 'user1@gmail.com', 'password': 'password', 
# #                           'name_first': 'Jayden', 'name_last': 'Huang'}).json()['token']
# #     stats = requests.get(config.url + 'user/stats/v1', params={'token': user_token}).json()['user_stats']
# #     assert stats['channels_joined'][0]['num_channels_joined'] == 0
# #     assert abs(stats['channels_joined'][0]['time_stamp'] - time) < 2
# #     assert stats['dms_joined'][0]['num_dms_joined'] == 0
# #     assert abs(stats['dms_joined'][0]['time_stamp'] - time) < 2
# #     assert stats['messages_sent'][0]['num_messages_sent'] == 0
# #     assert abs(stats['messages_sent'][0]['time_stamp'] - time) < 2
# #     assert stats['involvement_rate'] == 0

# # def test_return_type(clear, user1):
# #     resp = requests.get(config.url + 'user/stats/v1', params={'token': user1['token']})
# #     stats = resp.json()
# #     assert 'user_stats' in stats
# #     assert 'channels_joined' in stats['user_stats']
# #     assert type(stats['user_stats']['channels_joined']) == list
# #     assert 'dms_joined' in stats['user_stats']
# #     assert type(stats['user_stats']['dms_joined']) == list
# #     assert 'messages_sent' in stats['user_stats']
# #     assert type(stats['user_stats']['messages_sent']) == list
# #     assert 'involvement_rate' in stats['user_stats']
# #     assert type(stats['user_stats']['involvement_rate']) == float