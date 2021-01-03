"""
Author: Hongji Liu / TONG LIU
Date:29/09/2020

This file will be used to test the points of failure for the channels.py function
is meant to implemented according to spec.
"""

import pytest
from auth import auth_register
from channels import channels_create, channels_list, channels_listall
from error import InputError
from other import clear
from flockr_database_api import DataBase

@pytest.fixture
def global_variables():
    """
    Variables to be used in all functions.
    """
    try:
        pytest.global_token_1 = auth_register("test1@email.com", "password", "name_first", "name_last")
        pytest.global_token_2 = auth_register("test2@email.com", "password", "name_first", "name_last")
    except InputError:
        database = DataBase()
        pytest.global_token_1 = database.database_dict['active_users'][0]
        pytest.global_token_2 = database.database_dict['active_users'][1]

def test_channels_create(global_variables):
    """
    Test that the channel_create function works as expected.
    """
    # Check that the code successfully generated a channel
    created_channel = channels_create(pytest.global_token_1['token'], "channel_0", True)
    assert isinstance(created_channel, dict)

def test_channels_create_name_error(global_variables):
    """
    Trigger create name error i.e. name is more than 20 chars.
    """
    # Update global token variables and checks rejection of name
    with pytest.raises(InputError):
        channels_create(pytest.global_token_2, "a" * 21, True)

def test_channels_list_all(global_variables):
    """
    Test that the listall function works as expected.
    """
    # Uses previous test token and checks the list
    channels_temp_list = channels_listall(pytest.global_token_1['token'])
    assert channels_temp_list['channels'][0]['name'] == "channel_0"

def test_no_channel_in_channels_list(global_variables):
    """
    Trigger non-existent channel error.
    """
    # Not in any channels, so should raise an internal error
    with pytest.raises(Exception):
        channels_list(pytest.global_token_2)
 
def test_channel_list(global_variables):
    """
    Lists channels user is only in.
    """
    channels_create(pytest.global_token_2['token'], "channel_1", True)
    channels_temp_list = channels_list(pytest.global_token_2['token'])
    assert channels_temp_list['channels'][0]['name'] == "channel_1"

def test_clear_database():
    """
    Reset database.
    """
    clear()
