import datetime
from src.error import InputError
from src import config
from src.data_store import data_store
from src.error import InputError
from src.token import get_ids_from_token, get_user_from_token
import hashlib
import jwt
import re 
import urllib.request
import requests
from PIL import Image
import time
from datetime import datetime

regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
SECRET = 'CAMEL'
from json import dumps
# store = data_store.get() 
# def get_data():
#     # helper function for getting data from the json file
#     with open('src/data_store.json','r') as file:
#         store = loads(file.read())
#         return store
    
# def writeData(store):
#     #helper function for writing data back to json file
#     with open('src/data_store.json','w') as file:
#         store = loads(file.write())
#         return store
def writeData(data):
    #Writing data to export.json
    with open('src/data_store.json', 'w') as file:
        file.write(dumps(data))   
    
def users_all_v1(token):
    '''
    Given valid token and returns a list of all users and their associated details
    
    Agruments:
        token (type string) - valid token associated with a registered user's session
    Exceptions:
        N/A
    Return value:
        {'user  s':['user':{'u_id' : u_id,
                            'email' : email,
                            'password' : password,
                            'name_first' : name_first,
                            'name_lats; : name_last,
                            'handle_str' : handle_str,}
                    ]
        }
    '''
    user = get_user_from_token(token)
    store = data_store.get() 
    
    # get data from database
    user_list = []
    # create the return type of user profiles
    for user in store['users']:
        profiles = {'u_id': user['u_id'],
                    'email' : user['email'],
                    'name_first' : user['name_first'],
                    'name_last' : user['name_last'],
                    'handle_str' : user['handle_str'],
                    }
        user_list.append(profiles)
        
    return{'users': user_list}

    # no exceptions for this function


def user_profile_v1(token, u_id):
    '''
    Take in valid token and u_id and returns the profile of specified user

    Arguments:
        token: the string which indicates the user's session
        u_id: user id created when registered
    
    Exceptions:
        InputError: u_id does not refer to a valid user
    
    Assumptions:
        token is always valid 
    
    return value:
        {'user':{'u_id' : u_id,
                'email' : email,
                'name_first' : name_first,
                'name_last' : name_last,
                'handle_str' : handle_str,}
        }
    '''
    store = data_store.get() 
    # get data from database
    get_user_from_token(token)['u_id']
    for user in store['users']:
        if u_id == user['u_id']:
            profile = {
                    'user': {
                        'u_id': user['u_id'],
                        'email': user['email'],
                        'name_first': user['name_first'],
                        'name_last': user['name_last'],
                        'handle_str': user['handle_str'],
                        'profile_img_url' : user['profile_img_url']
                    }
            }            
            return profile
    else:
        # Raise InputError(u_id invalid)
        raise InputError(description = "u_id is not valid")
    
def user_profile_setname_v1(token, name_first, name_last):
    '''
    Given token, name_first and name_last and update the username
    
    Arguments:
        token : string which indicates the user's session
        name_first : string, user's first name
        name_last : string, user's last name 
        
    Exceptions:
        InputError - When name_first or name_last is not in range of 1-50 
        
    return value: N/A
        
    '''
    store = data_store.get() 
    # get the relevent user datas
    check = get_user_from_token(token)
    # get the u_id from token taking in
    if len(name_first) > 50 or len(name_first) < 1:
        # if name_first is not in range of 1 to 50
        raise InputError(description="first_name is not in range of 1 to 50")
    if len(name_last) > 50 or len(name_last) < 1:
        # is name_last is not in range of 1 to 50
        raise InputError(description="last_name is not in range of 1 to 50")
        
    check['name_first'] = name_first
    check['name_last'] = name_last
    data_store.set(store)
    #Writing modified data to export.json
    #will add this in server.py
    #writeData(data) 

    return {}
    
def user_profile_setemail_v1(token, email):
    '''
    Takes in token and email and update the user's email address
    
    Arguments:
        token : string, which indicates the user's session
        email : string, which is the user's email address
        
    Exceptions:
        InputError : email is not in valid format
        InputError : email is already being used by another user
        
    Return value ： N/A
    '''
    
    store = data_store.get() 
    # get relevant datas
    check = get_user_from_token(token)
    if not re.match(regex, email):
        raise InputError(description = "Invalid email")
        # check if the email format is correct or raise InputError
        # Creates list of existing emails
    existing_emails = [user['email'] for user in store['users']]
    if email in existing_emails:
        raise InputError(description = "Email address is being used")
        
    check['email'] = email
    data_store.set(store)
    # writeData(data)
    # write back the modified datas
    # will add this in serve.py
            
    return{}


def user_profile_sethandle_v1(token, handle_str):
    '''
    Takes in token and handle_str and rewrite the user's handle_str
    
    Arguments:
        token : string, which indicates the user's session
        handle_str : the information the user wants to update
        
    Exceptions:
        InputError : length of handle_str is not between 3 and 20 characters inclusive
        InpoutError : handle_str contains characters that are not alphanumeric
        InputError : the handle is already used by another user
        
    return : N/A
    '''
    
    store = data_store.get() 
    # getting data from database
    check = get_user_from_token(token)
    # get u_id from token
    if not handle_str.isalnum():
        raise InputError(description="Handle_str contains characters that are not alphanumeric")

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description= "Handle_str is not in range of 3 to 20")
    
    for user in store['users']:
        if handle_str == user['handle_str']:
            raise InputError(description= "Handle_str is being used" )
    
    check['handle_str'] = handle_str
    data_store.set(store)
    writeData(store)
    
    return{}    
        
