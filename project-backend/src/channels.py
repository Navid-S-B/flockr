"""
Author: TONG LIU/ Hongji Liu
Date: 01/10/2020

Channels_functions in itration1

Assumptions for channels in itration1:
We assums that channel_id is created depend on the length of channels in database.
Assums that token is 'token' in iteration1.
"""
from flockr_database_api import DataBase
from auth import OWNER_PERMISSIONS
from error import InputError, AccessError

# DEPENDENCIES
def make_channels_list(channel_list):
    """
    Strip channel information to send essential information 
    to frontend.
    """
    new_channel_list = []
    for channel in channel_list:
        channel_dict = {}
        channel_dict['channel_id'] = channel['channel_id']
        channel_dict['name'] = channel['name']
        new_channel_list.append(channel_dict)
    return new_channel_list

# FEATURES
def channels_list(token):
    """
    Return the user the list of channels they are in.
    """
    # Open database
    database = DataBase()
    channel_member = database.get_account_info(token)
    channel_member_u_id = channel_member['u_id']
    # Get member_channels
    member_channels = []
    for channel in database.database_dict['channels']:
        if channel_member_u_id in channel['members_id']:
            member_channels.append(channel)
    member_channels = make_channels_list(member_channels)
    return {'channels': member_channels}

def channels_listall(token):
    """
    Admin feature to know all of the channels.
    """
    # Need to change token structure.
    database = DataBase()
    current_channels = database.database_dict['channels']
    current_channels = make_channels_list(current_channels)
    return {'channels': current_channels}

def channels_create(token, name, is_public):
    """
    Create a channel for a user.
    """
    if len(name) > 20:
        raise InputError
    database = DataBase()
    # Get user
    channel_creator = database.get_account_info(token)
    # Get Channel ID and change number of channels
    database.database_dict['no_channels'] += 1
    channel_id = database.database_dict['no_channels']
    #We assume that channel_id start from 0->1->2->3->4->...
    new_channel = {
        'standup': {
            'user_token': None,
            'end': None,
            'message': ""
        },
        'creator_token': channel_creator['u_id'],
        'name': name,
        'channel_id': channel_id,
        'is_public': is_public,
        'owners_id': [],
        'members_id': [],
        'no_sent_messages': 0,
        'messages': []
    }
    new_channel['members_id'].append(channel_creator['u_id'])
    new_channel['owners_id'].append(channel_creator['u_id'])
    database.database_dict['channels'].append(new_channel)
    database.close()
    return {'channel_id': channel_id}
