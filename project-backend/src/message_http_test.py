"""
By Navid Bhuiyan
Date: 26/10/2020

Creating tests to check the server integration of the backend into the frontend
for the auth.py functions.

"""
from auth import auth_register
from error import InputError
from other import clear
from flockr_database_api import DataBase
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
from auth import auth_register
from error import AccessError, InputError
from channels import channels_create
from channel import channel_invite
from message import *

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

@pytest.fixture
def url():
    """
    Start url of server and get url for tests.
    """
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

def test_message_send(url, message_init):
    """
    Test sending message.
    """
    test_url = url + "/message/send"
    json_package = {
        'token': message_init[0]['token'],
        'channel_id': message_init[2],
        'message': "hello"
    }
    response = requests.post(test_url, json=json_package)
    print(response.text)
    assert json.loads(response.text)['message_id']

def test_message_edit(url, message_init):
    """
    Test sending message.
    """
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    response = requests.put(f"{url}message/edit", json={
        'token': message_init[0]['token'],
        'message_id': m_id,
        'message': "different message"
    })
    print(response.text)
    assert json.loads(response.text) == {}

def test_message_remove(url, message_init):
    """
    Test removing message.
    """
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    response = requests.delete(f"{url}message/remove", json={
        'token': message_init[0]['token'],
        'message_id': m_id
    })
    print(response.text)
    assert json.loads(response.text) == {}

#Iteration 3 features

def test_message_sendlater_remote(url, message_init):
    response = requests.post(f'{url}message/sendlater', json={
        'token' : message_init[0]['token'],
        'channel_id' : message_init[2],
        'message' : 'message',
        'time_sent' : 1
    
    })
    assert json.loads(response.text)['message_id']
    
    
def test_message_react_remote(url, message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    requests.post(f'{url}message/react', json={
        'token' : message_init[0]['token'],
        'message_id' : m_id,
        'react_id' : 1
    
    })
    database = DataBase()
    assert message_init[0]['u_id'] in database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['reacts'][0]['u_ids']
    

def test_message_unreact_remote(url, message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_react(message_init[0]['token'], m_id, 1)
    requests.post(f'{url}message/unreact', json={
        'token' : message_init[0]['token'],
        'message_id' : m_id,
        'react_id' : 1
    
    })
    database = DataBase()
    assert message_init[0]['u_id'] not in database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['reacts'][0]['u_ids']
    
def test_message_pin_remote(url, message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    requests.post(f'{url}message/pin', json={
        'token' : message_init[0]['token'],
        'message_id' : m_id,
    
    })
    database = DataBase()
    assert database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['is_pinned'] == True

def test_message_unpin_remote(url, message_init):
    m_id = message_send(message_init[0]['token'], message_init[2], "message")['message_id']
    message_pin(message_init[0]['token'], m_id)
    requests.post(f'{url}message/unpin', json={
        'token' : message_init[0]['token'],
        'message_id' : m_id,
    
    })
    database = DataBase()
    assert database.get_channel_messages(message_init[2])[int(str(m_id)[5:10])]['is_pinned'] != True

def test_clear(url):
    test_url = url + "/clear"
    requests.delete(test_url)
