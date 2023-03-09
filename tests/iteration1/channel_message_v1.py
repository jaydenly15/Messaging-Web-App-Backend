import pytest

from src.auth import auth_register_v1
from src.channel import channel_messages_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.data_store import data_store

@pytest.fixture
def create_input():
    clear_v1()

    data_test_users = [
        auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan"),
        auth_register_v1("jaydenly@mail.com", "123456", "jayden", "ly"), 
        auth_register_v1("james.teng@mail.com", "123456", "james", "teng"), 
        auth_register_v1("william.sheppard@mail.com", "123456", "william", "sheppard"), 
        auth_register_v1("eric.cai@mail.com", "123456", "eric", "cai")
    ]

    data_test_channels = [channels_create_v1(data_test_users[0]["auth_user_id"], "First Channel", True),
        channels_create_v1(data_test_users[1]["auth_user_id"], "Second Channel", True),
        channels_create_v1(data_test_users[2]["auth_user_id"], "Third Channel", False),
    ]

    dict_return = {
            'messages':[
                    {
                        'message_id':1,
                        'u_id':26,
                        'message':"hello world",
                        'time_created':1616126327
                    },
                    {
                        'message_id':2,
                        'u_id':42,
                        'message':"goodbye world",
                        'time_created':1616126390
                    }
                ]
        }

    data = data_store.get()
    for channel in data['channels']:
        if 1 == channel['id']:
            channel['messages'] = dict_return['messages']
            # for messages in dict_return['messages']:
            #     channel['messages'].append(messages)
        break
    data_store.set(data)
    #for i in range(0, 120):
        #message_send?(data_test_users[0]["auth_user_id"], data_test_channels[0]["channel_id"], f"This is message {i}.")
        
    '''There is now no function which can do the message sending thing so I will just comment those two lines out.'''

    return [data_test_users, data_test_channels]


def test_invalid_member(create_input):
    
    '''user_is is not a member of the channel'''
    with pytest.raises(AccessError):
        channel_messages_v1(create_input[0][2]["auth_user_id"], create_input[1][0]["channel_id"], 0)

def test_invalid_channel_id(create_input):
  
    '''invalid channel_id'''
    with pytest.raises(InputError):
        channel_messages_v1(create_input[0][0]["auth_user_id"], 5, 0)

def test_invalid_auth_user_id(create_input):
    
    '''invalid user_id'''
    with pytest.raises(AccessError):
        channel_messages_v1(7, create_input[1][0]["channel_id"], 0)
    
# def test_invalid_unread(create_input):
#     '''unread message is greater than total message'''
#     with pytest.raises(InputError):
#         channel_messages_v1(create_input[0][0]["auth_user_id"], create_input[0][0]["channel_id"], 130)
    
def test_message_amount(create_input):
    messages = channel_messages_v1(create_input[0][0]["auth_user_id"], create_input[1][0]["channel_id"], 0)
    assert messages['start'] == 0
    assert messages['end'] == -1
    assert messages['messages'] == [
                    {
                        'message_id':1,
                        'u_id':26,
                        'message':"hello world",
                        'time_created':1616126327
                    },
                    {
                        'message_id':2,
                        'u_id':42,
                        'message':"goodbye world",
                        'time_created':1616126390
                    }
                ]

def test_message_amount_shifted(create_input):
    messages = channel_messages_v1(create_input[0][0]["auth_user_id"], create_input[1][0]["channel_id"], 1)
    assert messages['start'] == 1
    assert messages['end'] == -1
    assert messages['messages'] == [
                    {
                        'message_id':2,
                        'u_id':42,
                        'message':"goodbye world",
                        'time_created':1616126390
                    }
                ]