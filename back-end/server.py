from flask import Flask, jsonify, request

import database_helper

app = Flask(__name__)

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    if 'email' in data and 'password' in data and 'firstname' in data and \
       'familyname' in data and 'gender' in data and 'city' in data and 'country' in data:
        if len(data['password']) >= 8:
            result = database_helper.save_user(data)
            if (result == True):
                return jsonify(success=True, message="Sign up successful."), 200
            else:
                return jsonify(success=False, message="Account already exists."), 200
        else:
            return jsonify(success=False, message="Password too short."), 400
    else:
        return jsonify(success=False, message="Missing sign up values."), 400

@app.route('/sign_in', methods=['POST'])
def sign_in():
    return "halloj!"

if __name__ == '__main__':
    app.run(debug=True)