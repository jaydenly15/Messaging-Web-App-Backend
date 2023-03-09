import pytest

from src.auth import auth_register_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

@pytest.mark.skip
def create_valid_user_data():
    """ Creates and returns a set of valid users.
    """
    user_data = (
        auth_register_v1("ruosong.pan@mail.com", "123456", "ruosong", "pan"),
        auth_register_v1("jayden.ly@mail.com", "123456", "jayden", "ly"), 
        auth_register_v1("james.teng@mail.com", "123456", "james", "teng"), 
        auth_register_v1("william.sheppard@mail.com", "123456", "william", "sheppard"), 
        auth_register_v1("eric.cai@mail.com", "123456", "eric", "cai")
    ) 
    return user_data

def test_invalid_channel_id_exception():
    """ Tests for InputError when Channel ID is passed in as an invalid channel.
    """
    clear_v1()

    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()

    channel = channels_create_v1(user_1['auth_user_id'], "Silent Fox", True)
    channel_join_v1(user_2['auth_user_id'], channel['channel_id'])
    channel_join_v1(user_3['auth_user_id'], channel['channel_id'])
    channel_join_v1(user_4['auth_user_id'], channel['channel_id'])
    channel_join_v1(user_5['auth_user_id'], channel['channel_id'])
    
    with pytest.raises(InputError):
        channel_details_v1(user_2['auth_user_id'], channel['channel_id'] + 5)
    with pytest.raises(InputError):
        channel_details_v1(user_3['auth_user_id'], channel['channel_id'] + 5000)
    with pytest.raises(InputError):
        channel_details_v1(user_4['auth_user_id'], channel['channel_id'] - 500)
    with pytest.raises(InputError):
        channel_details_v1(user_5['auth_user_id'], channel['channel_id'] + 2)

def test_invalid_auth_id_exception():
    """ Tests when the authorised user is an invalid id
    """
    clear_v1()

    user = auth_register_v1("example@mail.com", "123456", "example", "N/A")
    channel = channels_create_v1(user['auth_user_id'], "Valid channel", True)

    with pytest.raises(AccessError):
        channel_details_v1(user['auth_user_id'] + 3, channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user['auth_user_id'] + 4000, channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user['auth_user_id'] + 50000, channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user['auth_user_id'] - 7, channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user['auth_user_id'] - 8000, channel['channel_id'])

