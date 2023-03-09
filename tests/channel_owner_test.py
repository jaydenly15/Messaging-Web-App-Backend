from os import remove
import pytest

import json
import urllib
import requests
from src.channel import channel_addowner
from src import config
import pytest

NUM_USERS = 10

# Registers multiple users at once and adds them to servers
@pytest.fixture()
def create_input():
   requests.delete(config.url + '/clear/v1', json={})
   
   users = []

   global NUM_USERS
   for i in range(NUM_USERS):
      resp = requests.post(config.url + '/auth/register/v2', json={
         'email': 'Group_camel' + str(i) + '@gmail.com',
         'password': 'camel_hump123',
         'name_first': 'Simon',
         'name_last': 'Camel'
      })
      users.append(resp.json())
   
   channels = []

   channel_pub = requests.post(config.url + '/channels/create/v2', json={
      'token': users[0]['token'],
      'name': 'camel',
      'is_public': True
   }).json()
   channels.append(channel_pub)

   requests.post(config.url + '/channel/join/v2', json={
      'token': users[1]['token'],
      'channel_id': channel_pub['channel_id']
   })

   requests.post(config.url + '/channel/join/v2', json={
      'token': users[2]['token'],
      'channel_id': channel_pub['channel_id']
   })

   channel_priv = requests.post(config.url + '/channels/create/v2', json={
       'token': users[1]['token'],
       'name': 'llama',
       'is_public': False
   }).json()
   channels.append(channel_priv)

   requests.post(config.url + '/channel/invite/v2', json={
       'token': users[1]['token'],
       'channel_id': channel_priv['channel_id'],
       'u_id': users[2]['auth_user_id']
   })

   requests.post(config.url + '/channel/invite/v2', json={
       'token': users[1]['token'],
       'channel_id': channel_priv['channel_id'],
       'u_id': users[3]['auth_user_id']
   })

   return [users, channels]

def test_add_and_remove_owner_pub(create_input):
   user, c_id = create_input

   requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })

   details = requests.get(config.url + '/channel/details/v2', params={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id']
   }).json()

   assert details['owner_members'] ==  [{
                                          'u_id': user[0]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel0@gmail.com',
                                          'handle_str': 'simoncamel', 
                                       },
                                       {
                                          'u_id': user[1]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel1@gmail.com',
                                          'handle_str': 'simoncamel0', 
                                       }]

   requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   }).json()

   remove = requests.get(config.url + '/channel/details/v2', params={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id']
   }).json()

   assert remove['owner_members'] ==  [{
                                          'u_id': user[0]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel0@gmail.com',
                                          'handle_str': 'simoncamel', 
                                       }]

def test_add_and_remove_owner_priv(create_input):
   user, c_id = create_input

   requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[1]['channel_id'],
      'u_id': user[2]['auth_user_id']
   })

   details = requests.get(config.url + '/channel/details/v2', params={
      'token': user[1]['token'],
      'channel_id': c_id[1]['channel_id']
   }).json()

   assert details['owner_members'] ==  [{
                                          'u_id': user[1]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel1@gmail.com',
                                          'handle_str': 'simoncamel0', 
                                       },
                                       {
                                          'u_id': user[2]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel2@gmail.com',
                                          'handle_str': 'simoncamel1', 
                                       }]

   requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[1]['channel_id'],
      'u_id': user[2]['auth_user_id']
   }).json()

   remove = requests.get(config.url + '/channel/details/v2', params={
      'token': user[1]['token'],
      'channel_id': c_id[1]['channel_id']
   }).json()

   assert remove['owner_members'] ==  [{
                                          'u_id': user[1]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel1@gmail.com',
                                          'handle_str': 'simoncamel0', 
                                       }]
   resp = requests.post(config.url + 'channel/addowner/v1', json={
      'token' : user[0]['token'], 
      'channel_id' : c_id[1]['channel_id'],
      'u_id' : user[2]['auth_user_id']
   })
   assert resp.status_code == 403

   resp_2 = requests.post(config.url + 'channel/removeowner/v1', json={
      'token' : user[0]['token'], 
      'channel_id' : c_id[1]['channel_id'],
      'u_id' : user[2]['auth_user_id']
   })
   assert resp_2.status_code == 403

def test_remove_self(create_input):
   user, c_id = create_input

   requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })

   requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[0]['auth_user_id']
   }).json()

   remove = requests.get(config.url + '/channel/details/v2', params={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id']
   }).json()

   assert remove['owner_members'] ==  [{
                                          'u_id': user[1]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel1@gmail.com',
                                          'handle_str': 'simoncamel0', 
                                       }]

