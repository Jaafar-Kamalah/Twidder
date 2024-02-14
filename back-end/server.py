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

@app.route("/sign_up", methods=["POST"])
def sign_up():
    form_data = request.get_json()
    if form_data.get("email") is not None and form_data.get("password") is not None and \
       form_data.get("firstname") is not None and form_data.get("familyname") is not None and \
       form_data.get("gender") is not None and form_data.get("city") is not None and \
       form_data.get("country") is not None:
        if len(form_data["password"]) >= 8 and is_valid_email(form_data["email"]):
            sucess = database_helper.add_user(form_data)
            if (sucess == True):
                return jsonify(success=True, message="Sign up successful.")
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
        password = database_helper.find_user(form_data["username"])
        if form_data["password"] == password:
            token = secrets.token_hex(16)
            database_helper.add_logged_in_user(form_data["username"], token) # Function should not fail due to user input, do we need to handle fails either way?
            return jsonify(success=True, message="Sign in successful", data=token)
        else:
            return jsonify(success=False, message="Invalid email or password.")
    else:
        return jsonify(success=False, message="Missing sign-in values.")

@app.route("/sign_out", methods=["POST"])
def sign_out():
    form_data = request.get_json()
    if "token" in form_data:
        sucess = database_helper.remove_logged_in_user(form_data["token"])
        if sucess:
            return jsonify(success=True, message="Sign out successful")
        else:
            return jsonify(success=False, message="Invalid token.")
    else:
        return jsonify(success=False, message="Missing token value.")

if __name__ == "__main__":
    app.run(debug=True)