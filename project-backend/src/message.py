"""
By Navid Bhuiyan
Date: 26/10/2020

By Kenneth Liu
Date: 09/11/2020

Message features for flockr.

Assumes channels up to 89998, and messages up to 89998.

Message ID is strcutured in this way: CCCCCMMMMMU...

C - Channel ID (Backwards ID i.e. 99999 - CCCCCC = real Channel ID)
M - Message Count
U - User message sent.
"""

import time
import concurrent.futures
from datetime import datetime
from datetime import timezone
from flockr_database_api import DataBase
from error import AccessError, InputError

# Message and channel limitations
NO_CHANNELS = 99999
NO_MESSAGES = 99999

# DEPENDENCIES
def to_seconds(function):
    """
    Helper function for message send later.
    """
    def wrapper(*args):
        arg_list = list(args)
        if isinstance(arg_list[3], int):
            pass
        else:
            time_diff = datetime.strptime(arg_list[3], "%Y-%m-%d %X") - datetime.now()
            diff_in_secs = time_diff.total_seconds()
            arg_list[3] = diff_in_secs
        args = tuple(arg_list)
        return function(*args)
    return wrapper

def find_message_index(message_id, messages):
    """
    Find message index as messages often get deleted.
    """
    try:
        for index, message in enumerate(messages):
            if message['message_id'] == message_id:
                return index
        # Raise error if message cannot be found
        raise InputError('Message doesn\'t exist')
    except Exception:
        raise InputError

# FEATURES
def message_send(token, channel_id, message):
    """
    Send message in channel.
    """
    # Raise error if message is too long
    if len(message) > 1000:
        raise InputError('Message over 1000 words')
    database = DataBase()
    user_id = database.get_account_info(token)['u_id']
    channel = database.get_channel_info(channel_id)
    # Raise error is user_id is not part of channel.
    if user_id not in channel['members_id']:
        raise AccessError('Not a channel member')
    # Create message_id
    channel_id_str = str(NO_CHANNELS - channel_id)
    message_id = channel_id_str + str(channel['no_sent_messages']).zfill(5)
    message_id += str(user_id)
    message_id = int(message_id)
    # Create message_dict
    dt = datetime.now()
    timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())
    message_dict = {}
    message_dict['message_id'] = message_id
    message_dict['u_id'] = user_id
    message_dict['message'] = message
    message_dict['time_created'] = timestamp
    message_dict['reacts'] = [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}]
    message_dict['is_pinned'] = False
    channel['messages'] = [message_dict] + channel['messages']
    channel['no_sent_messages'] += 1
    database.close()
    return {
        'message_id': message_id,
    }

def message_remove(token, message_id):
    """
    Remove message in channel
    """
    database = DataBase()
    user_id = database.get_account_info(token)['u_id']
    channel_id = str(message_id)  
    channel_id = NO_CHANNELS - int(channel_id[0:5])
    channel = database.get_channel_info(channel_id)
    channel_msgs = database.get_channel_messages(channel_id)
    message_user_id = int(str(message_id)[10:])
    # Check users allowed to delete messages
    if user_id not in channel['owners_id'] and user_id != message_user_id:
        raise AccessError('Not a member of channel')
    # Check if message exists to delete in list
    message_index = find_message_index(message_id, channel_msgs)
    channel_msgs.pop(message_index)
    database.close()
    return {}

def message_edit(token, message_id, message):
    """
    Edit messages or delete them.
    """
    # Get channel which message_id attaches itself too
    database = DataBase()
    user_id = database.get_account_info(token)['u_id']
    channel_id = str(message_id)  
    channel_id = NO_CHANNELS - int(channel_id[0:5])
    channel = database.get_channel_info(channel_id)
    message_user_id = int(str(message_id)[10:])
    message_index = find_message_index(message_id, channel['messages'])
    # Error handling
    if user_id not in channel['owners_id'] and user_id != message_user_id:
        raise AccessError('Not member of channel')
    # Edit or delete message
    if message:
        channel['messages'][message_index]['message'] = message
    else:
        channel['messages'].pop(message_index)
    database.close()
    return {}

