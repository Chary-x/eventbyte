
import pickle  

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime, timedelta


db = SQLAlchemy()

def dbinit():
    addDummyData()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text(), unique=True)
    forename = db.Column(db.Text())
    surname = db.Column(db.Text())
    passwordHash = db.Column(db.Text())
    createdAt = db.Column(db.DateTime, default=datetime.now) ## get time of creation
    isSuperUser = db.Column(db.Boolean, default=datetime.now)
    emailVerified = db.Column(db.Boolean, default=False)
    verificationToken = db.Column(db.Text())

    # Populating refs
     
    # Constructor
    def __init__(self, email, forename, surname, passwordHash, isSuperUser=False):
        self.email = email 
        self.forename = forename
        self.surname = surname
        self.passwordHash = passwordHash
        self.isSuperUser = isSuperUser
    
    @staticmethod
    def generate_verification_token(email):
        token_data = {'email' : email, 'timestamp' : datetime.now()}
        verification_token = pickle.dumps(token_data)
        return verification_token

    def verify_token(self, token_data) -> bool:
        email = token_data.get('email')
        if email:
            return email == self.email
        return False



def addDummyData():
    user_list = [
        User("xxxxxxxxxxxxxxx@gmail.com","Ignatius","Boateng","yapyapyap")
    ]
    db.session.add_all(user_list)
    db.session.commit()