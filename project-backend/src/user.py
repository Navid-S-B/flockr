"""
By Navid Bhuiyan
Date: 26/10/2020

By Kenneth Liu
Date: 12/11/2020

Implementing user features for flockr.
"""

from flockr_database_api import DataBase
from error import AccessError, InputError
from auth import validate_names, validate_email
import urllib.request
from PIL import Image
import glob
import imghdr
import os

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """
    User uploads profile picture.
    """
    database = DataBase()
    directory = "src/res/avatar/"
    user_id = str(database.get_account_info(token)['u_id'])
    try:
        avatar_file, header = urllib.request.urlretrieve(img_url, directory + user_id + ".jpg")
        # No use for header
        header = str(header)
    except:
        raise InputError
    #Error checking
    image = Image.open(avatar_file)
    width, height = image.size
    if width <= x_end or height <= y_end:
        raise InputError('Cannot crop picture to specified x, y coordinates')
    file_list = glob.glob(f'{directory}{user_id}*')
    if imghdr.what(file_list[0]) != 'jpeg':
        os.remove(file_list[0])
        raise InputError('Picture is not jpg')
    #Implementation
    avatar_file_cropped = Image.open(avatar_file)
    avatar_file_cropped = avatar_file_cropped.crop((x_start, y_start, x_end, y_end))
    avatar_file_cropped.save("src/res/avatar/" + str(database.get_account_info(token)['u_id']) + ".jpg")

def user_profile(token, u_id):
    """
    Obtain user profile.
    """
    database = DataBase()
    user_profile = database.get_info_from_id(u_id)
    if not user_profile:
        raise InputError('User does not exist')
    return {'user': user_profile}

def user_profile_setname(token, name_first, name_last):
    """
    user sets name.
    """
    database = DataBase()
    user_profile = database.get_account_info(token)
    if not validate_names(name_first, name_last):
        raise InputError
    user_profile['name_first'] = name_first
    user_profile['name_last'] = name_last
    database.close()
    return {}

def user_profile_setemail(token, email):
    """
    Change email.
    """
    database = DataBase()
    user_profile = database.get_account_info(token)
    if not validate_email(email):
        raise InputError('Email can\'t be used')
    user_profile['email'] = email
    return {}

def user_profile_sethandle(token, handle_str):
    """
    Let user modify handle.
    """
    if len(handle_str) > 20 or len(handle_str) < 3:
        raise InputError('Illegible handle')
    database = DataBase()
    user_profile = database.get_account_info(token)
    users = database.database_dict['users']
    for user in users:
        if handle_str == user['handle_str']:
            raise InputError('Handle already exists')
    user_profile['handle_str'] = handle_str
    database.close()
    return {}