@to_seconds
def message_sendlater(token, channel_id, message, time_sent):
    '''
    Send message at set time
    Time_sent can be both integer and timestring
    '''
    #Error checking
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    if not channel or len(message) > 1000 or time_sent < 0:
        raise InputError
    if channel_member['u_id'] not in channel['members_id']:
        raise AccessError('Not a member in the channel')
    #Implementation
    with concurrent.futures.ThreadPoolExecutor(1) as exe:
        def sleep_for(secs):
            time.sleep(secs)
            return 1
        exe.submit(sleep_for, time_sent)
        future = exe.submit(message_send, token, channel_id, message)
        return_val = future.result()
        return return_val

def message_react(token, message_id, react_id):
    """
    Let users react to messages.
    """
    database = DataBase()
    channel_id = str(message_id)  
    channel_id = NO_CHANNELS - int(channel_id[0:5])
    channel_msgs = database.get_channel_messages(channel_id)
    message_index = find_message_index(message_id, channel_msgs)
    msg = channel_msgs[message_index]
    channel_member_id = database.get_account_info(token)['u_id']
    if react_id != 1 or channel_member_id in msg['reacts'][react_id-1]['u_ids']:
        raise InputError
    # Add react
    react = channel_msgs[message_index]['reacts'][react_id - 1]
    react['is_this_user_reacted'] = True
    react['u_ids'].append(database.get_account_info(token)['u_id'])
    database.close()
    return {}

def message_unreact(token, message_id, react_id):
    """
    User unreacts to message.
    """
    database = DataBase()
    channel_id = str(message_id)  
    channel_id = NO_CHANNELS - int(channel_id[0:5])
    channel_msgs = database.get_channel_messages(channel_id)
    message_index = find_message_index(message_id, channel_msgs)
    #Error checking
    msg = channel_msgs[message_index]
    channel_member_id = database.get_account_info(token)['u_id']
    if react_id != 1 or channel_member_id not in msg['reacts'][react_id-1]['u_ids']:
        raise InputError('Not valid react or member hasn\'t reacted')
    react = msg['reacts'][react_id - 1]
    if not react['is_this_user_reacted']:
        raise InputError('No reacts have been made')
    #Implementation
    react['u_ids'].remove(database.get_account_info(token)['u_id'])
    if not react['u_ids']:
        react['is_this_user_reacted'] = False
    database.close()
    return {}

def message_pin(token, message_id):
    """
    Pin messages.
    """
    database = DataBase()
    channel_id = str(message_id)  
    channel_id = NO_CHANNELS - int(channel_id[0:5])
    channel_msgs = database.get_channel_messages(channel_id)
    # Error Checking
    message_index = find_message_index(message_id, channel_msgs)
    msg = channel_msgs[message_index]
    channel = database.get_channel_info(channel_id)
    channel_member_id = database.get_account_info(token)['u_id']
    if channel_member_id not in channel['members_id']:
        raise AccessError('Not a member in the channel')
    if msg['is_pinned']:
        raise InputError('Message is already pinned')
    # Pin Message
    channel_msgs[message_index]['is_pinned'] = True
    database.close()
    return {}

def message_unpin(token, message_id):
    """
    Unpin messages.
    """
    database = DataBase()
    channel_id = str(message_id)  
    channel_id = NO_CHANNELS - int(channel_id[0:5])
    channel_msgs = database.get_channel_messages(channel_id)
    message_index = find_message_index(message_id, channel_msgs)
    # Error checking
    msg = channel_msgs[message_index]
    channel = database.get_channel_info(channel_id)
    channel_member_id = database.get_account_info(token)['u_id']
    if channel_member_id not in channel['members_id']:
        raise AccessError('Not a member in the channel')
    if not msg['is_pinned']:
        raise InputError('Message is already unpinnned')
    # Unpin messages
    channel_msgs[message_index]['is_pinned'] = False
    database.close()
    return {}
