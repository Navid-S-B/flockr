"""
By Navid Bhuiyan
Date: 15/11/2020

Functions to allow standup time to occur
"""
from time import sleep
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from flockr_database_api import DataBase
from message import message_send
from error import *

### FEATURES
def standup_start(token, channel_id, length):
    """
    Start standup.
    """
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    if not channel:
        raise InputError('Invalid channel')
    if channel['standup']['end'] is not None:
        raise InputError('Standup is active')
    dt = datetime.now()
    seconds_added = timedelta(seconds = length)
    dt2 = dt + seconds_added
    time_finish = int(dt2.replace(tzinfo=timezone.utc).timestamp())
    channel['standup']['end'] = time_finish
    channel['standup']['user_token'] = token
    database.close()
    return {
        'time_finish': time_finish
    }

def standup_active(token, channel_id):
    """
    Check if standup is in session.
    """
    # Add delay to get access to database
    sleep(0.1)
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    if not channel:
        raise InputError('inalid channel')
    active_dict = {}
    dt = datetime.now()
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    # Not active
    if not channel['standup']['end']:
        active_dict['is_active'] = False
        active_dict['time_finish'] = None
        return active_dict
    elif timestamp >= channel['standup']['end']:
        if channel['standup']['message']:
            message_send(channel['standup']['user_token'], channel_id, channel['standup']['message'])
        database = DataBase()
        channel = database.get_channel_info(channel_id)
        channel['standup']['end'] = None
        channel['standup']['message'] = ""
        channel['standup']['user_token'] = None
        active_dict['is_active'] = False
        active_dict['time_finish'] = None
        database.close()
        return active_dict
    # Active
    active_dict['is_active'] = True
    active_dict['time_finish'] = channel['standup']['end']
    return active_dict

def standup_send(token, channel_id, message):
    """
    Send messages on a queue during a standup
    """
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    # Error checking
    if not channel:
        raise InputError('Inalid channel')
    if len(message) > 1000:
        raise InputError('Message over 1000 characters')
    if channel['standup']['end'] is None:
        raise InputError('Standup is not active')
    user_account = database.get_account_info(token)
    user_id = user_account['u_id']
    if user_id not in channel['members_id']:
        raise AccessError('Not a member of this channel')
    # Adding message
    if channel['standup']['message'] == "":
        channel['standup']['message'] = f"{user_account['handle_str']}: {message}"
    else:
        channel['standup']['message'] = channel['standup']['message'] + f"\n{user_account['handle_str']}: {message}"
    database.close()
    return {}
