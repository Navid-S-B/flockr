'''
Author: Haixiang (Kenneth) Liu
Date of creation: 21/09/2020
Description: A test suite for channel functions

Last edit: 21/10/2020
Description: Added black-box http tests
'''

from subprocess import Popen, PIPE
from time import sleep
import re
import urllib
import signal
import requests
import pytest
from auth import auth_register
from error import AccessError, InputError
from channel import channel_invite
from channel import channel_details
from channel import channel_messages
from channel import channel_leave
from channel import channel_join
from channel import channel_addowner
from channel import channel_removeowner
from channels import channels_create
from other import clear
from flockr_database_api import DataBase
from message import *

UNIQUE_ID = 0

@pytest.fixture
def channel_init():
    '''
    fixture for all channel tests
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


### LOGIC TESTS
def test_owner_permission(channel_init):
    result = channel_details(channel_init[0]['token'], channel_init[2])
    result1 = channel_messages(channel_init[0]['token'], channel_init[2], 0)
    new_channel = channels_create(channel_init[3]['token'], "new_channel", False)
    result2 = channel_join(channel_init[0]['token'], new_channel['channel_id'])
    result3 = channel_removeowner(channel_init[0]['token'], new_channel['channel_id'], channel_init[3]['u_id'])
    result4 = channel_addowner(channel_init[0]['token'], new_channel['channel_id'], channel_init[3]['u_id'])
    result5 = channel_leave(channel_init[0]['token'], new_channel['channel_id'])
    assert result
    assert result1
    assert isinstance(result2, dict)  
    assert isinstance(result3, dict)
    assert isinstance(result4, dict)
    assert isinstance(result5, dict)

def channel_removeowner_owner(channel_init):
    channel_addowner(channel_init[0]['token'], channel_init[2], channel_init[3]['u_id'])
    result = channel_removeowner(channel_init[3]['token'], channel_init[2], channel_init[0]['u_id'])
    result = channel_removeowner(channel_init[0]['token'], channel_init[2], channel_init[3]['u_id'])
    assert isinstance(result, dict)

def test_channel_invite_unauthorised_invitation(channel_init):
    '''
    test_channel_invite_unauthorised_invitation
    '''
    with pytest.raises(AccessError):
        channel_invite(channel_init[3]['token'], channel_init[2], channel_init[3]['u_id'])

def test_channel_invite_empty(channel_init):
    '''
    test_channel_invite_empty
    '''
    with pytest.raises(InputError):
        #An empty string is definitely invalid for both channel_id and u_id
        channel_invite(channel_init[3]['token'], "", "")

def test_channel_invite_invalid_channel(channel_init):
    '''
    test_channel_invite_invalid_channel
    '''
    with pytest.raises(InputError):
        #Test with valid and authorised token & u_id
        channel_invite(channel_init[0]['token'], "", channel_init[3]['u_id'])

def test_channel_invite_invalid_user(channel_init):
    '''
    test_channel_invite_invalid_user
    '''
    with pytest.raises(InputError):
        #Test with valid channel_id
        channel_invite(channel_init[0]['token'], channel_init[2], "")

def test_channel_details(channel_init):
    '''
    test_channel_details_unauthorised_user
    '''
    result = channel_details(channel_init[0]['token'], channel_init[2])
    assert 'test_channel' in result['name']

def test_channel_details_unauthorised_user(channel_init):
    '''
    test_channel_details_unauthorised_user
    '''
    with pytest.raises(AccessError):
        #Test with valid channel_id
        channel_details(channel_init[3]['token'], channel_init[2])

def test_channel_messages_invalid_channel(channel_init):
    '''
    test_channel_messages_invalid_channel
    '''
    with pytest.raises(InputError):
        #Test with valid user and index
        channel_messages(channel_init[0]['token'], "", 0)

def test_channel_messages_invalid_index(channel_init):
    '''
    test_channel_messages_invalid_index
    '''
    with pytest.raises(InputError):
        #Test with valid user and channel_id
        channel_messages(channel_init[0]['token'], channel_init[2], 1)

def test_channel_messages_invalid_user(channel_init):
    '''
    test_channel_messages_invalid_user
    '''
    with pytest.raises(AccessError):
        #Test with valid index and channel_id
        channel_messages(channel_init[3]['token'], channel_init[2], 0)

def test_channel_leave(channel_init):
    '''
    test_channel_leave_invalid_channel
    '''
    channel_leave(channel_init[0]['token'], channel_init[2])

def test_channel_leave_invalid_channel(channel_init):
    '''
    test_channel_leave_invalid_channel
    '''
    with pytest.raises(InputError):
        #Test with valid user
        channel_leave(channel_init[0]['token'], "")

def test_channel_leave_invalid_user(channel_init):
    '''
    test_channel_leave_invalid_user
    '''
    with pytest.raises(AccessError):
        #Test with valid channel_id
        channel_leave(channel_init[3]['token'], channel_init[2])

def test_channel_join(channel_init):
    '''
    test_channel_join_invalid_channel
    '''
    c_id = channels_create(channel_init[0]['token'], "public_channel",True)
    channel_join(channel_init[3]['token'], c_id['channel_id'])

def test_channel_join_invalid_channel(channel_init):
    '''
    test_channel_join_invalid_channel
    '''
    with pytest.raises(InputError):
        #Test with valid user
        channel_join(channel_init[0]['token'], "")

def test_channel_join_private(channel_init):
    '''
    test_channel_join_private
    '''
    with pytest.raises(AccessError):
        #Test with valid channel_id
        channel_join(channel_init[3]['token'], channel_init[2])

def test_channel_addowner(channel_init):
    '''
    test_channel_addowner_invalid_channel
    '''
    channel_addowner(channel_init[0]['token'], channel_init[2],channel_init[1]['u_id'])

def test_channel_addowner_invalid_channel(channel_init):
    '''
    test_channel_addowner_invalid_channel
    '''
    with pytest.raises(InputError):
        #Test with valid user
        channel_addowner(channel_init[0]['token'], "",channel_init[1]['u_id'])

def test_channel_addowner_already_owner(channel_init):
    '''
    test_channel_addowner_already_owner
    '''
    with pytest.raises(InputError):
        #Test by granting the owner himself ownership
        channel_addowner(channel_init[0]['token'], channel_init[2],channel_init[0]['u_id'])

def test_channel_addowner_not_owner(channel_init):
    '''
    test_channel_addowner_not_owner
    '''
    with pytest.raises(AccessError):
        #Test by granting a member himself ownership
        channel_addowner(channel_init[1]['token'], channel_init[2],channel_init[1]['u_id'])

def test_channel_removeowner_invalid_channel(channel_init):
    '''
    test_channel_removeowner_invalid_channel
    '''
    with pytest.raises(InputError):
        channel_removeowner(channel_init[0]['token'], "",channel_init[0]['u_id'])

def test_channel_removeowner_not_owner(channel_init):
    '''
    test_channel_removeowner_not_owner
    '''
    with pytest.raises(InputError):
        channel_removeowner(channel_init[0]['token'], channel_init[2], channel_init[1]['u_id'])

def test_channel_removeowner_unauthorised_action(channel_init):
    '''
    test_channel_removeowner_unauthorised_action
    '''
    with pytest.raises(AccessError):
        channel_removeowner(channel_init[1]['token'], channel_init[2],channel_init[0]['u_id'])

def test_channel_details_invalid_channel(channel_init):
    '''
    test_channel_details_invalid_channel
    '''
    with pytest.raises(InputError):
        #Test with valid user
        channel_details(channel_init[0]['token'], "")

# HTTP TESTSs
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

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    assert url.startswith("http")

def test_channel_invite_remote(url, channel_init):
    '''
    test_channel_invite_remote
    '''
    requests.post(f'{url}channel/invite', json={
        'token':channel_init[0]['token'],
        'channel_id':channel_init[2],
        'u_id':channel_init[3]['u_id']
    })
    database = DataBase()
    assert channel_init[3]['u_id'] in database.get_channel_info(channel_init[2])['members_id']

def test_channel_details_remote(channel_init, url):
    '''
    test_channel_details_remote
    '''
    query_string = urllib.parse.urlencode({
        'token':channel_init[0]['token'],
        'channel_id':channel_init[2]
    })
    #print(f'{url}channel/details?{query_string}')
    print(f'{url}channel/details?{query_string}')
    response = requests.get(f'{url}channel/details?{query_string}')
    print(response.text)
    payload = response.json()
    database = DataBase()
    assert database.get_channel_info(channel_init[2])['name'] == payload['name']
    #assert 'test' == payload['test']

def test_channel_details_remote_no_permission(url, channel_init):
    '''
    test_channel_details_remote_no_permission
    '''
    query_string = urllib.parse.urlencode({
        'token':channel_init[3]['token'],
        'channel_id':channel_init[2]
    })
    response = requests.get(f'{url}channel/details?{query_string}')
    assert response.json()['code'] == 400


def test_channel_messages_empty_remote(url, channel_init):
    '''
    test_channel_messages_empty_remote
    '''
    query_string = urllib.parse.urlencode({
        'token':channel_init[0]['token'],
        'channel_id':channel_init[2],
        'start':0
    })
    response = requests.get(f'{url}channel/messages?{query_string}')
    assert response.json()['messages'] == []

def test_channel_messages_remote_no_permission(url, channel_init):
    '''
    test_channel_messages_remote_no_permission
    '''
    query_string = urllib.parse.urlencode({
        'token':channel_init[3]['token'],
        'channel_id':channel_init[2],
        'start':0
    })
    response = requests.get(f'{url}channel/messages?{query_string}')
    assert response.json()['code'] == 400

def test_channel_leave_remote(url, channel_init):
    '''
    test_channel_leave_remote
    '''
    requests.post(f'{url}channel/leave', json={
        'token':channel_init[1]['token'],
        'channel_id':channel_init[2]
    })
    database = DataBase()
    assert channel_init[1]['u_id'] not in database.get_channel_info(channel_init[2])['members_id']

def test_channel_addowner_remote(url, channel_init):
    '''
    test_channel_addowner_remote
    '''
    requests.post(f'{url}channel/addowner', json={
        'token':channel_init[0]['token'],
        'channel_id':channel_init[2],
        'u_id':channel_init[1]['u_id']
    })
    database = DataBase()
    assert channel_init[1]['u_id'] in database.get_channel_info(channel_init[2])['owners_id']

def test_channel_removeowner_remote(url, channel_init):
    '''
    test_channel_removeowner_remote
    '''
    requests.post(f'{url}channel/removeowner', json={
        'token':channel_init[0]['token'],
        'channel_id':channel_init[2],
        'u_id':channel_init[0]['u_id']
    })
    database = DataBase()
    assert channel_init[0]['u_id'] not in database.get_channel_info(channel_init[2])['owners_id']

def test_channel_join_remote(url, channel_init):
    '''
    test_channel_join_remote
    '''
    test_channel_public_id = channels_create(
        channel_init[0]['token'],
        f"test_public{UNIQUE_ID}",
        True
    )
    requests.post(f'{url}channel/join', json={
        'token':channel_init[1]['token'],
        'channel_id':test_channel_public_id['channel_id']
    })
    database = DataBase()
    assert channel_init[1]['u_id'] in database.get_channel_info(test_channel_public_id['channel_id'])['members_id']

def test_clear_database():
    '''
    test_clear_database
    '''
    clear()