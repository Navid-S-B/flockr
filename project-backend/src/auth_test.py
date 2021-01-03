"""
Author: Navid Bhuiyan
Date: 27/09/2020

This file is essentially a quick demo of auth.py tests.
"""
import jwt
import pytest
from auth import auth_login
from auth import auth_register
from auth import auth_logout
from auth import auth_passwordreset_request
from auth import auth_passwordreset_reset
from flockr_database_api import DataBase
from error import InputError
from other import clear

# TEST SUCCESSFUL CASES
def test_register():
    """
    Tests if the register function works as intended with valid input.
    """
    # Dict is returned (for first time entering/otherwise pass this function)
    registered_email = "registered.email@registeredemail.com"
    registered_password = "registered_password"
    valid_first_name = "Name_First"
    valid_last_name = "Name_Last"
    return_type = auth_register(registered_email, registered_password,
                                valid_first_name, valid_last_name)
    return_type = type(return_type)
    assert return_type == dict

def test_logout():
    """
    Tests if the log out function works as intended with valid input.
    """
    # Get token from global variable and use it to logout
    token = jwt.encode({"token": "active_user_0_0"}, "tokenkey", algorithm='HS256')
    return_dict = auth_logout(token.decode('UTF-8'))
    assert return_dict['is_success'] == True

def test_login():
    """
    Test if the logout function works as intended with valid input.
    """
    # Use registered account information to login
    registered_email = "registered.email@registeredemail.com"
    registered_password = "registered_password"
    return_dict = auth_login(registered_email, registered_password)
    return_type = type(return_dict)
    assert return_type == dict

# TEST UNSUCCESSFUL TEST CASES
# Test auth_login
def test_invalid_email_login():
    """
    Test log in function error detection measures for an invalid email.
    """
    # Invalid emails
    not_an_email = "email.com"
    contains_non_letter_chars = "aa<>@google.com"
    invalid_domain = "email@<>.com"
    # Assume password
    password = "password"
    with pytest.raises(InputError):
        assert auth_login(not_an_email, password)
        assert auth_login(contains_non_letter_chars, password)
        assert auth_login(invalid_domain, password)

def test_non_user_email():
    """
    Test login function to throw an error for a non-user email.
    """
    # No user is attached to the email
    # (Assumme currently no one is)
    no_user_email = "no.useremal@nouseremail.com"
    password = "password"
    with pytest.raises(InputError):
        assert auth_login(no_user_email, password)

def test_wrong_password():
    """
    Test login function to throw an error when the wrong password is entered.
    """
    registered_email = "registered.email@registeredemail.com"
    wrong_password = "wrong_password"
    with pytest.raises(InputError):
        assert auth_login(registered_email, wrong_password)
    # Clear database after testing (no persistence required yet)

def test_invalid_email_register():
    """
    Trigger invalid email error.
    """
    # Invalid emails
    not_an_email = "email.com"
    contains_non_letter_chars = "aa<>@google.com"
    invalid_domain = "email@<>.com"
    # Assume account data
    password = "password"
    name_first = "name"
    name_last = "name"
    with pytest.raises(InputError):
        assert auth_register(not_an_email, password, name_first, name_last)
        assert auth_register(contains_non_letter_chars, password, name_first, name_last)
        assert auth_register(invalid_domain, password, name_first, name_last)

def test_email_in_database():
    """
    Trigger error when signing up an email in the database.
    """
    # Using account generated by first function
    registered_email = "registered.email@registeredemail.com"
    valid_password = "password"
    valid_first_name = "Name_First"
    valid_last_name = "Name_Last"
    with pytest.raises(InputError):
        assert auth_register(registered_email, valid_password, valid_first_name, valid_last_name)

def test_password_strength():
    """
    Trigger weak password error.
    """
    # Assume this is in the user database
    valid_email = "correct.email@correctemail.com"
    valid_first_name = "Name_First"
    valid_last_name = "Name_Last"
    # Less than 6 chars long
    weak_password = "pas"
    with pytest.raises(InputError):
        assert auth_register(valid_email, weak_password, valid_first_name, valid_last_name)

def test_invalid_name_first():
    """
    Trigger invalid first name error.
    """
    # Assume this account is in database
    valid_email = "used.email@usedemail.com"
    valid_password = "password"
    # Under 1 char and over 50 char
    invalid_name_first_1 = ""
    invalid_name_first_2 = "a" * 51
    name_last = "name"
    with pytest.raises(InputError):
        assert auth_register(valid_email, valid_password, invalid_name_first_1, name_last)
        assert auth_register(valid_email, valid_password, invalid_name_first_2, name_last)

def test_invalid_name_last():
    """
    Trigger invalid last name error.
    """
    # Assume this account is in database
    valid_email = "used.email@usedemail.com"
    valid_password = "password"
    valid_first_name = "Name_First"
    # Under 1 char and over 50 char
    invalid_name_last_1 = ""
    invalid_name_last_2 = "a" * 51
    with pytest.raises(InputError):
        assert auth_register(valid_email, valid_password, valid_first_name, invalid_name_last_1)
        assert auth_register(valid_email, valid_password, valid_first_name, invalid_name_last_2)

def test_password_reset():
    """
    Check if password reset works for valid inputs.
    """
    registered_email = "registered.email@registeredemail.com"
    return_1 = auth_passwordreset_request(registered_email)
    # String sent
    reset_string = jwt.encode({'email': registered_email}, 'changepassword', algorithm='HS256')
    new_password = "different_password"
    return_2 = auth_passwordreset_reset(reset_string, new_password)
    assert return_1 == {} and return_2 == {}

def test_password_reset_invalid_reset_code():
    """
    Trigger input error for invalid reset code.
    """
    with pytest.raises(InputError):
        assert auth_passwordreset_reset("aslkmdklsamdlka", "password")

def test_password_reset_invalid_password():
    """
    Trigger input error for invalid password.
    """
    registered_email = "registered.email@registeredemail.com"
    reset_string = jwt.encode({'email': registered_email}, 'changepassword', algorithm='HS256')
    with pytest.raises(InputError):
        assert auth_passwordreset_reset(reset_string, "p")

def test_clear_database():
    """
    Clear database.
    """
    clear()
