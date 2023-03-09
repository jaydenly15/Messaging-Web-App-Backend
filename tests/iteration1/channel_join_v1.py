import pytest
from src.auth import auth_register_v1
from src.channel import channel_join_v1, channel_details_v1
from src.channels import channels_create_v1, channels_list_v1
from src.other import clear_v1
from src.error import InputError, AccessError

@pytest.fixture()
def create_input():
    clear_v1()

    data_test_users = [
        auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan")['auth_user_id'],
        auth_register_v1("jaydenly@mail.com", "123456", "jayden", "ly")['auth_user_id'], 
        auth_register_v1("james.teng@mail.com", "123456", "james", "teng")['auth_user_id'], 
        auth_register_v1("william.sheppard@mail.com", "123456", "william", "sheppard")['auth_user_id'], 
        auth_register_v1("eric.cai@mail.com", "123456", "eric", "cai")['auth_user_id']
    ]

    data_test_channels = [channels_create_v1(data_test_users[0], "First Channel", True)['channel_id'],
        channels_create_v1(data_test_users[1], "Second Channel", True)['channel_id'],
        channels_create_v1(data_test_users[2], "Third Channel", False)['channel_id']
    ]

    return [data_test_users, data_test_channels]
    
def test_single_channel1(create_input):
    u_ids, c_ids = create_input
    channel_join_v1(u_ids[0], c_ids[1])
    channel_join_v1(u_ids[2], c_ids[1])
    channel_join_v1(u_ids[3], c_ids[1])
    channel_join_v1(u_ids[4], c_ids[1])

    # Checks that there are five members in total
    assert len(channel_details_v1(u_ids[0], c_ids[1])['all_members']) == 5

    # Checks that only single owner exists
    assert len(channel_details_v1(u_ids[0], c_ids[1])['owner_members']) == 1

def test_single_channel2(create_input):
    u_ids, c_ids = create_input
    channel_join_v1(u_ids[0], c_ids[1])
    channel_join_v1(u_ids[3], c_ids[1])
    channel_join_v1(u_ids[4], c_ids[1])

    # Checks that there are five members in total
    assert len(channel_details_v1(u_ids[0], c_ids[1])['all_members']) == 4

    # Checks first name returned are correct and in order
    first_names = [user['name_first'] for user in channel_details_v1(u_ids[0], c_ids[1])['all_members']]
    assert first_names == ['jayden', 'ruosong', 'william', 'eric']

    # Checks that only single owner exists
    assert len(channel_details_v1(u_ids[0], c_ids[1])['owner_members']) == 1

def test_channel_join_return_type(create_input):
    u_ids, c_ids = create_input
    assert channel_join_v1(u_ids[0], c_ids[1]) == {}

def test_channel_id_invalid(create_input):
    u_ids, c_ids = create_input
    #channel_id sum(c_ids) does not exist
    with pytest.raises(InputError):
        channel_join_v1(u_ids[0], sum(c_ids))

def test_auth_user_id_invalid(create_input):
    u_ids, c_ids = create_input
    #auth_user_id sum(u_ids) does not exist
    with pytest.raises(AccessError):
        channel_join_v1(sum(u_ids), c_ids[0])

def test_both_cid_and_uid_invalid(create_input):
    u_ids, c_ids = create_input
    # auth_user_id and channel_id does not exist,
    # InputError is prioritised
    with pytest.raises(AccessError):
        channel_join_v1(sum(u_ids), sum(c_ids))

def test_fail_private_channel(create_input):
    u_ids, c_ids = create_input
    assert len(channel_details_v1(u_ids[2], c_ids[2])["owner_members"]) == 1 
    assert len(channel_details_v1(u_ids[2], c_ids[2])["all_members"]) == 1

    #AccessError becuase these users are not global owners
    with pytest.raises(AccessError):
        channel_join_v1(u_ids[4], c_ids[2])
    with pytest.raises(AccessError):
        channel_join_v1(u_ids[1], c_ids[2])
    with pytest.raises(AccessError):
        channel_join_v1(u_ids[3], c_ids[2])


def test_success_private_channel(create_input):
    u_ids, c_ids = create_input
    assert len(channel_details_v1(u_ids[2], c_ids[2])["owner_members"]) == 1 
    assert len(channel_details_v1(u_ids[2], c_ids[2])["all_members"]) == 1
    
    channel_join_v1(u_ids[0], c_ids[2])

    # Succesfully joins private channel, since user with u_ids[0] is a global owner
    assert len(channel_details_v1(u_ids[0], c_ids[2])["owner_members"]) == 1
    assert len(channel_details_v1(u_ids[0], c_ids[2])["all_members"]) == 2

