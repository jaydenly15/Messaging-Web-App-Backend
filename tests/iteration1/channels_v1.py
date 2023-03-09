import pytest

from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.auth import auth_login_v1, auth_register_v1
from src.channel import channel_join_v1, channel_invite_v1
from src.other import clear_v1
from src.error import InputError
from src.error import AccessError

# Registers 5 users and returns a tuple of their IDS
@pytest.fixture()
def clear_and_register_group_camel():
    clear_v1()
    user_ids = [
        auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan")['auth_user_id'],
        auth_register_v1("jaydenly@mail.com", "123456", "jayden", "ly")['auth_user_id'], 
        auth_register_v1("james.teng@mail.com", "123456", "james", "teng")['auth_user_id'], 
        auth_register_v1("william.sheppard@mail.com", "123456", "william", "sheppard")['auth_user_id'], 
        auth_register_v1("eric.cai@mail.com", "123456", "eric", "cai")['auth_user_id']
    ]
    return user_ids

# Creates multiple channels and returns a list of user_ids and channel_ids ([user_ids], [channel_ids])
@pytest.fixture()
def create_multiple_channels(clear_and_register_group_camel):
    user_ids = clear_and_register_group_camel
    # user_ids[0] is the owner of channels_id[0], user_ids[1] is the owner of channels_id[1] etc...
    # creates 4 channels 
    channels_id = [
        channels_create_v1(user_ids[count], 'Example Channel' + str(count), True)['channel_id']\
        for count in range(4)
    ]
    return (user_ids, channels_id)


def test_invalid_channel_name(clear_and_register_group_camel):
    user_ids = clear_and_register_group_camel
    # checking Channel Name which is too short
    with pytest.raises(InputError):
        channels_create_v1(user_ids[0], '', True)
    # checking Channel Name which is too long
    with pytest.raises(InputError):
        channels_create_v1(user_ids[0], 'LongInvalidChannelName', True)


# checks correct channels were created and it lists the correct channels for each owner
def test_channels_list1(clear_and_register_group_camel):
    user_ids = clear_and_register_group_camel
    
    # Creates 10 different channels owned by a single person with ID, 'user_id[0]'
    channel_ids = [
        channels_create_v1(user_ids[0], 'Example Channel' + str(count), True)['channel_id'] for count in range(10)
    ]

    channel_names = ['Example Channel' + str(count) for count in range(10)]

    assert channels_list_v1(user_ids[0]) ==\
        {'channels': [{'channel_id': channel_ids[i], 'name': channel_names[i]} for i in range(10)]}


# checks that each channel owner owns the expected created channels
def test_channel_list_2(clear_and_register_group_camel):
    user_ids = clear_and_register_group_camel

    # Creates 100 channels with random owners and returns their channel_ids in a list
    channel_ids = [
        channels_create_v1(user_ids[count % 5], 'Example Channel' + str(count), True)['channel_id'] for count in range(100)
    ]

    channel_names = ['Example Channel' + str(count) for count in range(100)]

    # Checks that each channel_id is unique
    assert channels_list_v1(user_ids[0]) ==\
        {'channels': [{'channel_id': channel_ids[i], 'name': channel_names[i]} for i in range(0, 100, 5)]}
    assert channels_list_v1(user_ids[1]) ==\
        {'channels': [{'channel_id': channel_ids[i], 'name': channel_names[i]} for i in range(1, 100, 5)]}
    assert channels_list_v1(user_ids[2]) ==\
        {'channels': [{'channel_id': channel_ids[i], 'name': channel_names[i]} for i in range(2, 100, 5)]}
    assert channels_list_v1(user_ids[3]) ==\
        {'channels': [{'channel_id': channel_ids[i], 'name': channel_names[i]} for i in range(3, 100, 5)]}
    assert channels_list_v1(user_ids[4]) ==\
        {'channels': [{'channel_id': channel_ids[i], 'name': channel_names[i]} for i in range(4, 100, 5)]}

# checks that there are no duplicate channel_ids after creating multiple channels
def test_channel_id_uniqueness(clear_and_register_group_camel):
    user_ids = clear_and_register_group_camel

    # Creates 100 channels with random owners and returns their channel_ids in a list
    channel_ids = [
        channels_create_v1(user_ids[count % 5], 'Example Channel' + str(count), True)['channel_id'] for count in range(100)
    ]

    # Checks that each channel_id is unique
    assert len(channel_ids) == len(set(channel_ids))

# checks that invalid auth_user_ids raise an AccessError
def test_auth_user_id_invalid(clear_and_register_group_camel):
    clear_v1()
    # register 3 users with ids 1-3
    u_ids = [
        auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan")['auth_user_id'],
        auth_register_v1("jaydenly@mail.com", "123456", "jayden", "ly")['auth_user_id'],
        auth_register_v1("james.teng@mail.com", "123456", "james", "teng")['auth_user_id']
    ]
    with pytest.raises(AccessError):
        channels_list_v1(sum(u_ids))
    with pytest.raises(AccessError):
        channels_listall_v1(sum(u_ids))
    with pytest.raises(AccessError):
        channels_create_v1(sum(u_ids), "Test Channel1", True)
    
# simple test to see if list all is returning the correct groups
def test_channels_list_all(create_multiple_channels):
    user_ids, __ = create_multiple_channels
    assert channels_listall_v1(user_ids[0])['channels'] == [{'channel_id': count + 1, 'name': 'Example Channel' + str(count)} for count in range(4)]

# Tests channels_list_v1() with channel_join
def test_channels_list2(create_multiple_channels):
    # user_ids[0] is the owner of channels_id[0], user_ids[1] is the owner of channels_id[1] etc...
    user_ids, channel_ids = create_multiple_channels

    # Loop to get user[0] to join all other channels
    for i in range(1, len(channel_ids)):
        channel_join_v1(user_ids[0], channel_ids[i])

    # correct output is a list of all channels
    assert channels_list_v1(user_ids[0]) == {'channels': [{'channel_id': channel_ids[i], 'name': 'Example Channel' + str(i)} for i in range(0, len(channel_ids))]}

# tests invites and joining with private channels
def test_channels_list_priv(clear_and_register_group_camel):
    user_ids = clear_and_register_group_camel
    # user_ids[0] is the owner of channels_id[0], user_ids[1] is the owner of channels_id[1]
    # creates 2 public channels
    channels_id_pub = [
        channels_create_v1(user_ids[count], 'Example Channel' + str(count), True)['channel_id']\
        for count in range(2)
    ]
    # user_ids[2] is the owner of channels_id[2], user_ids[3] is the owner of channels_id[3]
    # creates 2 private channels 
    channels_id_priv = [
        channels_create_v1(user_ids[count], 'Example Channel' + str(count), False)['channel_id']\
        for count in range(2, 4)
    ]
    channels_ids = channels_id_pub + channels_id_priv 
    # invites user_ids[3] to channels_ids[1] (PUBLIC) by user_ids[1]
    channel_invite_v1(user_ids[1], channels_ids[1], user_ids[3])
    # invites user_ids[3] to channels_ids[2] (PRIVATE) by user_ids[2]
    channel_invite_v1(user_ids[2], channels_ids[2], user_ids[3])
    # user_ids[3] joins channels_ids[0] (PUBLIC)
    channel_join_v1(user_ids[3], channels_ids[0])
    assert channels_list_v1(user_ids[3]) == {'channels': [{'channel_id': channels_ids[i], 'name': 'Example Channel' + str(i)} for i in range(0, 4)]}