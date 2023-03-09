import requests
import pytest
from src import config
from tests.channel_invite_http_test import clear_and_register_multiple_users
from src.notification import search_tags
from datetime import datetime, timedelta
from time import sleep

@pytest.fixture()
def create_input_pub_channel(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    # Setup for message in public channel
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_pub',
        'is_public': True
    }).json()

    requests.post(config.url + '/channel/join/v2', json={
        'token': user[1]['token'],
        'channel_id': channel['channel_id']
    })

    requests.post(config.url + '/channel/invite/v2', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id'],
        'u_id': user[2]['auth_user_id'] 
    })

    requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello @jaydenly'
    })

    return (user, channel)

@pytest.fixture()
def create_input_priv_channel(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    # Setup for message in public channel
    channel = requests.post(config.url + '/channels/create/v2', json={
        'token': user[0]['token'],
        'name': 'channel_priv',
        'is_public': False
    }).json()

    requests.post(config.url + '/channel/invite/v2', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id'],
        'u_id': user[1]['auth_user_id'] 
    })

    requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello @jaydenly'
    })

    return (user, channel)

@pytest.fixture()
def create_input_dm(clear_and_register_multiple_users):
    user = clear_and_register_multiple_users

    # Setup for message in dm
    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': user[0]['token'],
        'u_ids': [user[2]['auth_user_id']],
    }).json()

    requests.post(config.url + 'message/senddm/v1', json={
        'token': user[2]['token'],
        'dm_id': dm['dm_id'],
        'message':'Hello @ruosongpan'
    })

    return (user, dm)

def test_noti_channel_tag(create_input_pub_channel):
    user, c_id = create_input_pub_channel

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[1]['token']
    }).json()['notifications']

    assert notification[0]['channel_id'] == c_id['channel_id']
    assert notification[0]['dm_id'] == -1
    assert notification[0]['notification_message'] == 'ruosongpan tagged you in channel_pub: Hello @jaydenly'

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[2]['token']
    }).json()['notifications']

    assert len(notification) == 1
    assert notification[0]['notification_message'] == "ruosongpan added you to channel_pub"

def test_noti_multiple_tag(create_input_pub_channel):
    user, c_id = create_input_pub_channel

    requests.post(config.url + '/message/send/v1', json={
        'token': user[1]['token'],
        'channel_id': c_id['channel_id'],
        'message': '@ruosongpan @ruosongpan @ruosongpan @ruosongpan @ruosongpan @ruosongpan'
    })

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[0]['token']
    }).json()['notifications']

    assert len(notification) == 1
    assert notification[0]['notification_message'] == 'jaydenly tagged you in channel_pub: @ruosongpan @ruosong'

def test_noti_message_edit_over_20_char(create_input_pub_channel):
    user, c_id = create_input_pub_channel

    message = requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': c_id['channel_id'],
        'message': 'I am very cool'
    }).json()

    requests.put(config.url + "/message/edit/v1", json = {
        'token': user[0]['token'],
        'message_id': message['message_id'],
        'message': "This will be a message over 20 characters @jaydenly",
    })

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[1]['token']
    }).json()['notifications']

    assert notification[-1]['notification_message'] == 'ruosongpan tagged you in channel_pub: This will be a messa'

def test_noti_channel_add_pub(create_input_pub_channel):
    user, c_id = create_input_pub_channel

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[2]['token']
    }).json()['notifications']

    assert notification[0]['channel_id'] == c_id['channel_id']
    assert notification[0]['dm_id'] == -1
    assert notification[0]['notification_message'] == 'ruosongpan added you to channel_pub'

def test_noti_channel_add_priv(create_input_priv_channel):
    user, c_id = create_input_priv_channel  
    
    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[1]['token']
    }).json()['notifications']

    assert notification[0]['channel_id'] == c_id['channel_id']
    assert notification[0]['dm_id'] == -1
    assert notification[0]['notification_message'] == 'ruosongpan added you to channel_priv'

def test_noti_react(create_input_pub_channel):
    user, c_id = create_input_pub_channel  

    message = requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': c_id['channel_id'],
        'message': 'react to this message please'
    }).json()
    
    requests.post(config.url + 'message/react/v1', json={
        'token': user[1]['token'],
        'message_id': message['message_id'],
        'react_id': 1
    })

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[0]['token']
    }).json()['notifications']

    assert notification[0]['channel_id'] == c_id['channel_id']
    assert notification[0]['dm_id'] == -1
    assert notification[0]['notification_message'] == 'jaydenly reacted to your message in channel_pub'

