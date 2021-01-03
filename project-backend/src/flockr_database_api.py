"""
By Navid Bhuiyan
Date: 30/09/2020

This API allows for the other developers to interact with the database, and
ease development when implementing the account database. It also contains the basic
documentation of the database.

DataBase(): {
    'no_users': num,

    'users': [{
        'handle_str': create_handle(name_first, name_last),
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'permissions': permissions,
        'u_id': len(users),
        'profile_img_url': None,
    }],

    'no_active_users': num,

    'active_users': [{'u_id': num,
         'token': random_str
    }],

    "no_channels": 0,

    'channels': [{
        'creator_token': token
        'name': name,
        'channel_id': channel_id,
        'is_public': True/False,
        'members_id': [],
        'owners_id': [],
        'no_sent_messages': 0,
        'messages' : [{
            'message_id':,
            'u_id':,
            'message':,
            'time_created':,
            'reacts': {
                'react_id':,
                'u_ids':,
                'is_user_reacted':
            }
            
        }]

    }

You use this to open the database and do edits on it and save it to the json file.

If you want the specifics of each key, go to their relative python script sections.
"""
import json
import jwt
import re
from error import AccessError

# JWT Secrets
TOKEN_KEY = "tokenkey"

class DataBase():
    """
    Manages the backend data storage for flockr.
    """
    def __init__(self):
        """
        Initialises access into the database using a dictionary.
        """
        self.database_name = "flockr_database.json"
        with open(self.database_name, 'r') as database_file:
            database_dict = json.load(database_file)
        self.database_dict = database_dict
    
    def token_generator(self, token_str):
        """
        Generated encrypted tokens.
        """
        token_dict = {
            'token': token_str
        }
        encrypted_token = jwt.encode(token_dict, TOKEN_KEY, algorithm='HS256')
        return encrypted_token.decode('UTF-8')

    def token_decryptor(self, token):
        """
        Decrypts tokens.
        """
        decrypted_token = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
        return decrypted_token['token']

    def get_account_info(self, token):
        """
        Collects accont information from token.
        """
        token = self.token_decryptor(token)
        active_user_index = re.search("_[0-9]*_", token).group(0)
        active_user_index = int(re.sub("_", "", active_user_index))
        user_accounts = self.database_dict['users']
        return user_accounts[active_user_index]

    def get_info_from_id(self, u_id):
        """
        Gets account info from u_id.
        """
        try:
            return self.database_dict['users'][u_id]
        # Return null type
        except:
            return

    def get_channel_info(self, channel_id):
        """
        Get channel info from channel_id.
        """
        try:
            return self.database_dict['channels'][channel_id - 1]
        # Return null type
        except:
            return

    def get_channel_messages(self, channel_id):
        """
        Get channel messages from channel_id.
        """
        try:
            return self.database_dict['channels'][channel_id - 1]['messages']
        # Return null type
        except:
            return

    def close(self):
        """
        Closes database and saves changes.
        """
        with open(self.database_name, 'w') as database_file:
            json.dump(self.database_dict, database_file, indent=4)
