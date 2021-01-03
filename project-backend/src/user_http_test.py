"""
By Navid Bhuiyan
Date: 26/10/2020

Creating tests to check the server integration of the backend into the frontend
for the auth.py functions.

"""
from auth import auth_register
from flockr_database_api import DataBase
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
from channels import channels_create
from channel import channel_invite

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
def user_init():
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

@pytest.fixture
def global_variables(url):
    """
    Variables to be used in all functions.
    """
    data_1 = {}
    data_1['email'] = 'test1@email.com'
    data_1['password'] = 'password'
    data_1['name_first'] = 'name_first'
    data_1['name_last'] = 'name_last'
    data_2 = {}
    data_2['email'] =  'test2@email.com'
    data_2['password'] = 'password'
    data_2['name_first'] = 'name_first'
    data_2['name_last'] = 'name_last'
    pathname = "/auth/register"

    response_1 = requests.post(url + pathname, json=data_1)
    response_2 = requests.post(url + pathname, json=data_2)
   
    try:
        pytest.global_token_1 = json.loads(response_1.text)['token']
        pytest.global_token_2 = json.loads(response_2.text)['token']
    except:
        database = DataBase()
        pytest.global_token_1 = database.database_dict['active_users'][0]['token']
        pytest.global_token_2 = database.database_dict['active_users'][1]['token']

def test_user_profile(url, global_variables):
    """
    Test that the channel_create function works as expected.
    """
    pathname = "/user/profile"
    test_url = url + pathname + f'?token={pytest.global_token_1}&u_id=0'
    response = requests.get(test_url)
    print(response)
    assert json.loads(response.text)['user']

def test_user_profile_setname(url, global_variables):
    """
    Change username
    """
    pathname = "/user/profile/setname"
    test_url = url + pathname
    json_package = {
        'token': pytest.global_token_1,
        "name_first": "Navid",
        "name_last": "bhuiyan"
    }
    response = requests.put(test_url, json = json_package)
    assert json.loads(response.text) == {}

def test_user_profile_setemail(url, global_variables):
    """
    Change email/
    """
    pathname = "/user/profile/setemail"
    test_url = url + pathname
    json_package = {
        'token': pytest.global_token_1,
        "email": "yeye@email.com"
    }
    response = requests.put(test_url, json = json_package)
    assert json.loads(response.text) == {}

def test_user_profile_sethandle(url, global_variables):
    """
    Change email/
    """
    pathname = "/user/profile/sethandle"
    test_url = url + pathname
    json_package = {
        'token': pytest.global_token_1,
        "handle_str": "bueycorp"
    }
    response = requests.put(test_url, json = json_package)
    assert json.loads(response.text) == {}

def test_user_profile_uploadphoto_remote(url, user_init):
    response = requests.post(f"{url}user/profile/uploadphoto", json = {
        'token': user_init[0]['token'],
        'img_url': "https://secure.aspca.org/files/aspca/p2p-campaign-images/user-2660231/guide-dogs_025-11.jpg",
        'x_start': 0,
        'y_start': 0,
        'x_end': 1000,
        'y_end': 1000,
    })
    assert json.loads(response.text) == {}

def test_clear(url):
    test_url = url + "/clear"
    requests.delete(test_url)
    