def test_noti_capped_20(create_input_pub_channel):
    user, c_id = create_input_pub_channel 

    message = requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': c_id['channel_id'],
        'message': 'react to this message please'
    }).json()
    
    for _ in range(20):
        requests.post(config.url + 'message/react/v1', json={
            'token': user[1]['token'],
            'message_id': message['message_id'],
            'react_id': 1
        })

        requests.post(config.url + 'message/unreact/v1', json={
            'token': user[1]['token'],
            'message_id': message['message_id'],
            'react_id': 1
        })
    
    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[0]['token']
    }).json()['notifications']

    assert len(notification) == 20

def test_noti_dm_tag(create_input_dm):
    user, dm_id = create_input_dm

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[0]['token']
    }).json()['notifications']

    assert notification[0]['channel_id'] == -1
    assert notification[0]['dm_id'] == dm_id['dm_id']
    assert notification[0]['notification_message'] == 'jamesteng tagged you in jamesteng, ruosongpan: Hello @ruosongpan'

def test_noti_add_dm(create_input_dm):
    user, dm_id = create_input_dm

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[2]['token']
    }).json()['notifications']

    assert notification[0]['channel_id'] == -1
    assert notification[0]['dm_id'] == dm_id['dm_id']
    assert notification[0]['notification_message'] == 'ruosongpan added you to jamesteng, ruosongpan'

def test_invalid_token():

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': 'abcdefg'
    })

    assert notification.status_code == 403

def test_noti_react_in_dm(create_input_dm):
    user, dm_id = create_input_dm

    message = requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0]['token'],
        'dm_id': dm_id['dm_id'],
        'message':'Hello :)'
    }).json()

    requests.post(config.url + 'message/react/v1', json={
        'token': user[2]['token'],
        'message_id': message['message_id'],
        'react_id': 1
    })

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[0]['token']
    }).json()['notifications']

    assert notification[-1]['notification_message'] == 'jamesteng reacted to your message in jamesteng, ruosongpan'

def test_multiple_tagging(create_input_pub_channel):
    user, c_id = create_input_pub_channel 

    requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': c_id['channel_id'],
        'message': '@jamesteng123 @jamesteng1 @jaydenly0 @jaydenly @jamesteng'
    }).json()

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[1]['token']
    }).json()['notifications']

    assert len(notification) == 2

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[2]['token']
    }).json()['notifications']

    assert len(notification) == 2

def test_send_later_channel(create_input_pub_channel):
    user, c_id = create_input_pub_channel 

    curr_time = datetime.now()
    time_change = timedelta(seconds=1)
    time_sent = (curr_time + time_change).timestamp()

    requests.post(config.url + 'message/sendlater/v1', json={
        'token': user[0]['token'],
        'channel_id': c_id['channel_id'],
        'message': '@jaydenly later',
        'time_sent': time_sent
    })

    requests.post(config.url + '/message/send/v1', json={
        'token': user[0]['token'],
        'channel_id': c_id['channel_id'],
        'message': '@jaydenly now'
    })

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[1]['token']
    }).json()['notifications']

    assert notification[-1]['notification_message'] == 'ruosongpan tagged you in channel_pub: @jaydenly now'

    sleep(1)

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[1]['token']
    }).json()['notifications']

    assert notification[-1]['notification_message'] == 'ruosongpan tagged you in channel_pub: @jaydenly later'

def test_send_later_dm(create_input_dm):
    user, dm_id = create_input_dm

    curr_time = datetime.now()
    time_change = timedelta(seconds=2)
    time_sent = (curr_time + time_change).timestamp()

    requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user[0]['token'],
        'dm_id': dm_id['dm_id'],
        'message':'@jamesteng later',
        'time_sent': time_sent
    })

    requests.post(config.url + 'message/senddm/v1', json={
        'token': user[0]['token'],
        'dm_id': dm_id['dm_id'],
        'message':'@jamesteng now'
    })

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[2]['token']
    }).json()['notifications']

    assert notification[-1]['notification_message'] == 'ruosongpan tagged you in jamesteng, ruosongpan: @jamesteng now'

    sleep(2)

    notification = requests.get(config.url + 'notifications/get/v1', params={
        'token': user[2]['token']
    }).json()['notifications']

    assert notification[-1]['notification_message'] == 'ruosongpan tagged you in jamesteng, ruosongpan: @jamesteng later'
