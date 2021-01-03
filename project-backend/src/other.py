"""
By Navid Bhuiyan
Date: 29/09/2020

other.py implementations of functions.
"""

import json
from flockr_database_api import DataBase
from auth import USER_PERMISSIONS, OWNER_PERMISSIONS
from error import *

### DEPENDENCIES
def make_user_list_other(user_list):
    """
    Make member list for front-end to gather information on channel info.
    """
    member_list = []
    for user in user_list:
        temp_dict = {}
        temp_dict['u_id'] = user['u_id']
        temp_dict['name_first'] = user['name_first']
        temp_dict['name_last'] = user['name_last']
        temp_dict['profile_img_url'] = user['profile_img_url']
        member_list.append(temp_dict)
    return member_list

### FEATAURES
def clear():
    """
    Resets database
    """
    # Basic database structure
    database_dict = {
        'no_users': 0,
        'users': [],
        'no_channels': 0,
        'channels': [],
        'no_active_users': 0,
        'active_users':[]
     }
    database_name = "flockr_database.json"
    with open(database_name, 'w') as database:
        json.dump(database_dict, database, indent=4)

def users_all(token):
    """
    Get list of all users.
    """
    database = DataBase()
    users = make_user_list_other(database.database_dict['users'])
    return {'users': users}

def admin_userpermission_change(token, u_id, permission_id):
    """
    Change user permissions.
    """
    database = DataBase()
    user = database.get_info_from_id(u_id)
    admin = database.get_account_info(token)
    # Error checking
    if not user or (permission_id != USER_PERMISSIONS and permission_id != OWNER_PERMISSIONS):
        raise InputError
    if admin['permissions'] != OWNER_PERMISSIONS:
        raise AccessError
    user['permissions'] = permission_id
    database.close()
    return{}

def search(token, query_str):
    """
    Searches messages for query_str
    """
    database = DataBase()
    user_id = database.get_account_info(token)['u_id']
    channels = database.database_dict['channels']
    messages_list = []
    for channel in channels:
        messages = channel['messages']
        if user_id in channel['members_id']:
            for message in messages:
                if query_str in message['message']:
                    messages_list.append(message)
    database.close()
    return {
        'messages': messages_list
    }