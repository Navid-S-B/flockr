# Assumptions for Flockr :)
This contains all of the asssumptions done whilst building tests and source code.

### Tests
#### auth_register_test.py
- Invalid emails are those described in 'https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/'.
    - Emails with no @ symbol
    - Emails containing [^0-9a-zA-Z] characters.
    - Etc.
#### Other tests
- There was a mix of black box testing and white box testing to ensure
  the backend is functional. Otherwise no other assumptions other than
  those described in the spec.

### Features
#### General Assumptions
- Data is stored in a dictionary converted to a JSON file, through the use of flockr_database_api (refer to api documentation)
- Assume all inputs are expected to be entered correctly according to spec
- Valid emails are those described in 'https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/'.
#### auth.py
- Backend database needs to store account information (documented in flockr_database_api.py).
- For auth_login() that active user tracking is required for only active users to make changes.
- Users would not care about the the handle_name.
- Token is structured as active_user_(u_id)_(no_active_users)
- u_id is the nth index user in python list
### channel.py
- Assume channel dictionary to use the structure outlined in the flockr_database_api documentation
- Assumes channels.py functions work
### channels.py
- We assumed that channel_id is created depend on the length of channels in db.
- Assumes that token is 'token' in iteration1.
- Creation of channel_id is based on length of channel_list after addition of new channel (1 - 9999)
### message.py
- Assumed limits on channel size, and max number of messages for message_id design (CCCCCMMMMMU*) (C - channel, M - message)
- Both C and M are padded to 5 digits and right aligned
- Assumes channels up to 89999, and messages up to 89999.
- Issues with message_sendlater on the frontend.
### other.py
- Only assumed search terms to be actually in the message strings.
### standup.py
- No assumption however issues with frontend not giving right times for standups to end,
  but then still works properly internally (time is maintained in the backend).
# user.py
- No assumptions.
### Persistent Database (flockr_database_api.py)
- Uses JSON to store user information.
- Collects universal commands into one api.
- Refer to the script for more information.

## Not Completed
- Password hashing
- message_sendlater()