def test_global_owner(create_input):
   user, c_id = create_input

   requests.post(config.url + '/channel/join/v2', json={
      'token': user[0]['token'],
      'channel_id': c_id[1]['channel_id']
   })

   details = requests.get(config.url + '/channel/details/v2', params={
      'token': user[1]['token'],
      'channel_id': c_id[1]['channel_id']
   }).json()

   assert details['all_members'] ==    [{
                                          'u_id': user[1]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel1@gmail.com',
                                          'handle_str': 'simoncamel0', 
                                       },
                                       {
                                          'u_id': user[2]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel2@gmail.com',
                                          'handle_str': 'simoncamel1'
                                       },
                                       {
                                          'u_id': user[3]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel3@gmail.com',
                                          'handle_str': 'simoncamel2'
                                       },
                                       {
                                          'u_id': user[0]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel0@gmail.com',
                                          'handle_str': 'simoncamel'
                                       }]

   requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[1]['channel_id'],
      'u_id': user[0]['auth_user_id']
   })   

   owner_details = requests.get(config.url + '/channel/details/v2', params={
      'token': user[0]['token'],
      'channel_id': c_id[1]['channel_id']
   }).json()

   assert owner_details['owner_members'] ==  [{
                                                'u_id': user[1]['auth_user_id'],     
                                                'name_first': 'Simon',
                                                'name_last': 'Camel',
                                                'email': 'Group_camel1@gmail.com',
                                                'handle_str': 'simoncamel0', 
                                             },
                                             {
                                                'u_id': user[0]['auth_user_id'],     
                                                'name_first': 'Simon',
                                                'name_last': 'Camel',
                                                'email': 'Group_camel0@gmail.com',
                                                'handle_str': 'simoncamel'  
                                             }]


def test_invalid_channel(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'] + 100,
      'u_id': user[1]['auth_user_id']
   })
   assert resp.status_code == 400

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'] + 100,
      'u_id': user[1]['auth_user_id']
   })    
   assert remove.status_code == 400

def test_invalid_user(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id'] + 11
   })    
   assert resp.status_code == 400

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id'] + 11
   })    
   assert remove.status_code == 400

def test_user_not_in_channel(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[3]['auth_user_id']
   })    
   assert resp.status_code == 400

def test_user_not_owner(create_input):
   user, c_id = create_input

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })    
   assert remove.status_code == 400

def test_user_already_owner(create_input):
   user, c_id = create_input

   requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })    

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })  
   assert resp.status_code == 400

def test_user_already_removed(create_input):
   user, c_id = create_input

   requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })    

   requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   }) 

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id']
   })    
   assert remove.status_code == 400

def test_user_only_owner(create_input):
   user, c_id = create_input  

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[0]['auth_user_id']
   })  
   assert remove.status_code == 400
   
   details = requests.get(config.url + '/channel/details/v2', params={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id']
   }).json()
   assert details['owner_members'] ==  [{
                                          'u_id': user[0]['auth_user_id'],     
                                          'name_first': 'Simon',
                                          'name_last': 'Camel',
                                          'email': 'Group_camel0@gmail.com',
                                          'handle_str': 'simoncamel', 
                                       }]

def test_user_no_perm(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[2]['auth_user_id']
   })  
   assert resp.status_code == 403

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[0]['auth_user_id']
   })  
   assert remove.status_code == 403

def test_invalid_u_id(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[2]['auth_user_id'] + 100
   })  
   assert resp.status_code == 400

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[0]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[2]['auth_user_id'] + 100
   })
   assert remove.status_code == 400

def test_no_perms_invalid_user(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id'] + 11
   })  
   assert resp.status_code == 403

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[1]['auth_user_id'] + 11
   })
   assert remove.status_code == 403

def test_no_perms_user_not_in_channel(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[5]['auth_user_id']
   })  
   assert resp.status_code == 403

   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[5]['auth_user_id']
   })
   assert remove.status_code == 403

def test_no_perms_already_owner(create_input):
   user, c_id = create_input

   resp = requests.post(config.url + '/channel/addowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[0]['auth_user_id']
   })  
   assert resp.status_code == 403

def test_not_owner_no_perms(create_input):
   user, c_id = create_input
   
   remove = requests.post(config.url + '/channel/removeowner/v1', json={
      'token': user[1]['token'],
      'channel_id': c_id[0]['channel_id'],
      'u_id': user[2]['auth_user_id']
   })
   assert remove.status_code == 403

   
