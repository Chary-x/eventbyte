
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
    emailVerified = db.Column(db.Boolean, default=False)
    lastLoggedIn = db.Column(db.DateTime) 
    verificationToken = db.Column(db.Text())

    superuser = db.relationship('SuperUser', back_populates='user')


     
    # Constructor
    def __init__(self, email, forename, surname, passwordHash):
        self.email = email 
        self.forename = forename
        self.surname = surname
        self.passwordHash = passwordHash
    
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
    

class SuperUser(db.Model):
    __tablename__ = 'superuser'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),unique=True)
    
    # 1-1 relationship with user table
    user = db.relationship('User', back_populates = 'superuser')

    def __init__(self, user_id):
        self.user_id = user_id

def addDummyData():
    user_list = [
        User(
            email="xxxxxxxxxxxxxxx@gmail.com",
            forename="Ignatius",
            surname="Boateng",
            passwordHash="yapyapyap"), 
    ]
    db.session.add_all(user_list)
    db.session.commit()
    
    # Check if SuperUser exists
    super_user = SuperUser.query.first()
    if super_user is None:
        # If SuperUser does not exist, create one
        super_user = SuperUser(user_id=user_list[0].id)  # Assuming the first user is the superuser
        db.session.add(super_user)
        db.session.commit()
