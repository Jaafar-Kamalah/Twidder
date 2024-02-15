from flask import Flask, jsonify, request

import database_helper, secrets

app = Flask(__name__)

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

def is_valid_email(email):
    if " " in email or "@" not in email:
        return False
    
    local_part, domain_part = email.split("@")

    if len(local_part) == 0 or len(domain_part) == 0:
        return False
    
    if "." not in domain_part:
        return False
    
    second_lvl_domain, top_lvl_domain = domain_part.split(".")

    if len(second_lvl_domain) == 0 or len(top_lvl_domain) == 0:
        return False

    return True

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
            sucess = database_helper.add_user(form_data)
            if (sucess == True):
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
            database_helper.add_logged_in_user(form_data["username"], token) # Function should not fail due to user input, do we need to handle fails either way?
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

        sucess = database_helper.find_logged_in_user(token)
        if sucess:
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
                    database_helper.change_user_password(email, form_data["newpassword"])
                    return jsonify(success=True, message="Password successfully changed!")
                else:
                    return jsonify(success=False, message="Invalid old password") 
            else:
                return jsonify(success=False, message="Invalid token: '" + token + "'")    
        else:
            return jsonify(success=False, message="Invalid new password")
    else:
        return jsonify(success=False, message="Missing change-password values.")

if __name__ == "__main__":
    app.run(debug=True)