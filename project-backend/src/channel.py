'''
Author: Haixiang (Kenneth) Liu and Navid Bhuiyan
Date of creation: 21/09/2020
Description: All channel functions as set by the spec.
'''
from flockr_database_api import DataBase
from auth import OWNER_PERMISSIONS
from error import InputError, AccessError

# DEPENDENCIES
def make_user_list(u_id_list):
    """
    Make member list for front-end to gather information on channel info.
    """
    database = DataBase()
    member_list = []
    for u_id in u_id_list:
        temp_dict = {}
        u_dict = database.database_dict['users'][u_id]
        temp_dict['u_id'] = u_id
        temp_dict['name_first'] = u_dict['name_first']
        temp_dict['name_last'] = u_dict['name_last']
        temp_dict['profile_img_url'] = u_dict['profile_img_url']
        member_list.append(temp_dict)
    return member_list

# FEATURES
def channel_invite(token, channel_id, u_id):
    """
    Invite registered users to channels.
    """
    # Open database and gather channel info and member info
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    add_member = database.get_info_from_id(u_id)
    # Error testing
    if not channel or not add_member:
        raise InputError('Channel doesn\'t exist or member doesn\'t exist')
    if channel_member['permissions'] != OWNER_PERMISSIONS:
        if channel_member['u_id'] not in channel['members_id']:
            raise AccessError('Not a member in the channel')
    # Update database
    channel['members_id'].append(u_id)
    database.close()
    return {}

def channel_details(token, channel_id):
    """
    Obtain channel details from database with a valid token.
    """
    # Open database amd gather important channel info for error checking
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    # Error checking
    if not channel:
        raise InputError('Channel does not exist')
    if channel_member['permissions'] != OWNER_PERMISSIONS:
        if channel_member['u_id'] not in channel['members_id']:
            raise AccessError('Not a member in the channel')
    result = {}
    result['name'] = channel['name']
    result['owner_members'] = make_user_list(channel['owners_id'])
    result['all_members'] = make_user_list(channel['members_id'])
    return result

def channel_messages(token, channel_id, start):
    """
    Obtain message chain for user in a channel.
    """
    # Open database to get info for error testing
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    # Error checking
    if not channel:
        raise InputError('Channel does not exist')
    if channel_member['permissions'] != OWNER_PERMISSIONS:
        if channel_member['u_id'] not in channel['members_id']:
            raise AccessError('Not a member in the channel')
    if start >= len(channel['messages']) and start != 0:
        raise InputError('Non-existent message')
    result = {}
    result['start'] = start
    # Use slicing and try statement to slice list of messages
    if start + 50 > len(channel['messages']):
        result['end'] = -1
    else:
        result['end'] = start + 50
    result['messages'] = channel['messages'][start:start + 50]
    return result

def channel_leave(token, channel_id):
    """
    Remove user from channel with valid token.
    """
    # Get info from database for error checking
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    # Error checking
    if not channel:
        raise InputError('Channel does not exist')
    if channel_member['permissions'] != OWNER_PERMISSIONS:
        if channel_member['u_id'] not in channel['members_id']:
            raise AccessError('Not a member in the channel')
    # Change database
    channel['members_id'].remove(channel_member['u_id'])
    database.close()
    return {}

def channel_join(token, channel_id):
    """
    Add valid user to channel.
    """
    # Get info from database for error checking
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    joining_member = database.get_account_info(token)
    # Error checking
    if not channel:
        raise InputError('Channel does not exist')
    if joining_member['permissions'] != OWNER_PERMISSIONS:
        if not channel['is_public']:
            raise AccessError('Channel is private')
    # Update database
    channel['members_id'].append(joining_member['u_id'])
    database.close()
    return {}

def channel_addowner(token, channel_id, u_id):
    """
    Add channel ownwers for user with valid channel ownership.
    """
    # Get info for error checking
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    # Error checking
    if not channel or u_id in channel['owners_id']:
        raise InputError('Channel does not exist or user is not an owner')
    if channel_member['permissions'] != OWNER_PERMISSIONS:
        if channel_member['u_id'] not in channel['owners_id']:
            raise AccessError('Not an owner of the channel')
    # Update database
    channel['owners_id'].append(u_id)
    database.close()
    return {}

def channel_removeowner(token, channel_id, u_id):
    """
    Remove the ownwer of channel with user with valid channel ownership.
    """
    # Get info for error checking
    database = DataBase()
    channel = database.get_channel_info(channel_id)
    channel_member = database.get_account_info(token)
    # Check for errors
    if not channel or u_id not in channel['owners_id']:
        raise InputError('Channel does not exist or user is not an owner')
    if (channel_member['u_id'] not in channel['owners_id'] and 
        channel_member['permissions'] != OWNER_PERMISSIONS):
        raise AccessError('Not an owner of this channel')
    # Update database
    channel['owners_id'].remove(u_id)
    database.close()
    return {}
