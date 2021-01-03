"""
By Navid Bhuiyan
Date: 20/10/2020

Creating tests to check the server integration of the backend into the frontend
for the auth.py functions.
"""

import re
import json
import jwt
import signal
from time import sleep
from subprocess import Popen, PIPE
import pytest
import requests
from flockr_database_api import DataBase
from other import clear

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

# TEST SUCCESS CASES
@pytest.fixture
def test_auth_register_post(url):
    """
    Test successful account registration.
    """
    json_package = {
        'email': 'register@email.com',
        'password': 'password',
        'name_first': 'first',
        'name_last': 'last'
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json=json_package)
    pytest.return_dict = json.loads(response.text)

def test_auth_logout_post(url, test_auth_register_post):
    """
    Tests for successful log out.
    """
    token = pytest.return_dict['token']
    json_package = {
        'token': token
    }
    test_url = url + "/auth/logout"
    response = requests.post(test_url, json=json_package)
    # Checkk if is_success is True
    print(response.text)
    assert json.loads(response.text)['is_success']

def test_auth_login_post(url):
    """
    Tests for successful login.
    """
    json_package = {
        'email': 'register@email.com',
        'password': 'password'
    }
    test_url = url + "/auth/login"
    response = requests.post(test_url, json=json_package)
    print(response.text)
    assert json.loads(response.text)['token']

# TEST FAILURE CASES
def test_auth_register_invalid_email(url):
    """
    Detect error when an invalid email address is added for registration.
    """
    json_package = {
        'email': 'email@<>.com',
        'password': 'password',
        'name_first': 'first',
        'name_last': 'last'
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json=json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_register_bad_password(url):
    """
    Detect error with a bad password
    """
    json_package = {
        'email': 'email@gmail.com',
        'password': 'pass',
        'name_first': 'first',
        'name_last': 'last'
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_register_empty_first_name(url):
    """
    Detect error with bad first and last name

    """
    json_package = {
        'email': 'register2@email.com',
        'password': 'password',
        'name_first': "",
        'name_last': 'last'
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_register_bad_first_name(url):
    """
    Detect error with bad first and last name

    """
    json_package = {
        'email': 'register2@email.com',
        'password': 'password',
        'name_first': "".join(['a'] * 51),
        'name_last': 'last'
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_register_empty_last_name(url):
    """
    Detect error with bad first and last name

    """
    json_package = {
        'email': 'registe2r@email.com',
        'password': 'password',
        'name_first': 'name',
        'name_last': ''
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_register_bad_last_name(url):
    """
    Detect error with bad first and last name

    """
    json_package = {
        'email': 'register2@email.com',
        'password': 'password',
        'name_first': "name",
        'name_last': 'l' * 51
    }
    test_url = url + "/auth/register"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_login_invalid_email(url):
    """
    Detect error with invalid email.

    """
    json_package = {
        'email': 'registermail.com',
        'password': 'password'
    }
    test_url = url + "/auth/login"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400


def test_auth_login_email_doesnt_exist(url):
    """
    Detect error with invalid email.

    """
    json_package = {
        'email': 'doesnotexist@email.com',
        'password': 'password'
    }
    test_url = url + "/auth/login"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_login_wrong_password(url):
    """
    Detect error with wrong password inputted.

    """
    json_package = {
        'email': 'register@email.com',
        'password': 'wrongpassword'
    }
    test_url = url + "/auth/login"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text)['code'] == 400

def test_auth_password_reset(url):
    """
    Test password reset
    """
    reset_code = jwt.encode({'email': 'register@email.com'}, 'changepassword', algorithm='HS256')
    json_package = {
        'reset_code': reset_code.decode('UTF-8'),
        'new_password': 'passworddddyy'
    }
    test_url = url + "/auth/passwordreset/reset"
    response = requests.post(test_url, json = json_package)
    assert json.loads(response.text) == {}

def test_clear():
    clear()
