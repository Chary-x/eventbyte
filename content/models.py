
import pickle  

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask_login import UserMixin


db = SQLAlchemy()

def dbinit():
    addDummyData()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text(), unique=True)
    forename = db.Column(db.Text())
    surname = db.Column(db.Text())
    passwordHash = db.Column(db.Text())
    createdAt = db.Column(db.DateTime, default=datetime.now) ## get time of creation
    emailVerified = db.Column(db.Boolean, default=False)
    lastLoggedIn = db.Column(db.DateTime) 
    verificationCode = db.Column(db.Text())
    resetCode = db.Column(db.Integer)

    superuser = db.relationship('SuperUser', back_populates='user')
    notifications = db.relationship('Notification', back_populates='user')
    tickets = db.relationship('Ticket', back_populates='user') 
     
    # Constructor
    def __init__(self, email, forename, surname, passwordHash):
        self.email = email 
        self.forename = forename
        self.surname = surname
        self.passwordHash = passwordHash
    
    @staticmethod
    def generate_verification_token(email):
        token_data = {'email' : email, 
                      'timestamp' : str(datetime.now())
                     }
        verification_token = pickle.dumps(token_data)
        return verification_token

    def verify_token(self, token_data) -> bool:
        email = token_data['email']
        timestamp = token_data['timestamp'] # idk what to do with this yet, some sort of expiry logic
        if email:
            return email == self.email
        return False

    def get_id(self):
        return str(self.id)
    
class SuperUser(db.Model):
    __tablename__ = 'superuser'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),unique=True)
    
    # 1-1 relationship with user table
    user = db.relationship('User', back_populates = 'superuser')

    def __init__(self, user_id):
        self.user_id = user_id


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    date = db.Column(db.Date)   # 1-1 with html type="date"
    start_time = db.Column(db.Time)
    duration = db.Column(db.Time)
    capacity = db.Column(db.Integer)
    tickets_allocated = db.Column(db.Integer, default=0)
    location = db.Column(db.Text())
    cancelled = db.Column(db.Boolean, default=False)
    max_tickets_per_user = db.Column(db.Integer, default=1)

    tickets = db.relationship('Ticket', back_populates='event')
  

    def __init__(self, name, description, date, start_time, duration, capacity, location, tickets_allocated=0, max_tickets_per_user=1):
        self.name = name 
        self.description = description
        self.date = date 
        self.start_time = start_time
        self.duration = duration
        self.capacity = capacity
        self.location = location
        self.tickets_allocated = tickets_allocated
        self.max_tickets_per_user = max_tickets_per_user

    def format_date(self):
      return self.date.strftime('%d/%m/%Y')

    # string formatting, lstrip for leading 0's
    def format_start_time(self):
        return self.start_time.strftime('%H:%M')

    def format_duration(self):
        formatted_duration = self.duration.strftime('%-Hh:%Mm').lstrip('0')
        if self.duration.minute == 0:
            formatted_duration = formatted_duration[:-4]  
        return formatted_duration


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    booked_at = db.Column(db.DateTime, default=datetime.now)
    barcode_id = db.Column(db.Integer, db.ForeignKey('barcode.id'))  
    cancelled = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='tickets')
    event = db.relationship('Event', back_populates='tickets')
    barcode = db.relationship('Barcode', back_populates='ticket')

    def __init__(self, user_id, event_id, barcode_id):
        self.user_id = user_id 
        self.event_id = event_id
        self.barcode_id = barcode_id

    def format_booked_at(self):
        return self.booked_at.strftime('%d/%m/%Y %H:%M') 


class Barcode(db.Model):
    __tablename__ = 'barcode'
    id = db.Column(db.Integer, primary_key=True)
    svg_data = db.Column(db.Text())

    ticket = db.relationship('Ticket', back_populates='barcode')

    def __init__(self, id, svg_data):
        self.id = id 
        self.svg_data = svg_data


    def get_svg_data(self):
        return self.svg_data

class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', back_populates='notifications')

    def __init__(self, title, description, user_id):
        self.title = title
        self.description = description
        self.user_id = user_id

    def format_sent_at(self):
        return self.sent_at.strftime('%d/%m/%Y %H:%M')
    
def addDummyData():
    user_list = [
        User(
            email="ignatiusboateng123@gmail.com",
            forename="ignatiusboateng123@gmail.com",
            surname="ignatiusboateng123@gmail.com",
            passwordHash=generate_password_hash("ignatiusboateng123@gmail.com", salt_length=10)    
        ), 
        User(
            email="attendeetester123@gmail.com",
            forename="attendeetester123@gmail.com",
            surname="attendeetester123@gmail.com",
            passwordHash=generate_password_hash("attendeetester123@gmail.com", salt_length=10)    
        ),
        User(
            email="publictester123@gmail.com",
            forename="publictester123@gmail.com",
            surname="publictester123@gmail.com",
            passwordHash=generate_password_hash("publictester123@gmail.com", salt_length=10) 
        )]
    # for testing purposes
    user_list[0].emailVerified = True
    user_list[1].emailVerified = True
    db.session.add_all(user_list)
    db.session.commit()

    event_list = [
        Event(
            name="Pop",
            date=datetime.strptime("2024-02-21", "%Y-%m-%d"),  
            description="party with friends",
            start_time=datetime.strptime("01:00", "%H:%M").time(),  
            duration=datetime.strptime("01:30", "%H:%M").time(),  
            capacity=100,  
            location="Somewhere"  
        ),
        Event(
            name="Code Jam",
            date=datetime.strptime("21/02/2024", "%d/%m/%Y").date(),  
            description="Make games",
            start_time=datetime.strptime("01:00", "%H:%M").time(),  
            duration=datetime.strptime("01:30", "%H:%M").time(),  
            capacity=100,  
            location="Somewhere", 
            tickets_allocated = 50
        ),
        Event(
            name="Valorant Night",
            date=datetime.strptime("21/02/2025", "%d/%m/%Y").date(), 
            description="Play games",
            start_time=datetime.strptime("01:00", "%H:%M").time(),   
            duration=datetime.strptime("01:30", "%H:%M").time(), 
            capacity=100,  #
            location="Somewhere",
            tickets_allocated = 50
        ),
        Event(
            name="Overwatch Night",
            date=datetime.strptime("21/02/2026", "%d/%m/%Y").date(),  
            description="Play games",
            start_time=datetime.strptime("01:00", "%H:%M").time(),  
            duration=datetime.strptime("01:30", "%H:%M").time(),  
            capacity=100,  
            location="Somewhere", 
            tickets_allocated = 50
        )
    ]

    db.session.add_all(event_list)
    db.session.commit()


    # check if SuperUser exists
    super_user = SuperUser.query.first()    
    if super_user is None:
        # if SuperUser does not exist, create one
        super_user = SuperUser(user_id=user_list[0].id)  # Assuming the first user is the superuser
        db.session.add(super_user)
        db.session.commit()
