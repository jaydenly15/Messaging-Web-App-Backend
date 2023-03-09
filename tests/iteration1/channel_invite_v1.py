import pytest

from src.auth import auth_register_v1
from src.channel import channel_invite_v1, channel_details_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

def create_valid_user_data():
    """ Creates and returns a set of valid users.
    """
    user_data = (
        auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan"),
        auth_register_v1("jaydenly@mail.com", "123456", "jayden", "ly"), 
        auth_register_v1("james.teng@mail.com", "123456", "james", "teng"), 
        auth_register_v1("william.sheppard@mail.com", "123456", "william", "sheppard"), 
        auth_register_v1("eric.cai@mail.com", "123456", "eric", "cai")
    ) 
    '''register an account for each people'''
    '''set password as 123456 as examples XD This is a terrible password'''
    return user_data

def test_invalid_channel_id():
    """ Tests when channel_id does not refer to a valid channel."""
    clear_v1()

    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()

    channel = channels_create_v1(user_1['auth_user_id'], "Party Time", True)
    
    '''Creating valid channel_id '''

    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel['channel_id'] + 1000,user_2['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel['channel_id'] + 500,user_3['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel['channel_id'] - 1000,user_4['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel['channel_id'] - 500,user_5['auth_user_id'])
    '''excepting InputError to occur when inviting to an invalid channel'''
    
def test_invalid_user_id():
    """ Tests when u_id does not refer to a valid user.
    """
    clear_v1()

    #Create a valid user and add them to a valid channel
    #Under this circumstance, we only need one user to do the test , so only one user is need to create
    user = auth_register_v1("example@mail.com", "123456", "example", "N/A")
    channel = channels_create_v1(user['auth_user_id'], "camel", True)

    #Test for InputError when invalid users are invited to channel
    with pytest.raises(InputError):
        channel_invite_v1(user['auth_user_id'], channel['channel_id'],user['auth_user_id'] + 5)


def test_invalid_creator_id():
    """ Tests when the authorised user is an invalid id
        This one is different from last one, last one is test for invalid invitor,
        and this one is test for invalid channel creator
        Though this test is not involved in gitlab page but I think it is somewhat
        worth testing and it is a good assumption
    """
    clear_v1()

    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()

    #Create a valid channel with user as owner
    user = auth_register_v1("example@mail.com", "123456", "example", "N/A")
    channel = channels_create_v1(user['auth_user_id'], "camel", True)

    with pytest.raises(AccessError):
        channel_invite_v1(user['auth_user_id'] + 50, channel['channel_id'],user_1['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user['auth_user_id'] + 500, channel['channel_id'],user_2['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user['auth_user_id'] + 5000, channel['channel_id'],user_3['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user['auth_user_id'] - 50, channel['channel_id'],user_4['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user['auth_user_id'] - 5000, channel['channel_id'],user_5['auth_user_id'])

def test_unauthorised_user():
    """ Tests when the authorised user is not already a member of the channel
    """
    clear_v1()

    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()

    #Create a channel with user_in_channel as the only member
    user_in_channel = auth_register_v1("example@mail.com", "123456", "example", "N/A")
    channel = channels_create_v1(user_in_channel['auth_user_id'], "camel", True)

    with pytest.raises(AccessError):
        channel_invite_v1(user_1['auth_user_id'], channel['channel_id'],user_2['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user_2['auth_user_id'], channel['channel_id'],user_3['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user_3['auth_user_id'], channel['channel_id'],user_4['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user_4['auth_user_id'], channel['channel_id'],user_5['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user_5['auth_user_id'], channel['channel_id'],user_1['auth_user_id'])

def test_Already_member_of_channel():
    clear_v1()
    user_in_channel = auth_register_v1("example@mail.com", "123456", "example", "N/A")
    channel = channels_create_v1(user_in_channel['auth_user_id'], "camel", True)
    with pytest.raises(InputError):
        channel_invite_v1(user_in_channel['auth_user_id'], channel['channel_id'],user_in_channel['auth_user_id'])
        
    
def test_successful_invites():
    """ Tests for multiple successful invites to a channel
    """
    clear_v1()

    #Create a set of users not in the channel yet
    user_1 = auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan")

    #Create channels with user_auth_X as owner
    user_auth_1 = auth_register_v1("example@mail.com", "123456", "example","N/A")

    channel_1 = channels_create_v1(user_auth_1['auth_user_id'], "Partee", True)

    #Test for successful calls and that users have been immediately added into
    #their channels

    #Invite user1 to channel 1
    assert channel_invite_v1(user_auth_1['auth_user_id'], channel_1['channel_id'],user_1['auth_user_id']) == {}

    #Check that user have been added to channels
    channel_detail_1 = channel_details_v1(user_auth_1['auth_user_id'],channel_1['channel_id'])


    #Check channel 1
    assert channel_detail_1['all_members'][0]['u_id'] == user_auth_1['auth_user_id']


def test_invite_private_channel():
    """ Tests that users can be invited into private channels too.
    """
    clear_v1()

    user_1, user_2, user_3, _, _ = create_valid_user_data()

    channel_private = channels_create_v1(user_1['auth_user_id'], "Secret", False)

    assert channel_invite_v1(user_1['auth_user_id'], channel_private['channel_id'], user_2['auth_user_id']) == {}
    assert channel_invite_v1(user_2['auth_user_id'], channel_private['channel_id'], user_3['auth_user_id']) == {}

def test_invite_public_channel():
    """ Tests that users can be invited into public channels too.
    """
    clear_v1()

    user_1, user_2, user_3, _, _ = create_valid_user_data()

    channel_public = channels_create_v1(user_1['auth_user_id'], "Secret", True)

    assert channel_invite_v1(user_1['auth_user_id'], channel_public['channel_id'], user_2['auth_user_id']) == {}
    assert channel_invite_v1(user_2['auth_user_id'], channel_public['channel_id'], user_3['auth_user_id']) == {}