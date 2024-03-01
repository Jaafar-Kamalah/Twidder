from flask import Flask, jsonify, request
from flask_sock import Sock

import database_helper, secrets, re, json

app = Flask(__name__)
sockets = Sock(app)

open_sockets = {}

@sockets.route("/new_socket")
def echo_socket(ws):
    while True:
        token = ws.receive()
        email = database_helper.find_logged_in_user(token)
        open_sockets[email] = ws

@app.route('/')
def root():
    return app.send_static_file("client.html")

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' 
    return re.match(pattern, email) is not None

def is_valid_password(password):
    return len(password) >= 8

@app.route("/sign_up", methods=["POST"])
def sign_up():
    form_data = request.get_json()
    if form_data.get("email") is not None and form_data.get("password") is not None and \
       form_data.get("firstname") is not None and form_data.get("familyname") is not None and \
       form_data.get("gender") is not None and form_data.get("city") is not None and \
       form_data.get("country") is not None:
        if is_valid_password(form_data["password"]) and is_valid_email(form_data["email"]):

            user_info  = database_helper.find_user(form_data["email"])
            if (user_info is not None):
                return jsonify(success=False, message="Email taken."), 409

            success = database_helper.create_user(form_data)
            if (success == True):
                return jsonify(success=True, message="Sign up successful!"), 201
            else:
                return jsonify(success=False, message="Database threw an exception."), 500
        else:
            return jsonify(success=False, message="Invalid email or password"), 400
    else:
        return jsonify(success=False, message="Missing sign-up values."), 400
    

@app.route("/sign_in", methods=["POST"])
def sign_in():
    form_data = request.get_json()
    if "username" in form_data and "password" in form_data:
        email = form_data["username"]
        user_info = database_helper.find_user(email)
        if user_info != None and form_data["password"] == user_info["password"]:

            # If user is already logged in in another browser log the old session out
            token = database_helper.get_token(email)
            if token != None:
                open_sockets[email].send(json.dumps({"command": "Signed out"}))
                database_helper.delete_logged_in_user(token)

            token = secrets.token_hex(16)
            database_helper.create_logged_in_user(form_data["username"], token) 
            return jsonify(success=True, message="Sign in successful!", data=token), 200
        else:
            return jsonify(success=False, message="Invalid email or password."), 401
    else:
        return jsonify(success=False, message="Missing sign-in values."), 400

@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get('Authorization')
    if token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        email = database_helper.find_logged_in_user(token)
        if email:
            # Close socket
            if (open_sockets.get(email) is not None):
                open_sockets[email].close()
                del open_sockets[email]

            database_helper.delete_logged_in_user(token)
            return jsonify(success=True, message="Sign out successful!"), 200
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'"), 401
    else:
        return jsonify(success=False, message="Missing token in Authorization header."), 400
    
@app.route("/change_password", methods=["PUT"])
def change_password():
    form_data = request.get_json()
    token = request.headers.get('Authorization')
    if form_data.get("oldpassword") is not None and form_data.get("newpassword") is not None \
       and token:
        if is_valid_password(form_data["newpassword"]):
            # Postman adds "Berer " to token but not tests.py
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            email = database_helper.find_logged_in_user(token)
            if email:
                user_info = database_helper.find_user(email)
                if user_info["password"] == form_data["oldpassword"]:
                    database_helper.update_user_password(email, form_data["newpassword"])
                    return jsonify(success=True, message="Password successfully changed!"), 200
                else:
                    return jsonify(success=False, message="Invalid old password"), 401
            else:
                return jsonify(success=False, message="Invalid token: '" + token + "'"), 401    
        else:
            return jsonify(success=False, message="Invalid new password"), 400
    else:
        return jsonify(success=False, message="Missing change-password values."), 400
    
@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = request.headers.get('Authorization')
    if token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        email = database_helper.find_logged_in_user(token)
        if email:
            user_info = database_helper.find_user(email)
            user_info.pop("password")
            return jsonify(success=True, message="User info retrieval successful!", data=user_info), 200
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'"), 401
    else:
        return jsonify(success=False, message="Missing token in Authorization header."), 400
    
@app.route("/get_user_data_by_email/<email>", methods=["GET"])
def get_user_data_by_email(email):
    token = request.headers.get('Authorization')
    if email is not None and token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        success = database_helper.find_logged_in_user(token)
        if success:
            user_info = database_helper.find_user(email)
            if user_info != None:
                user_info.pop("password")
                return jsonify(success=True, message="User info retrieval successful!", data=user_info), 200
            else:
                return jsonify(success=False, message="User with email does not exist."), 404
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'"), 401
    else:
        return jsonify(success=False, message="Missing token in Authorization header."), 400
    
@app.route("/post_message", methods=["POST"])
def post_message():
    form_data = request.get_json()
    token = request.headers.get('Authorization')
    
    if form_data.get("email") is not None and form_data.get("message") is not None and token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        if form_data["message"] == "":
            return jsonify(success=False, message="Message empty.")
        
        writer = database_helper.find_logged_in_user(token)
        if writer == None:
            return jsonify(success=False, message="Token invalid."), 401
        
        receiver = database_helper.find_user(form_data["email"])
        if receiver == None:
            return jsonify(success=False, message="No user found with email."), 404

        database_helper.create_message(writer, receiver["email"], form_data["message"])
        return jsonify(success=True, message="Message post successful!"), 201
    else:
        return jsonify(success=False, message="Missing post-message values."), 400
    
@app.route("/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = request.headers.get('Authorization')
    if token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        email = database_helper.find_logged_in_user(token)
        if email:
            messages = database_helper.find_messages(email)
            return jsonify(success=True, message="Message retrieval successful!", \
                           data=messages), 200
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'"), 401
    else:
        return jsonify(success=False, message="Missing token in Authorization header."), 400
    
@app.route("/get_user_messages_by_email/<email>", methods=["GET"])
def get_user_messages_by_email(email):
    token = request.headers.get('Authorization')
    if token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        success = database_helper.find_logged_in_user(token)
        if success:
            user_info = database_helper.find_user(email)
            if user_info is not None:
                messages = database_helper.find_messages(user_info["email"])
                return jsonify(success=True, message="Message retrieval successful!", \
                               data=messages), 200
            else:
                return jsonify(success=False, message="No user with email."), 404
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'"), 401
    else:
        return jsonify(success=False, message="Missing get-user-messages-by-email values."), 400

if __name__ == "__main__":
    app.run(debug=True)