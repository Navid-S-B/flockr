'''
By Kenneth Liu
Date: 12/11/2020
'''

import pytest
from other import clear
from auth import auth_register
from error import AccessError, InputError
from channels import channels_create
from other import clear
from flockr_database_api import DataBase
from channel import channel_invite
from user import *
import glob
import os

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

#Success test
def test_user_profile_uploadphoto(user_init):
    user_profile_uploadphoto(user_init[0]['token'],
"https://secure.aspca.org/files/aspca/p2p-campaign-images/user-2660231/guide-dogs_025-11.jpg",
0, 0, 1000, 1000)
    database = DataBase()
    fname = "src/res/avatar/"+str(database.get_account_info(user_init[0]['token'])['u_id'])+".jpg"
    assert os.path.isfile(fname)

def test_user_profile_uploadphoto_bad_request(user_init):
    with pytest.raises(InputError):
        user_profile_uploadphoto(user_init[0]['token'],
"https://albjeai.com/alei.jpg", 0, 0, 1, 1)

def test_user_profile_uploadphoto_coords_out_of_bounds(user_init):
    with pytest.raises(InputError):
        user_profile_uploadphoto(user_init[0]['token'],
"https://secure.aspca.org/files/aspca/p2p-campaign-images/user-2660231/guide-dogs_025-11.jpg",
0, 0, 99999, 99999)

def test_user_profile_uploadphoto_format_error(user_init):
    with pytest.raises(InputError):
        user_profile_uploadphoto(user_init[0]['token'],
"https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
0, 0, 1, 1)


def test_user_profile(user_init):
    ret_dict = user_profile(user_init[0]["token"], user_init[0]["u_id"])
    assert ret_dict['user']['u_id'] == user_init[0]["u_id"]

def test_user_profile_failed(user_init):
    with pytest.raises(InputError):
        user_profile(user_init[0]["token"], -999)

def test_user_profile_setname(user_init):
    ret_dict = user_profile_setname(user_init[0]["token"], "New", "Name")
    assert ret_dict == {}

def test_user_profile_setname_failed(user_init):
    with pytest.raises(InputError):
        user_profile_setname(user_init[0]["token"], "", "")

def test_user_profile_setemail(user_init):
    ret_dict = user_profile_setemail(user_init[0]["token"], "newmail@gmail.com")
    assert ret_dict == {}

def test_user_profile_setemail_failed(user_init):
    with pytest.raises(InputError):
        user_profile_setemail(user_init[0]["token"], "asdfaekl")

def test_user_profile_sethandle(user_init):
    ret_dict = user_profile_sethandle(user_init[0]["token"], "new_handle")
    assert ret_dict == {}

def test_user_profile_sethandle_failed_too_short(user_init):
    with pytest.raises(InputError):
        user_profile_sethandle(user_init[0]["token"], "d")

def test_user_profile_sethandle_failed_already_exists(user_init):
    user_profile_sethandle(user_init[1]["token"], "new_handle1")
    data = DataBase()
    user_dict = data.get_account_info(user_init[1]["token"])
    print(user_dict)
    with pytest.raises(InputError):
        user_profile_sethandle(user_init[0]["token"], "new_handle1")

def test_clear_database():
    """
    Reset database.
    """
    clear()
    files = glob.glob('src/res/avatar/*')
    for f in files:
        os.remove(f)
    files = glob.glob('res/avatar/*')
    for f in files:
        os.remove(f)
