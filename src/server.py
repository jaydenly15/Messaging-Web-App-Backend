import re
import sys
import signal
from json import dumps, dump, load
from flask import Flask, request
import requests
from flask_cors import CORS
from src.error import InputError
from src.other import clear_v1, save
from src.auth import auth_login_v1, auth_register_v1
from src.user import user_profile_setemail_v1, users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_sethandle_v1, user_profile_uploadphoto_v1, users_stats_v1, user_stats_v1
from src.channel import channel_details_v1, channel_addowner, channel_removeowner
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1, auth_password_reset_request_v1, auth_password_reset_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.dm import dm_create_v1, dm_details_v1, dm_list_v1, dm_messages_v1, dm_remove_v1, dm_leave_v1
from src.token import generate_token, get_user_from_token
from src.data_store import data_store
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_share_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src import config
from src.channel import channel_join_v1, channel_leave, channel_invite_v1, channel_messages_v1
from src.admin import admin_user_remove_v1, admin_user_permission_change_v1
from src.token import reset_session_tracker
from src.global_owners import reset_num_global_owners
from src.search import search_v1
from src.message_send_later import message_send_later_v1, message_send_later_dm_v1
from src.notification  import notifications_get_v1
from src.standup import standup_active_v1, standup_send_v1, standup_start_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# _____________________________  HELPER FUNCTIONS  _______________________________

# Resets data on server and empties data_store.json 
@APP.route("/clear/v1", methods=['DELETE'])
def clear_v2():
    reset_session_tracker()
    reset_num_global_owners()
    clear_v1()
    save()
    return {}

# ________________________  EXECUTES WHEN SERVER STARTS  _______________________

# Loads persistent data into data_store when server starts
with open('src/data_store.json', 'r') as file:
    try:
        data_store.set(load(file))
    except:
        clear_v1()

# _____________________________  AUTH FUNCTIONS  _______________________________

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():
    payload = request.get_json()
    user_key = auth_login_v1(payload['email'], payload['password'])
    save()
    return dumps(user_key)

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    user = request.get_json()
    user_key = auth_register_v1(user['email'], user['password'], \
                            user['name_first'], user['name_last'])
    save()
    return dumps(user_key)

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    payload = request.get_json()
    auth_logout_v1(payload['token'])
    save()
    return dumps({})

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_password_reset_request():
    payload = request.get_json()
    auth_password_reset_request_v1(payload['email'])
    save()
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_password_reset():
    payload = request.get_json()
    auth_password_reset_v1(payload['reset_code'], payload['new_password'])
    save()
    return dumps({})
# _____________________________  CHANNELS FUNCTIONS  _______________________________
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    payload = request.get_json()
    user_id = get_user_from_token(payload['token'])['u_id']
    result = channels_create_v1(user_id, payload['name'], payload['is_public'])
    save()
    return dumps(result)

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    token = request.args.get('token')
    user_id = get_user_from_token(token)['u_id']
    result = channels_list_v1(user_id)
    save()
    return dumps(result)
    
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    token = request.args.get('token')
    user_id = get_user_from_token(token)['u_id']
    result = channels_listall_v1(user_id)
    save()
    return dumps(result)

# _____________________________  CHANNEL FUNCTIONS  _______________________________
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    user_id = get_user_from_token(token)['u_id']
    return dumps(channel_details_v1(user_id, int(channel_id)))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner_v1():
    payload = request.get_json()
    channel_addowner(payload['token'], payload['channel_id'], payload['u_id'])
    save()
    return dumps({})

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner_v1():
    payload = request.get_json()
    channel_removeowner(payload['token'], payload['channel_id'], payload['u_id'])
    save()
    return dumps({})

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    payload = request.get_json()
    auth_user = get_user_from_token(payload['token'])['u_id']
    channel_join_v1(auth_user, payload['channel_id'])
    save()
    return dumps({})

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v1():
    channel = request.get_json()
    auth_user = get_user_from_token(channel['token'])['u_id']
    channel_leave(auth_user, channel['channel_id'])
    save()
    return dumps({})

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    channel = request.get_json()
    auth_user = get_user_from_token(channel['token'])['u_id']
    channel_invite_v1(auth_user, channel['channel_id'], channel['u_id'])
    save()
    return dumps({})

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get('token')
    user = int(get_user_from_token(token)['u_id'])
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    result = channel_messages_v1(user, channel_id, start)
    save()
    return dumps(result)
    
