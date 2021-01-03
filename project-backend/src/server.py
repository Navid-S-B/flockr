"""
By Mango Team 3
Date: 24/10/2020

Integrated the backend into this server.
"""

from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError
from auth import auth_login
from auth import auth_logout
from auth import auth_register
from auth import auth_passwordreset_reset
from channel import channel_invite
from channel import channel_details
from channel import channel_messages
from channel import channel_leave
from channel import channel_join
from channel import channel_addowner
from channel import channel_removeowner
from channels import channels_create
from channels import channels_list
from channels import channels_listall
from message import *
from standup import standup_active
from standup import standup_send
from standup import standup_start
from user import user_profile
from user import user_profile_setemail
from user import user_profile_sethandle
from user import user_profile_setname
from user import user_profile_uploadphoto
from other import clear, users_all, search, admin_userpermission_change

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "Internal Error",
        "message": err.get_description()
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = False
APP.register_error_handler(Exception, defaultHandler)

# ECHO TEST
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

#PROFILE PHOTO
@APP.route("/res/avatar/<path:path>")
def send_res(path):
    return send_from_directory('', f"res/avatar/{path}")

# AUTH FEATURES
@APP.route("/auth/login", methods=['POST'])
def auth_login_route():
    data = request.get_json()
    email = data['email']
    password = data['password']
    result = auth_login(email, password)
    return dumps(result)

@APP.route("/auth/logout", methods=['POST'])
def auth_logout_route():
    data = request.get_json()
    token = data['token']
    result = auth_logout(token)
    return dumps(result)

@APP.route("/auth/register", methods=['POST'])
def auth_register_route():
    data = request.get_json()
    email = data['email']
    password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']
    result = auth_register(email, password, name_first, name_last)
    return dumps(result)

@APP.route("/auth/passwordreset/request", methods=['POST'])
def auth_passwordreset_request_route():
    return dumps({})

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def auth_passwordreset_reset_route():
    data = request.get_json()
    auth_passwordreset_reset(data['reset_code'], data['new_password'])
    return dumps({})

