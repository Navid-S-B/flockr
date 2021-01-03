"""
By Navid Bhuiyan
Date: 15/11/2020

Creating htttp tests for success cases.
"""
import re
import json
import requests
import pytest
import signal
from other import clear
from flockr_database_api import DataBase
from subprocess import Popen, PIPE
from time import sleep
from auth import auth_register
from auth import OWNER_PERMISSIONS
from error import *
from channels import channels_create
from channel import channel_invite
from standup import *

@pytest.fixture
def url():
    """
    Start url of server.
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

### SUCCESS CASES
def test_admin_user_permission_change(url, other_init):
    pathname = "admin/userpermission/change"
    test_url = url + pathname
    json_package = {
        "token": other_init[0]['token'],
        "u_id": other_init[1]['u_id'],
        "permission_id": 1 
    }
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text) == {}

def test_users_all(url, other_init):
    pathname = "users/all"
    test_url = url + pathname
    response = requests.get(test_url + f"?token={other_init[0]['token']}")
    assert json.loads(response.text)['users']

def test_search(url, other_init):
    pathname = "search"
    test_url = url + pathname
    response = requests.get(test_url + f"?token={other_init[0]['token']}&query_str=message")
    assert json.loads(response.text)['messages'] == []

def test_clear():
    clear()