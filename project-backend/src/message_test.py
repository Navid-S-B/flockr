'''
By Kenneth Liu
Date: 12/11/2020

Comment By Navid:
The test suite has its flaws in terms of checking the database and checking the
messagers properties as the old indexing system relied on the removal of messages
to make messages empty. However the new system does account for this given the messages.py
has a find_message function. These tests do work as they only test for a new channel
with one message inside them.

The function called test_multiple_msg() should test everything nicely.

'''
import pytest
import time
from auth import auth_register
from error import AccessError, InputError
from channels import channels_create
from other import clear
from flockr_database_api import DataBase
from channel import channel_invite
from message import *
import datetime

UNIQUE_ID = 0

@pytest.fixture
def message_init():
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
        "goodword",
        "test_authorised",
        "test_authorised"
    )
    id_and_token_invited = auth_register(
        email_i,
        "goodword",
        "test_invited",
        "test_invited"
    )
    id_and_token_unauthorised = auth_register(
        email_u,
        "goodword",
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

# Test Success Cases
def test_message_sendlater(message_init):
    m_id = message_sendlater(message_init[0]['token'], message_init[2], "message", 2)['message_id']
    assert m_id

def test_message_sendlater_invalid_channel_id(message_init):
    with pytest.raises(InputError):
       message_sendlater(message_init[0]['token'], -2, "message", 5)

def test_message_send(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    assert m_id

def test_message_remove(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    response = message_remove(message_init[0]['token'], m_id)
    assert response == {}

def test_message_edit(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    # Edited
    message_edit(message_init[0]['token'], m_id, "edited")
    # Deleted
    message_edit(message_init[0]['token'], m_id, "")
    database = DataBase()
    assert len(database.get_channel_messages(message_init[2])) == 0

def test_message_react(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_react(message_init[0]['token'], m_id, 1)
    database = DataBase()
    assert message_init[0]['u_id'] in database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['reacts'][0]['u_ids']

def test_message_unpin(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_pin(message_init[0]['token'], m_id)
    message_unpin(message_init[0]['token'], m_id)
    database = DataBase()
    assert database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['is_pinned'] != True

def test_message_unreact(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_react(message_init[0]['token'], m_id, 1)
    message_unreact(message_init[0]['token'], m_id, 1)
    database = DataBase()
    assert message_init[0]['u_id'] not in database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['reacts'][0]['u_ids']

def test_message_pin(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_pin(message_init[0]['token'], m_id)
    database = DataBase()
    assert database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['is_pinned'] == True

# Error Cases
def test_messaage_invalid_message_id(message_init):
    for i in range(10):
        print(i)
        message_send(message_init[0]['token'], message_init[2], "message")
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_remove(message_init[0]['token'], m_id)
    with pytest.raises(InputError):
        message_edit(message_init[0]['token'], m_id, "hehe")

def test_messages_invalid_unreact(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(InputError):
        message_unreact(message_init[0]['token'], m_id, 1)

def test_messages_invalid_pin(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_pin(message_init[3]['token'], m_id)

def test_messages_invalid_unpin(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_unpin(message_init[3]['token'], m_id)

def test_message_sendlater_message_too_long(message_init):
    with pytest.raises(InputError):
        message_sendlater(message_init[0]['token'], message_init[2], "message"*1000, 5)
    
def test_message_sendlater_you_think_this_is_tenet_huh(message_init):
    with pytest.raises(InputError):
        message_sendlater(message_init[0]['token'], message_init[2], "message", -5)

def test_message_sendlater_user_not_a_member(message_init):
    with pytest.raises(AccessError):
        message_sendlater(message_init[3]['token'], message_init[2], "message", 5)

def test_message_sendlater_with_fomatted_time(message_init):
    m_id = message_sendlater(message_init[0]['token'], message_init[2], "message", str(datetime.datetime.now().replace(microsecond = 0)+datetime.timedelta(seconds = 2)))['message_id']
    database = DataBase()
    assert database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['message_id'] == m_id

def test_message_send_length_over_1000(message_init):
    with pytest.raises(InputError):
        message_send(message_init[0]['token'], message_init[2], "m" * 1001)

def test_message_not_channel_member(message_init):
    with pytest.raises(AccessError):
        message_send(message_init[3]['token'], message_init[2], "message")

def test_message_remove_not_channel_member(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_remove(message_init[3]['token'], m_id)

def test_message_edit_not_channel_member(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_edit(message_init[3]['token'], m_id, "new_message")

def test_message_react_invalid_message_id(message_init):
    with pytest.raises(InputError):
        message_react(message_init[0]['token'], '0'*4+'1'+'9'*5+'10', 1)

def test_message_react_invalid_react_id(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(InputError):
        message_react(message_init[0]['token'], m_id, -1)

def test_message_react_already_reacted(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_react(message_init[0]['token'], m_id, 1)
    with pytest.raises(InputError):
        message_react(message_init[0]['token'], m_id, 1) 

def test_message_unreact_invalid_message_id(message_init):
    with pytest.raises(InputError):
        message_unreact(message_init[0]['token'], '0'*4+'1'+'9'*5+'10', 1)
    
def test_message_unreact_invalid_react_id(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_react(message_init[0]['token'], m_id, 1)
    with pytest.raises(InputError):
        message_unreact(message_init[0]['token'], m_id, -1)

def test_message_unreact_not_reacted(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(InputError):
        message_unreact(message_init[0]['token'], m_id, 1) 

def test_message_pin_invalid_message_id(message_init):
    with pytest.raises(InputError):
        message_pin(message_init[0]['token'], '0'*4+'1'+'9'*5+'10')
        
def test_message_pin_already_pinned(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_pin(message_init[0]['token'], m_id)
    with pytest.raises(InputError):
        message_pin(message_init[0]['token'], m_id)  

def test_message_pin_user_not_a_member(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_pin(message_init[3]['token'], m_id) 
    
def test_message_pin_not_owner(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_pin(message_init[3]['token'], m_id)  

def test_message_unpin_invalid_message_id(message_init):
    with pytest.raises(InputError):
        message_unpin(message_init[0]['token'], '0'*4+'1'+'9'*5+'10')
     
def test_message_unpin_already_unpinned(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(InputError):
        message_unpin(message_init[0]['token'], m_id)
    
def test_message_unpin_user_not_a_member(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_unpin(message_init[3]['token'], m_id)
    
def test_message_unpin_not_owner(message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    with pytest.raises(AccessError):
        message_unpin(message_init[3]['token'], m_id)

def test_clear():
    clear()
