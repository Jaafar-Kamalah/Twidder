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
        get_db().execute("insert into users values(?,?,?,?,?,?,?);", 
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
        cursor = get_db().execute("select password from users where email = ?;", [email])
        user_password = cursor.fetchone()
        cursor.close()
        print(user_password)
        # Return first element if list is not empty, otherwise return None
        return user_password[0] if user_password else None 
    except Exception as e:
        print(e)
        return None
    
def add_logged_in_user(email, token):
    try:
        get_db().execute("insert into loggedInUsers values(?,?);", 
                         [token, email])
        get_db().commit()
        return True
    except Exception as e:
        print(e)
        return False
    
def remove_logged_in_user(token):
    try:
        cursor = get_db().execute("select email from loggedInUsers where token = ?;", [token])
        user = cursor.fetchone()
        cursor.close()

        if user != None:
            get_db().execute("delete from loggedInUsers where token = ?;", [token])
            get_db().commit()
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False