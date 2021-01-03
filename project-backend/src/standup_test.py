"""
By Navid Bhuiyan
Date: 15/11/2020

Tests for standup.py functions in success and error cases.
"""

import time
from flockr_database_api import DataBase
from error import AccessError, InputError
from channels import channels_create
from channel import channel_invite
from auth import auth_register
from standup import *
from other import *
from message import message_send
import pytest

UNIQUE_ID = 0

@pytest.fixture
def standup_init():
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

### SUCCESS CASES
def test_standup_active_not_active(standup_init):
    result = standup_active(standup_init[0]['token'], standup_init[2])
    assert not result['is_active']

def test_standup_active_then_not_active(standup_init):
    standup_start(standup_init[0]['token'], standup_init[2], 10)
    time.sleep(11)
    # Not active
    result = standup_active(standup_init[0]['token'], standup_init[2])
    assert not result['is_active']

def test_standup_active(standup_init):
    standup_start(standup_init[0]['token'], standup_init[2], 10)
    result = standup_active(standup_init[0]['token'], standup_init[2])
    assert result['is_active']

def test_standup_start(standup_init):
    result = standup_start(standup_init[0]['token'], standup_init[2], 10)
    assert result['time_finish']

def test_standup_send_message(standup_init):
    standup_start(standup_init[0]['token'], standup_init[2], 10)
    result = standup_send(standup_init[0]['token'], standup_init[2], "heyo")
    assert result == {}

def test_standup_active_ends_and_sends_message(standup_init):
    standup_start(standup_init[0]['token'], standup_init[2], 10)
    standup_send(standup_init[0]['token'], standup_init[2], "heyo")
    standup_send(standup_init[0]['token'], standup_init[2], "heyo0000")
    time.sleep(11)
    # Not active
    result = standup_active(standup_init[0]['token'], standup_init[2])
    assert not result['is_active']
    database = DataBase()
    messages = database.get_channel_info(standup_init[2])['messages']
    assert messages[0]

# Failcases
def test_standup_start_invalid_channel_id(standup_init):
    with pytest.raises(InputError):
        standup_start(standup_init[0]['token'], standup_init[2] + 1, 10)

def test_standup_start_standup_in_session(standup_init):
    standup_start(standup_init[0]['token'], standup_init[2], 10)
    with pytest.raises(InputError):
        standup_start(standup_init[0]['token'], standup_init[2], 20)

def test_standup_active_invalid_channel_id(standup_init):
    with pytest.raises(InputError):
        standup_active(standup_init[0]['token'], standup_init[2] + 1)

def test_standup_send_invalid_channel_id(standup_init):
    with pytest.raises(InputError):
        standup_send(standup_init[0]['token'], standup_init[2] + 1, "message")

def test_standup_send_over_1000_char(standup_init):
    with pytest.raises(InputError):
        standup_send(standup_init[0]['token'], standup_init[2], "message" * 1000)

def test_standup_send_when_no_session(standup_init):
    with pytest.raises(InputError):
        standup_send(standup_init[0]['token'], standup_init[2], "message")

def test_standup_send_not_member(standup_init):
    standup_start(standup_init[0]['token'], standup_init[2], 10)
    with pytest.raises(AccessError):
        standup_send(standup_init[3]['token'], standup_init[2], "message")

def test_clear():
    clear()
