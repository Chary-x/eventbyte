from sqlalchemy_utils import EmailType

from flask_sqlalchemy import SQLAlchemy
from flask import Flask


db = SQLAlchemy()

def dbinit():
    addDummyData()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EmailType, unique=True)
    firstName = db.Column(db.Text())
    secondName = db.Column(db.Text())
    username = db.Column(db.Text(), unique=True)
    passwordHash = db.Column(db.Text())

    # Populating refs
     
    # Constructor
    def __init__(self, email, firstName, secondName, username, passwordHash):
        self.email = email 
        self.firstName = firstName
        self.secondName = secondName
        self.username = username
        self.passwordHash = passwordHash



def addDummyData():
    user_list = [
        User("xxxxxxxxxxxxxxx@gmail.com","Ignatius","Boateng","chary","yapyapyap")
    ]
    db.session.add_all(user_list)
    db.session.commit()