# --------------------------------------------------iteration3--------------------------------------------------
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """ 
    Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
            
    Arguments:
        token  - string, valid token associated with a registered user's session
        img_url  - string, URl to a jpg online
        x_start  - int, indicates leftmost point on image
        y_start  - int, indicates topmost point on image
        x_end  - int, indicates righttmost point on image
        y_end  - int, indicates bottommost point on image
  
    Exceptions:
        InputError - img_url returns an HTTP status other than 200.
        InputError - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.
        InputError - Image uploaded is not a JPG
    Return value:
        { }
    """
    #Retrieving data from dictionary
    store = data_store.get()
    #Find user id from their token
    u_id = get_user_from_token(token)['u_id']
    #Define URL
    URL = f'{img_url}'
    #Define file path
    fileName = f'src/pic/{u_id}.jpg'
    #Trying to open URL, if it fails raise an InputError
    try:
        status = requests.get(URL).status_code
    except:
        status = -1
    
    if status != 200:
        raise InputError(description='Invalid URL')
    #Raising an error if the URL does not point to a jpg
    if not URL.endswith('.jpg'):
        raise InputError(description = 'Image is not a jpg')
    #Retrieve the URL abd save the image as fileName
    # urllib.request.urlretrieve(URL,fileName)
    
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(URL, fileName) 

    #Open the image
    img = Image.open(fileName)
    #Define the size of the image
    width, height = img.size
    width, height = int(width), int(height)
    #Raising an error if the crop points aren't valid
    if x_start < int(0) or y_start < int(0) or x_end > width or y_end > height or x_end < x_start or y_end < y_start:
        raise InputError(description='Crop start or end points not valid')
    #Cropping and saving the image
    crop_img = img.crop((x_start, y_start, x_end, y_end))
    crop_img.save(fileName)
    #Changin the user's associated URL to the new image
    for user in store['users']:
        if u_id == user['u_id']:
            user['profile_img_url'] = f'{config.url}/src/pic/{u_id}.jpg'
    # writeData(data)     
    return {}

#----------------------helper functions--------------------------

def channel_stats(store,u_id):
    channel_count = 0
    total_channel_count = 0
    for channels in store['channels']:
        # Checks if the user is a member in the channel
        if u_id in channels['users']:
            channel_count += 1
        total_channel_count += 1
    return [channel_count, total_channel_count]

def dm_stats(store,u_id):
    dm_count = 0
    total_dm_count = 0
    for dm in store['dms']:
        if u_id in dm['members']:
            dm_count += 1
        if dm['dm_id'] != -1:
            total_dm_count += 1
    return [dm_count, total_dm_count]

def message_stats(store,u_id):
    message_count = 0
    total_message_count = 0
    for channels in store['channels']:
        for messages in channels['messages']:
            if u_id == messages['u_id']:
                message_count += 1
            total_message_count += 1

    for dm in store['dms']:
        for message in dm['messages']:
            if u_id == message['u_id']:
                message_count += 1
            total_message_count += 1
    return [message_count, total_message_count]
#----------------------------ends------------------------

def update_num_channels(user_id):
    store = data_store.get()

    user = store['users'][user_id - 1]

    channel_count = channel_stats(store, user_id)[0]

    curr_timestamp = datetime.now().timestamp()
    user['channel_joined'] = user.get('channel_joined', [{'num_channels_joined': 0, 'time_stamp': 0}]) + [{'num_channels_joined': channel_count, 
    'time_stamp': curr_timestamp}]    
    data_store.set(store)

def update_num_dms(user_id):
    store = data_store.get()

    user = store['users'][user_id - 1]

    dm_count = dm_stats(store, user_id)[0]

    curr_timestamp = datetime.now().timestamp()
    user['dms_joined'] = user.get('dms_joined', [{'num_dms_joined': 0, 'time_stamp': 0}]) + [{'num_dms_joined': dm_count, 
    'time_stamp': curr_timestamp}]    
    data_store.set(store)

def update_num_message_count(user_id):
    store = data_store.get()

    user = store['users'][user_id - 1]

    message_count = message_stats(store, user_id)[0]

    curr_timestamp = datetime.now().timestamp()
    user['messages_sent'] = user.get('messages_sent', [{'num_messages_sent': 0, 
    'time_stamp': 0}]) + [{'num_messages_sent': message_count, 
    'time_stamp': curr_timestamp}]    
    data_store.set(store)

def user_stats_v1(token):
    u_id = get_user_from_token(token)['u_id']

    store = data_store.get()

    try:
        rate = (channel_stats(store, u_id)[0] + dm_stats(store, u_id)[0] + message_stats(store, u_id)[0])/(channel_stats(store, u_id)[1] + \
        dm_stats(store, u_id)[1] + message_stats(store, u_id)[0])
    except ZeroDivisionError:
        rate = 0
    
    user = store['users'][u_id - 1]

    return {
        'channels_joined': user.get('channel_joined', [{'num_dms_joined': 0, 'time_stamp': 0}]),
        'dms_joined' : user.get('dms_joined', [{'num_dms_joined': 0, 'time_stamp': 0}]),
        'messages_sent' : user.get('messages_sent', [{'num_messages_sent': 0, 'time_stamp': 0}]),
        'involvement_rate' : rate
    }

def users_stats_v1(token):
    u_id = get_user_from_token(token)['u_id']
    store = data_store.get()
    channel_count = channel_stats(store, u_id)[1]
    dm_count = dm_stats(store, u_id)[1]
    message_count = message_stats(store, u_id)[1]
    time_stamp = time.asctime( time.localtime(time.time()) )
    
    users_info = {
        'channels_joined' : [channel_count, time_stamp],
        'dm_joined' : [dm_count, time_stamp],
        'message_sent' : [message_count, time_stamp],
        # 'involvement_rate' : rate
    }
    
    return users_info