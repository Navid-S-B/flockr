""""
By Navid Bhuiyan
Date: 30/09/2020

auth.py interactes with the database to provide tokens for other features to
verify users.
"""
import re
import jwt
from error import InputError
from flockr_database_api import DataBase

# Permissions
USER_PERMISSIONS = 2
OWNER_PERMISSIONS = 1

# JWT Secrets
RESET_PASSWORD_KEY = "changepassword"

# FEATURE DEPENDENCIES
def check_email_in_database(email):
    """
    Checks if email is present in database.
    """
    # Open database
    database = DataBase()
    email_in_database = False
    users = database.database_dict['users']
    for user in users:
        if user['email'] == email:
            email_in_database = True
            break
    return email_in_database

def check_email_regex(email):
    """
    Validates email string.
    """
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return bool(re.search(regex, email))

def validate_email(email):
    """
    Validates if email is accepted.
    """
    # Check email regex
    regex_validate = check_email_regex(email)
    # Check email does not exist
    email_in_database = check_email_in_database(email)
    return bool(regex_validate and not email_in_database)

def validate_password(password):
    """
    Validate password.
    """
    return len(password) >= 6

def validate_names(name_first, name_last):
    """
    Validates the first and last name.
    """
    if len(name_first) >= 1 and len(name_first) <= 50:
        if len(name_last) >= 1 and len(name_last) <= 50:
            return True
    return False

def create_handle(name_first, name_last):
    """
    Autogenerates handle name.
    """
    database = DataBase()
    handle_str = name_first + '_' + name_last
    if len(handle_str) > 20:
        handle_str = name_first[0:9] + name_last[0:9]
    users = database.database_dict['users']
    for user in users:
        # Make handle str unique
        if handle_str == user['handle_str']:
            handle_str = name_first[0:5] + str(database.database_dict['no_users'] + 1)
    handle_str = handle_str.lower()
    return handle_str

# FEATURES
def auth_login(email, password):
    """
    Logs user into flockr (tracks account in database).
    """
    email_in_database = check_email_in_database(email)
    validate_email_regex = check_email_regex(email)
    if not email_in_database or not validate_email_regex:
        raise InputError('Invalid email or email already in database')
    database = DataBase()
    users = database.database_dict['users']
    valid_user = {}
    for user in users:
        if user['email'] == email and user['password'] == password:
            valid_user = user
            break
    if not valid_user:
        raise InputError('Invalid email or email already in database')
    # Add user to active_user database
    active_users = database.database_dict['active_users']
    token_str_1 = f"active_user_{valid_user['u_id']}"
    token_str_2 = f"{database.database_dict['no_active_users']}"
    token_str = token_str_1 + "_" + token_str_2
    token_str = database.token_generator(token_str)
    return_dict = {
        'u_id': valid_user['u_id'],
        'token': token_str
    }
    active_users.append(return_dict)
    database.database_dict['no_active_users'] += 1
    database.close()
    return return_dict

def auth_logout(token):
    """
    Logs user out of flockr (active to not active user).
    """
    database = DataBase()
    token = database.token_decryptor(token)
    # Get active users list
    active_users = database.database_dict['active_users']
    # Get active_users index from token
    active_user_index = re.search("_[0-9]*$", token).group(0)
    active_user_index = int(re.sub("_", "", active_user_index))
    # Remove active user
    active_users.pop(active_user_index)
    database.database_dict['no_active_users'] -= 1
    database.close()
    return {
        'is_success': True
    }

def auth_register(email, password, name_first, name_last):
    """
    Create user account based on valid info.
    """
    # Validate entries
    valid_email = validate_email(email)
    valid_password = validate_password(password)
    valid_names = validate_names(name_first, name_last)
    # If every input is valid
    if not valid_email or not valid_names or not valid_password:
        raise InputError('Invalid email or names or password')
    # Open database for editing
    database = DataBase()
    # Add user to database
    users = database.database_dict['users']
    # Give user specific permissions
    permissions = USER_PERMISSIONS
    if database.database_dict['no_users'] == 0:
        permissions = OWNER_PERMISSIONS
    user_dict = {
        'handle_str': create_handle(name_first, name_last),
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'permissions': permissions,
        'u_id': len(users),
        'profile_img_url': None,
    }
    users.append(user_dict)
    database.database_dict['no_users'] += 1
    # Add user to active user
    active_users = database.database_dict['active_users']
    token_str = f"active_user_{user_dict['u_id']}_{database.database_dict['no_active_users']}"
    token_str = database.token_generator(token_str)
    return_dict = {
        'u_id': user_dict['u_id'],
        'token': token_str
    }
    database.database_dict['no_active_users'] += 1
    active_users.append(return_dict)
    # Close database to save changes
    database.close()
    return return_dict

def auth_passwordreset_request(email):
    """
    Send email to reset password, however I am not seting an'
    email server to send string. The secret string is an jwt
    of the email set using a secret.
    """
    # Send email (do not want to set up a server as of now).
    email = email + "/"
    return {}

def auth_passwordreset_reset(reset_code, new_password):
    """
    Reset password given a reset code.
    """
    # Try decrypting jwt string
    try:
        decrypted_dict = jwt.decode(reset_code, RESET_PASSWORD_KEY, algorithms=['HS256'])
    except Exception:
        raise InputError
    email = decrypted_dict['email']
    # Check if password and email is valid
    if not validate_password(new_password) or not check_email_in_database(email):
        raise InputError
    # Reset the password
    database = DataBase()
    u_id = 0
    users = database.database_dict['users']
    for user in users:
        if user['email'] == email:
            break
        u_id += 1
    target_user = database.database_dict['users'][u_id]
    target_user['password'] = new_password
    database.close()
    return {}
