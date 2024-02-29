from flask import Flask, jsonify, request

import database_helper, secrets, re

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

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
            success = database_helper.create_user(form_data)
            if (success == True):
                return jsonify(success=True, message="Sign up successful!")
            else:
                return jsonify(success=False, message="Account already exists.")
        else:
            return jsonify(success=False, message="Invalid email or password")
    else:
        return jsonify(success=False, message="Missing sign-up values.")
    

@app.route("/sign_in", methods=["POST"])
def sign_in():
    form_data = request.get_json()
    if "username" in form_data and "password" in form_data:
        user_info = database_helper.find_user(form_data["username"])
        if user_info != None and form_data["password"] == user_info["password"]:
            token = secrets.token_hex(16)
            database_helper.create_logged_in_user(form_data["username"], token) # Function should not fail due to user input, do we need to handle fails either way?
            return jsonify(success=True, message="Sign in successful!", data=token)
        else:
            return jsonify(success=False, message="Invalid email or password.")
    else:
        return jsonify(success=False, message="Missing sign-in values.")

@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get('Authorization')
    if token:
        # Postman adds "Berer " to token but not tests.py
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        success = database_helper.find_logged_in_user(token)
        if success:
            database_helper.delete_logged_in_user(token)
            return jsonify(success=True, message="Sign out successful!")
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'")
    else:
        return jsonify(success=False, message="Missing token in Authorization header.")
    
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
                    return jsonify(success=True, message="Password successfully changed!")
                else:
                    return jsonify(success=False, message="Invalid old password") 
            else:
                return jsonify(success=False, message="Invalid token: '" + token + "'")    
        else:
            return jsonify(success=False, message="Invalid new password")
    else:
        return jsonify(success=False, message="Missing change-password values.")
    
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
            return jsonify(success=True, message="User info retrieval successful!", \
                           data=user_info)
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'")
    else:
        return jsonify(success=False, message="Missing token in Authorization header.")
    
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
                return jsonify(success=True, message="User info retrieval successful!", \
                           data=user_info)
            else:
                return jsonify(success=False, message="User with email does not exist.")
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'")
    else:
        return jsonify(success=False, message="Missing token in Authorization header.")
    
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
            return jsonify(success=False, message="Token invalid.")
        
        receiver = database_helper.find_user(form_data["email"])
        if receiver == None:
            return jsonify(success=False, message="No user found with email.")

        database_helper.create_message(writer, receiver["email"], form_data["message"])
        return jsonify(success=True, message="Message post successful!")
    else:
        return jsonify(success=False, message="Missing post-message values.")
    
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
                           data=messages)
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'")
    else:
        return jsonify(success=False, message="Missing token in Authorization header.")
    
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
                               data=messages)
            else:
                return jsonify(success=False, message="No user with email.")
        else:
            return jsonify(success=False, message="Invalid token: '" + token + "'")
    else:
        return jsonify(success=False, message="Missing get-user-messages-by-email values.")

if __name__ == "__main__":
    app.run(debug=True)