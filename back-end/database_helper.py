import sqlite3

from flask import g

DATABASE_URI = "database.db"

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
    return db

def disconnect_db():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
        g.db = None

def add_user(user_data):
    try:
        get_db().execute("INSERT INTO users VALUES(?,?,?,?,?,?,?);", 
                         [user_data['email'], user_data['password'], user_data['firstname'],
                          user_data['familyname'], user_data['gender'], user_data['city'],
                          user_data['country']])
        get_db().commit()
        return True
    except Exception as e:
        print(e)
        return False
    
def find_user(email):
    try:
        cursor = get_db().execute("SELECT * FROM users WHERE email = ?;", [email])
        user_info_tuple = cursor.fetchone()
        cursor.close()
        if user_info_tuple:
            user_info = {
                "email" : email,
                "password" : user_info_tuple[1],
                "firstname" : user_info_tuple[2],
                "familyname" : user_info_tuple[3],
                "gender" : user_info_tuple[4],
                "city" : user_info_tuple[5],
                "country" : user_info_tuple[6]
            }
            return user_info
        else:
            return None
    except Exception as e:
        print(e)
        return None
    
def add_logged_in_user(email, token):
    try:
        get_db().execute("INSERT INTO loggedInUsers VALUES(?,?);", 
                         [token, email])
        get_db().commit()
        return True
    except Exception as e:
        print(e)
        return False

def find_logged_in_user(token):
    try:
        cursor = get_db().execute("SELECT email FROM loggedInUsers WHERE token = ?;", [token])
        user_email = cursor.fetchone()
        cursor.close()

        # Return first element if list is not empty, otherwise return None
        return user_email[0] if user_email else None 
    except Exception as e:
        print(e)
        return False
    
def delete_logged_in_user(token):
    try:
        get_db().execute("DELETE FROM loggedInUsers WHERE token = ?;", [token])
        get_db().commit()
        return True
    except Exception as e:
        print(e)
        return False
    
def change_user_password(email, new_password):
    try:
        get_db().execute("UPDATE users SET password = ? WHERE email = ?", [new_password, email])
        get_db().commit()
        return True
    except Exception as e:
        print(e)
        return False