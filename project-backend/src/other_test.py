"""
By Kenneth Liu
Date: 14/11/2020

Tests for other.py functions.
"""

from flockr_database_api import DataBase
from error import AccessError, InputError
from channels import channels_create
from channel import channel_invite
from auth import auth_register
from other import *
from message import message_send
import pytest

UNIQUE_ID = 0

@pytest.fixture
def other_init():
    '''
    fixture for all message tests
    '''
    global UNIQUE_ID
    email_a = f"testauthorised{UNIQUE_ID}@gmail.com"
    email_i = f"testinvited{UNIQUE_ID}@gmail.com"
    email_u = f"testunauthorised{UNIQUE_ID}@gmail.com"
    #Generate test u_ids and tokens
    id_and_token_authorised = auth_register(
        email_a,
        "goodpassword",
        "test_authorised",
        "test_authorised"
    )
    id_and_token_invited = auth_register(
        email_i,
        "goodpassword",
        "test_invited",
        "test_invited"
    )
    id_and_token_unauthorised = auth_register(
        email_u,
        "goodpassword",
        "test_unauthorised",
        "test_unauthorised"
    )
    #Generate a test channel_id
    test_channel_id = channels_create(
        id_and_token_authorised['token'],
        f"test_channel{UNIQUE_ID}",
        False
    )
    #Initialise a user as a member of the channel
    channel_invite(
        id_and_token_authorised['token'],
        test_channel_id['channel_id'],
        id_and_token_invited['u_id']
    )
    UNIQUE_ID += 1
    return [
        id_and_token_authorised,
        id_and_token_invited,
        test_channel_id['channel_id'],
        id_and_token_unauthorised
    ]

def test_users_all(other_init):
    ret_dict = users_all(other_init[0]['token'])
    assert other_init[0]['u_id'] == ret_dict['users'][0]['u_id']

def test_perm_change(other_init):
    database = DataBase()
    admin = database.get_account_info(other_init[0]['token'])
    admin['permissions'] = 1
    database.close()
    result = admin_userpermission_change(other_init[0]['token'], other_init[1]['u_id'], 1)
    assert result == {}

def test_perm_change_input_error(other_init):
    database = DataBase()
    admin = database.get_account_info(other_init[0]['token'])
    admin['permissions'] = 1
    database.close()
    with pytest.raises(InputError):
        admin_userpermission_change(other_init[0]['token'], other_init[1]['u_id'], 0)

def test_perm_change_access_error(other_init):
    database = DataBase()
    admin = database.get_account_info(other_init[0]['token'])
    admin['permissions'] = 2
    database.close()
    with pytest.raises(AccessError):
        admin_userpermission_change(other_init[0]['token'], other_init[1]['u_id'], 1)

def test_search(other_init):
    message_send(other_init[0]['token'], other_init[2], "message")
    message_send(other_init[0]['token'], other_init[2], "message1")
    message_send(other_init[0]['token'], other_init[2], "message2")
    message_send(other_init[0]['token'], other_init[2], "message3")
    message_send(other_init[0]['token'], other_init[2], "message4")
    message_send(other_init[0]['token'], other_init[2], "message5")
    message_send(other_init[0]['token'], other_init[2], "message6")
    message_send(other_init[0]['token'], other_init[2], "message7")
    ret_dict = search(other_init[0]['token'], 'message7')
    print(ret_dict)
    assert 'message7' in ret_dict['messages'][0]['message']

def test_clear_database():
    """
    Reset database.
    """
    clear()
