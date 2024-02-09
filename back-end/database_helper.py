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

def save_user(user_data):
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