def test_unauthorised_user_exception():
    """ Tests for AccessError when Authorised user is not a member of channel
        with channel_id.
    """
    clear_v1()

    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()
    channel1 = channels_create_v1(user_1['auth_user_id'], "beep", True)
    channel2 = channels_create_v1(user_2['auth_user_id'], "boom", True)

    channel_join_v1(user_3['auth_user_id'], channel1['channel_id'])

    with pytest.raises(AccessError):
        channel_details_v1(user_3['auth_user_id'], channel2['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user_1['auth_user_id'], channel2['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user_4['auth_user_id'], channel1['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user_5['auth_user_id'], channel2['channel_id'])
    with pytest.raises(AccessError):
        channel_details_v1(user_2['auth_user_id'], channel1['channel_id'])

def test_order_of_exceptions():
    """ Tests that the function raises exceptions in the order as assumed. The order
        should be:
        1. InputError from invalid channel id
        2. AccessError from invalid auth user id
        3. AccessError when any of the authorised user is not already part of
        the channel with channel_id
    """
    clear_v1()

    user_1 = auth_register_v1("example1@mail.com", "123456", "qwe","rty")
    user_2 = auth_register_v1("example2@mail.com", "123456", "asd","fgh")
    channel = channels_create_v1(user_1['auth_user_id'], "General", True)

    with pytest.raises(InputError):
        channel_details_v1(user_2['auth_user_id'], channel['channel_id'] + 3)

    with pytest.raises(AccessError):
        channel_details_v1(user_2['auth_user_id'] + 6, channel['channel_id'])
    
    with pytest.raises(AccessError):
        channel_details_v1(user_2['auth_user_id'], channel['channel_id'])

    with pytest.raises(AccessError):
        channel_details_v1(user_2['auth_user_id'] + 2, channel['channel_id'] + 2)

def test_correct_details():
    """ Tests for successful list of channel details.
    """
    clear_v1()

    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()
   
    channel_1 = channels_create_v1(user_1['auth_user_id'], "sing", True)
    channel_2 = channels_create_v1(user_2['auth_user_id'], "dance", True)
    channel_3 = channels_create_v1(user_3['auth_user_id'], "rap", True)

    channel_join_v1(user_2['auth_user_id'], channel_1['channel_id'])
    channel_join_v1(user_3['auth_user_id'], channel_1['channel_id'])
    channel_join_v1(user_4['auth_user_id'], channel_1['channel_id'])
    channel_join_v1(user_5['auth_user_id'], channel_1['channel_id'])

    channel_join_v1(user_4['auth_user_id'], channel_2['channel_id'])
    channel_join_v1(user_5['auth_user_id'], channel_2['channel_id'])

    channel_join_v1(user_1['auth_user_id'], channel_3['channel_id'])
    channel_join_v1(user_5['auth_user_id'], channel_3['channel_id'])

    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) == {
        'name': 'sing',
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_1['auth_user_id'],     
                'name_first': 'ruosong',
                'name_last': 'pan',
                'email': 'ruosong.pan@mail.com',
                'handle_str': 'ruosongpan', 
            }
        ],
        'all_members': [
            {
                'u_id': user_1['auth_user_id'],
                'name_first': 'ruosong',
                'name_last': 'pan',
                'email': 'ruosong.pan@mail.com',
                'handle_str': 'ruosongpan',
            },
            {
                'u_id': user_2['auth_user_id'],
                'name_first': 'jayden',
                'name_last': 'ly',
                'email': 'jayden.ly@mail.com',
                'handle_str': 'jaydenly',
            },
            {
                'u_id': user_3['auth_user_id'],
                'name_first': 'james',
                'name_last': 'teng',
                'email': 'james.teng@mail.com',
                'handle_str': 'jamesteng',
            },
            {
                'u_id': user_4['auth_user_id'],
                'name_first': 'william',
                'name_last': 'sheppard',
                'email': 'william.sheppard@mail.com',
                'handle_str': 'williamsheppard',
            },
            {
                'u_id': user_5['auth_user_id'],
                'name_first': 'eric',
                'name_last': 'cai',
                'email': 'eric.cai@mail.com',
                'handle_str': 'ericcai',
            }
        ],
    }
    
    assert channel_details_v1(user_2['auth_user_id'], channel_2['channel_id']) == {
        'name': 'dance',
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_2['auth_user_id'],
                'name_first': 'jayden',
                'name_last': 'ly',
                'email': 'jayden.ly@mail.com',
                'handle_str': 'jaydenly',
            }
        ],
        'all_members': [
            {
                'u_id': user_2['auth_user_id'],
                'name_first': 'jayden',
                'name_last': 'ly',
                'email': 'jayden.ly@mail.com',
                'handle_str': 'jaydenly',
            },
            {
                'u_id': user_4['auth_user_id'],
                'name_first': 'william',
                'name_last': 'sheppard',
                'email': 'william.sheppard@mail.com',
                'handle_str': 'williamsheppard',
            },
            {
                'u_id': user_5['auth_user_id'],
                'name_first': 'eric',
                'name_last': 'cai',
                'email': 'eric.cai@mail.com',
                'handle_str': 'ericcai',
            },
        ],
    }
    
    assert channel_details_v1(user_3['auth_user_id'], channel_3['channel_id']) == {
        'name': 'rap',
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_3['auth_user_id'],
                'name_first': 'james',
                'name_last': 'teng',
                'email': 'james.teng@mail.com',
                'handle_str': 'jamesteng',
            }
        ],
        'all_members': [
            {
                'u_id': user_3['auth_user_id'],
                'name_first': 'james',
                'name_last': 'teng',
                'email': 'james.teng@mail.com',
                'handle_str': 'jamesteng',
            },
            {
                'u_id': user_1['auth_user_id'],
                'name_first': 'ruosong',
                'name_last': 'pan',
                'email': 'ruosong.pan@mail.com',
                'handle_str': 'ruosongpan',
            },
            {
                'u_id': user_5['auth_user_id'],
                'name_first': 'eric',
                'name_last': 'cai',
                'email': 'eric.cai@mail.com',
                'handle_str': 'ericcai',
        },
        ],
    }
    
    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) == \
        channel_details_v1(user_2['auth_user_id'], channel_1['channel_id'])
    assert channel_details_v1(user_2['auth_user_id'], channel_2['channel_id']) == \
        channel_details_v1(user_4['auth_user_id'], channel_2['channel_id'])
    assert channel_details_v1(user_3['auth_user_id'], channel_3['channel_id']) == \
        channel_details_v1(user_1['auth_user_id'], channel_3['channel_id'])
    assert channel_details_v1(user_3['auth_user_id'], channel_3['channel_id']) == \
        channel_details_v1(user_1['auth_user_id'], channel_3['channel_id'])
    assert channel_details_v1(user_4['auth_user_id'], channel_1['channel_id']) == \
        channel_details_v1(user_3['auth_user_id'], channel_1['channel_id'])
    
    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) != \
        channel_details_v1(user_5['auth_user_id'], channel_2['channel_id'])
    assert channel_details_v1(user_2['auth_user_id'], channel_1['channel_id']) != \
        channel_details_v1(user_2['auth_user_id'], channel_2['channel_id'])
    assert channel_details_v1(user_3['auth_user_id'], channel_3['channel_id']) != \
        channel_details_v1(user_4['auth_user_id'], channel_2['channel_id'])
    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) != \
        channel_details_v1(user_1['auth_user_id'], channel_3['channel_id'])
    assert channel_details_v1(user_5['auth_user_id'], channel_2['channel_id']) != \
        channel_details_v1(user_5['auth_user_id'], channel_3['channel_id'])
        