# CHANNEL FEATURES
@APP.route("/channel/invite", methods=['POST'])
def channel_invite_route():
    data = request.get_json()
    channel_invite(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route("/channel/details", methods=['GET'])
def channel_details_route():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    result = channel_details(token, channel_id)
    return dumps(result)

@APP.route("/channel/messages", methods=['GET'])
def channel_messages_route():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    result = channel_messages(token, channel_id, start)
    return dumps(result)

@APP.route("/channel/leave", methods=['POST'])
def channel_leave_route():
    data = request.get_json()
    channel_leave(data['token'], data['channel_id'])
    return dumps({})

@APP.route("/channel/addowner", methods=['POST'])
def channel_addowner_route():
    data = request.get_json()
    channel_addowner(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route("/channel/removeowner", methods=['POST'])
def channel_removeowner_route():
    data = request.get_json()
    channel_removeowner(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route("/channel/join", methods=['POST'])
def channel_join_route():
    data = request.get_json()
    channel_join(data['token'], int(data['channel_id']))
    return dumps({})

# CHANNELS FEATURES
@APP.route('/channels/create', methods=['POST'])
def channels_create_route():
    token = request.get_json()['token']
    name = request.get_json()['name']
    public = request.get_json()['is_public']
    result = channels_create(token, name, public)
    return dumps(result)

@APP.route('/channels/list', methods=['GET'])
def channels_list_route():
    token = request.args.get('token')
    result = channels_list(token)
    return dumps(result)

@APP.route('/channels/listall', methods=['GET'])
def channels_listall_route():
    token = request.args.get('token')
    result = channels_listall(token)
    return dumps(result)

# MESSAGE FEATURES
@APP.route('/message/send', methods=['POST'])
def mesage_send_route():
    payload = request.get_json()
    result = message_send(payload['token'], payload['channel_id'],
                          payload['message'])
    return dumps(result)

@APP.route('/message/remove', methods=['DELETE'])
def mesage_remove_route():
    payload = request.get_json()
    result = message_remove(payload['token'], payload['message_id'])
    return dumps(result)

@APP.route('/message/edit', methods=['PUT'])
def mesage_edit_route():
    payload = request.get_json()
    result = message_edit(payload['token'], payload['message_id'], payload['message'])
    return dumps(result)
    
@APP.route('/message/sendlater', methods=['POST'])
def message_sendlater_route():
    payload = request.get_json()
    result = message_sendlater(payload['token'], int(payload['channel_id']), payload['message'], int(payload['time_sent']))
    return dumps(result)
    
@APP.route('/message/react', methods=['POST'])
def message_react_route():
    payload = request.get_json()
    result = message_react(payload['token'], payload['message_id'], int(payload['react_id']))
    return dumps(result)

@APP.route('/message/unreact', methods=['POST'])
def message_unreact_route():
    payload = request.get_json()
    result = message_unreact(payload['token'], payload['message_id'], int(payload['react_id']))
    return dumps(result)

@APP.route('/message/pin', methods=['POST'])
def message_pin_route():
    payload = request.get_json()
    result = message_pin(payload['token'], payload['message_id'])
    return dumps(result)

@APP.route('/message/unpin', methods=['POST'])
def message_unpin_route():
    payload = request.get_json()
    result = message_unpin(payload['token'], payload['message_id'])
    return dumps(result)
    
# USER FEATURES
@APP.route('/user/profile', methods=['GET'])
def user_profile_route():
    token = request.args.get('token')
    user_id = int(request.args.get('u_id'))
    result = user_profile(token, user_id)
    return dumps(result)

@APP.route('/user/profile/setname', methods=['PUT'])
def user_profile_setname_route():
    payload = request.get_json()
    result = user_profile_setname(payload['token'], payload['name_first'],
                          payload['name_last'])
    return dumps(result)

@APP.route('/user/profile/setemail', methods=['PUT'])
def user_profile_setemail_route():
    payload = request.get_json()
    result = user_profile_setemail(payload['token'], payload['email'])
    return dumps(result)

@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_profile_sethandle_route():
    payload = request.get_json()
    result = user_profile_sethandle(payload['token'], payload['handle_str'])
    return dumps(result)
    
@APP.route('/user/profile/uploadphoto', methods=['POST'])
def user_profile_uploadphoto_route():
    payload = request.get_json()
    user_profile_uploadphoto(payload['token'], payload['img_url'], payload['x_start'], payload['y_start'], payload['x_end'], payload['y_end'] )
    database = DataBase()
    img_name = str(database.get_account_info(payload['token'])['u_id'])+".jpg"
    acc = database.get_account_info(payload['token']) 
    url = request.base_url.replace("user/profile/uploadphoto", "")
    acc['profile_img_url'] = f"{url}res/avatar/{img_name}"
    database.close()
    return dumps({})

# STANDUP FEATURES
@APP.route('/standup/start', methods=['POST'])
def standup_start_route():
    payload = request.get_json()
    result = standup_start(payload['token'], payload['channel_id'], payload['length'])
    return dumps(result)

@APP.route('/standup/active', methods=['GET'])
def standup_active_route():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    result = standup_active(token, channel_id)
    return dumps(result)

@APP.route('/standup/send', methods=['POST'])
def standup_send_route():
    payload = request.get_json()
    result = standup_send(payload['token'], payload['channel_id'], payload['message'])
    return dumps(result)

# OTHER FEATURES
@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_userpermission_route():
    payload = request.get_json()
    result = admin_userpermission_change(payload['token'], payload['u_id'], payload['permission_id'])
    return dumps(result)

@APP.route('/clear', methods=['DELETE'])
def clear_route():
    clear()
    return dumps({})

@APP.route('/users/all', methods=['GET'])
def users_all_route():
    token = request.args.get('token')
    return dumps(users_all(token))

@APP.route('/search', methods=['GET'])
def search_route():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    result = search(token, query_str)
    return dumps(result)

# Porting
if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
