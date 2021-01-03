"""
By TONG LIU/ hongji Liu
Date: 20/10/2020

Creating tests to check the server integration of the backend into the frontend
for the auth.py functions.

"""
from auth import auth_register
from channels import channels_create, channels_list, channels_listall
from other import clear
from flockr_database_api import DataBase
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests

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

def test_channels_create_post(url, global_variables):
    """
    Test that the channel_create function works as expected.
    """
    json_package = {
        'token': pytest.global_token_1,
        'name': 'name',
        'is_public': True
    }
    print(pytest.global_token_1)
    pathname = "/channels/create"
    test_url = url + pathname
    response = requests.post(test_url, json=json_package)
    assert response.json()['channel_id'] == 1

def test_channels_create_name_error(url, global_variables):
    
    """
    Trigger create name error i.e. name is more than 20 chars.
    """
    json_package = {
        'token': pytest.global_token_1,
        'name': 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii',
        'is_public': True
    }
    pathname = "/channels/create"
    test_url = url + pathname
    response = requests.post(test_url, json = json_package)
    assert response.json()['code'] == 400

def test_channels_list_all_get(url, global_variables):
    
    """
    Test that the listall function works as expected.
    Uses previous test token and checks the list
    """
    response = requests.get(url + '/channels/listall' + f'?token={pytest.global_token_1}')
    assert json.loads(response.text)["channels"]

def test_no_channel_in_channels_list(url, global_variables):
    """
    Trigger non-existent channel error.
    """
    response = requests.get(url + '/channels/list' + f'?token={pytest.global_token_2}')
    assert json.loads(response.text) == {'channels': []}

def test_clear():
    clear()