def test_private_channel_details():
    """ Assume channel_details is able to reveal details of private channels 
        as well 
    """
    clear_v1()
    user_1, user_2, user_3, user_4, user_5 = create_valid_user_data()
    channel_1 = channels_create_v1(user_1['auth_user_id'], "basketball", False)
    channel_invite_v1(user_1['auth_user_id'], channel_1['channel_id'], user_2['auth_user_id'])
    channel_invite_v1(user_1['auth_user_id'], channel_1['channel_id'], user_3['auth_user_id'])
    channel_invite_v1(user_1['auth_user_id'], channel_1['channel_id'], user_4['auth_user_id'])
    channel_invite_v1(user_1['auth_user_id'], channel_1['channel_id'], user_5['auth_user_id'])

    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) == {
        'name': 'basketball',
        'is_public': False,
        'owner_members': [
            {
                'u_id': user_1['auth_user_id'],     
                'name_first': 'ruosong',
                'name_last': 'pan',
                'email': 'ruosong.pan@mail.com',
                'handle_str': 'ruosongpan',
            }
        ],
        'all_members': [
            {
                'u_id': user_1['auth_user_id'],
                'name_first': 'ruosong',
                'name_last': 'pan',
                'email': 'ruosong.pan@mail.com',
                'handle_str': 'ruosongpan',
            },
            {
                'u_id': user_2['auth_user_id'],
                'name_first': 'jayden',
                'name_last': 'ly',
                'email': 'jayden.ly@mail.com',
                'handle_str': 'jaydenly',
            },
            {
                'u_id': user_3['auth_user_id'],
                'name_first': 'james',
                'name_last': 'teng',
                'email': 'james.teng@mail.com',
                'handle_str': 'jamesteng',
            },
            {
                'u_id': user_4['auth_user_id'],
                'name_first': 'william',
                'name_last': 'sheppard',
                'email': 'william.sheppard@mail.com',
                'handle_str': 'williamsheppard',
            },
            {
                'u_id': user_5['auth_user_id'],
                'name_first': 'eric',
                'name_last': 'cai',
                'email': 'eric.cai@mail.com',
                'handle_str': 'ericcai',
            }
        ],
    }