# _____________________________  MESSAGE FUNCTIONS  ____________________________________
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    payload = request.get_json()
    result = message_send_v1(payload['token'], payload['channel_id'], payload['message'])
    save()
    return dumps(result)

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    payload = request.get_json()
    message_edit_v1(payload['token'], payload['message_id'], payload['message'])
    save()
    return dumps({})
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    payload = request.get_json()
    message_remove_v1(payload['token'], payload['message_id'])
    save()
    return dumps({})

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    payload = request.get_json()
    result = message_senddm_v1(payload['token'], payload['dm_id'], payload['message'])
    save()
    return dumps(result)

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    payload = request.get_json()
    result = message_share_v1(payload['token'], payload['og_message_id'], payload['message'], payload['channel_id'], payload['dm_id'])
    save()
    return dumps(result)

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    payload = request.get_json()
    message_react_v1(payload['token'], payload['message_id'], payload['react_id'])
    save()
    return dumps({})

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    payload = request.get_json()
    message_unreact_v1(payload['token'], payload['message_id'], payload['react_id'])
    save()
    return dumps({})

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    payload = request.get_json()
    message_pin_v1(payload['token'], payload['message_id'])
    save()
    return dumps({})

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    payload = request.get_json()
    message_unpin_v1(payload['token'], payload['message_id'])
    save()
    return dumps({})

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_send_later():
    payload = request.get_json()
    result = message_send_later_v1(payload['token'], payload['channel_id'], \
        payload['message'], payload['time_sent'])
    save()
    return dumps(result)

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def dm_send_later():
    payload = request.get_json()
    result = message_send_later_dm_v1(payload['token'], payload['dm_id'], \
        payload['message'], payload['time_sent'])
    save()
    return dumps(result)

@APP.route("/search/v1", methods=['GET'])
def search_route():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    result = search_v1(token, query_str)
    return dumps(result)
# _____________________________  DM FUNCTIONS  ____________________________________

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    payload = request.get_json()
    print(payload.get('u_ids'))
    dm_id = dm_create_v1(payload['token'], payload['u_ids'])
    save()
    return dumps(dm_id)

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    dms = dm_list_v1(token)
    return dumps(dms)

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    payload = request.get_json()
    token, dm_id = payload['token'], payload['dm_id']
    dm_remove_v1(token, dm_id)
    save()
    return dumps({})

@APP.route("/dm/details/v1", methods=['GET'])
def dm_detail():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    dm_details = dm_details_v1(token, int(dm_id))
    return dumps(dm_details)

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    payload = request.get_json()
    token, dm_id = payload['token'], payload['dm_id']
    dm_leave_v1(token, dm_id)
    save()
    return dumps({})

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    messages = dm_messages_v1(token, dm_id, start)
    return dumps(messages)

#__________________________________USER FUNCTIONS_______________________#

@APP.route("/users/all/v1", methods=['GET'])
def user_all():
    token = request.args.get('token')
    users = users_all_v1(token)
    
    return dumps(users)
    
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    return dumps(user_profile_v1(token, int(u_id)))
    
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    payload = request.get_json()
    token, name_first, name_last= payload['token'], payload['name_first'], payload['name_last']
    user_profile_setname_v1(token, name_first, name_last)
    save()
    return dumps({})
    
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
    payload = request.get_json()
    token, email= payload['token'], payload['email']
    user_profile_setemail_v1(token,email)
    save()
    return dumps({})
    
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    payload = request.get_json()
    token, handle_str= payload['token'], payload['handle_str']
    user_profile_sethandle_v1(token, handle_str)
    save()
    return dumps({})

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto():
    payload = request.get_json()
    user_profile_uploadphoto_v1(payload['token'], payload['img_url'],
                         payload['x_start'], payload['y_start'], payload['x_end'], payload['y_end'])
    save()
    return dumps({})

@APP.route("/user/stats/v1", methods = ['GET'])
def user_stats():
    token = request.args.get('token')
    stats = user_stats_v1(token)
    save()
    return dumps({'user_stats': stats})

@APP.route("/users/stats/v1", methods = ['GET'] )
def users_stats():
    token = request.args.get('token')
    users_stats_v1(token)
    save()
    return dumps({})

#__________________________________ADMIN FUNCTIONS_______________________#
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    payload = request.get_json()
    admin_user_remove_v1(payload['token'], payload['u_id'])
    save()
    return dumps({})

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_user_permission_change():
    payload = request.get_json()
    token = payload['token']
    u_id = payload['u_id']
    permission_id = int(payload['permission_id'])
    admin_user_permission_change_v1(token, u_id, permission_id)
    save()
    return dumps({})

#__________________________________STANDUP FUNCTIONS_______________________#

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    payload = request.get_json()
    time_finish = standup_start_v1(payload['token'], payload['channel_id'], payload['length'])
    save()
    return dumps({'time_finish': time_finish})

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    active = standup_active_v1(token, int(channel_id))
    return dumps({'is_active': active[0], 'time_finish': active[1]})

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    payload = request.get_json()
    standup_send_v1(payload['token'], payload['channel_id'], payload['message'])
    save()
    return dumps({})

#__________________________________NOTIFICATIONS_______________________#
@APP.route("/notifications/get/v1", methods=['GET'])
def get_notifs():
    token = request.args.get('token')
    latest_notifs = notifications_get_v1(token)
    return dumps(latest_notifs)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
