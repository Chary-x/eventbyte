
# flask imports
import pickle
from flask_mail import Mail, Message
from flask import Flask,session, flash, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional
from datetime import datetime

from barcode import EAN13
from barcode.writer import ImageWriter
from random import randint
import uuid

# database imports

# sec imports
import os
from dotenv import load_dotenv

# model class imports
from content.models import db, dbinit, User, Event,SuperUser, Notification, Ticket, Barcode

load_dotenv()
login_manager = LoginManager()
login_manager.login_view = 'login'
app = Flask(__name__)


# mail configs

# https://pythonbasics.org/flask-mail/ 

# for warwick base
app.config['MAIL_SUPPRESS_SEND'] = True
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@warwick.ac.uk'

"""
app.config['MAIL_SUPPRESS_SEND'] = False  
app.config['MAIL_USE_TLS'] = True  
app.config['MAIL_PORT'] = 587  # smpt port for tls
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_USERNAME'] = 'eventbyte.org@gmail.com' 
## todo , try catch on getenv, default to warwick one
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'eventbyte.org@gmail.com'  # Default sender email address
"""

try:
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if app.config['SECRET_KEY'] is None:
        raise Exception("SECRET_KEY environment variable is not set.")
except Exception as e:
    raise Exception(f"error setting SECRET_KEY: {e}")


#print(app.config.items())
#select datbase filename, other configs

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventbyte.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# inits
mail = Mail(app)
db.init_app(app)
login_manager.init_app(app)

resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

@app.route('/reqs')
def reqs():
    with open('README.md') as readme:
      with open('requirements.txt') as req:
        return render_template('pages/index.html', README=readme.read(), requirements=req.read())
      
@app.route('/')
def index():
   return render_template('pages/index.html')

# auth routes



@app.route('/auth/register', methods=['POST','GET'])
def register(): 
   if request.method == 'GET':
      return render_template('pages/auth/register.html')

   if request.method == 'POST':

      email = request.form['email'].lower() # get email from form
      ## check if email already exists
      if isExistingEmail(email):
         flash("Email already exists","error")
         return redirect(url_for('register'))
      else:
         # extract payload 
         forename = request.form['forename']
         surname = request.form['surname']
         # hash password again with bcrypt
         password = request.form['password']

         # create and add user to db
         user = User(
            email=email,
            forename=forename,
            surname = surname,
            passwordHash= generate_password_hash(password, salt_length=10)
         )
         
         db.session.add(user)
         db.session.commit()

         # generate token
         token = User.generate_verification_token(email) 
         session['auth_token'] = token

         # try sending verification email
         try:
            send_verification_email(email, token)
         except Exception as e:
            print(f"Failed to send verification email to {email} : {e}")
            flash(f"An error occured whilst attempting to send you a verification email", "error")
            print("\nError details : "  + str(e))
            return redirect(url_for('register'))
         
         # send visual feedback
         flash('Email confirmation sent', 'success')

         # redirect to login
         return redirect(url_for('login'))

def send_verification_email(email: str, token: str):
   link = f"{os.getenv('FLASK_RUN_PORT')}{url_for('verify_email', email=email, token=token)}"
   message = Message('Email Verification Link', recipients=[email])
   message.body = f'Click the link to verify your email\n {link}'
   print(f"Trying to send {message.body} To {email}")
   mail.send(message)


def send_email(recipients, title: str, body: str):
   message = Message(title, recipients=recipients)
   message.body = body
   mail.send(message)



def isExistingEmail(email: str) -> bool:
   existingEmail = User.query.filter_by(email=email).first()
   if existingEmail:
      return True    
   else:
      return False

@app.route('/auth/verify-email/<token>')
def verify_email(token):
   try:
      token_data = pickle.loads(token)
      email = token_data.get('email')
      user = User.query.filter_by(email=email).first()

      if user and user.verify_token(token_data):
         # update user email and verification bool
         user.emailVerified = True
         db.session.commit()
         flash('Email verification successful! You can now log in', 'success')
         return redirect(url_for('login'))

      else:
         flash('Invalid or expired verification link', 'error')
         return redirect(url_for('register'))
   except Exception as e:
      flash('An error occurred during email verification, Please try again later', 'error')
      return redirect(url_for('register')) # redirect to register


def send_notification(title, description, user_id):
   try:
      notification = Notification(
               title=title,
               description=description,
               user_id = user_id
            )
      db.session.add(notification)
      db.session.commit()
      return True
   except Exception as e:
      print("Error occured trying to send a notification")
      print(e)
      return False
   

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
   if request.method == 'GET':
      return render_template('/pages/auth/login.html')

   if request.method == 'POST':
      # extract payload, should be sanitised from frontend
      email = request.form['email']
      password = request.form['password']
      try:

         user = User.query.filter_by(email=email).first()
         
         if not user:
            flash('This email does not exist', 'error')
            return redirect(url_for('login'))  # redirectto the login route

         # temporary for development

         super_user = getSuperUser()
         if user.id == super_user.user_id:
            send_notification(
               title="You Logged In",
               description=f"You logged in!",
               user_id=super_user.user_id
               )
         else:
            send_notification(
               title="User Login",
               description=f"User {user.forename} {user.surname} logged out",
               user_id=super_user.user_id
            )
         login_user(user)

         return redirect(url_for('dashboard'))
         """
         if not user.emailVerified:
            flash("You must verify your email before logging in", "error")
            return redirect(url_for('login'))
         
         if check_password_hash(user.passwordHash, password):
            login_user(user)
            flash("Successful Login", "success")
            print("Succesful Login")
            # Store the user id in session... TODO : create a more secure method, like tokenising again
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))  # redirect to the dashboard route
         else:
               flash("Your password is incorrect, please try again", "error")
               return redirect(url_for('login'))  # redirect to login
         """
      except Exception as e:
         print("Error searching for user by email after login post req ")
         print(e)
         flash("An error occurred. Please try again later.", "error")
         return redirect(url_for('login'))  # redirect to the login route



def getSuperUser():
   try:
      superuser = SuperUser.query.first()
      return superuser
   except Exception as e:
      print(e)
      print("Error trying to get super user object")
      



   
@app.route('/auth/logout')
@login_required
def logout():
   user = current_user
   super_user = getSuperUser()
   if current_user.get_id() == super_user.user_id:
      send_notification(
         title="You Logged Out",
         description=f"You logged out!",
         user_id=super_user.user_id
         )
   else:
      send_notification(
         title="User Logout",
         description=f"User {user.forename} {user.surname} logged out",
         user_id=super_user.user_id
      )
   user = None
   logout_user() 
   return redirect(url_for('index'))


def userInSession() -> Optional[User]:
   user_id = session.get('user_id')
   if user_id is None:
      return None  # no user id in the session
   try:
      user = User.query.filter_by(id=user_id).first()
      return user
   except Exception as e:
      print("Error retrieving user object after login, no user with this user id")
      return None
   
# todo -> login and forgot password
@app.route('/auth/forgot_password', methods=['GET','POST'])
def forgot_password():
   if request.method == 'GET':
      return render_template('pages/auth/forgot_password.html')
   
   if request.method == 'POST':
      email = request.form['email']
      try:
         user = User.query.get(email) 
         if user:  # check if email exists


            # https://www.uuidgenerator.net/dev-corner/python


            reset_code = uuid.uuid4()
            send_email(recipients=[email],
                       title= "Reset Your Password", 
                       body = f"{os.getenv('FLASK_RUN_PORT')}/auth/reset_password/{user.email}/{reset_code}")
            user.resetToken = reset_code
            flash("If your email is in our system, you'll recieve a password reset", "success")
            return redirect(url_for('login'))
         else:
            flash("Please register first", "error")
            print("Email doesn't exist in db ")
            return redirect(url_for('login'))
      except Exception as e:
         flash("Sorry, an error occured", "error")
         print(e)
         return redirect(url_for('login'))
         


@app.route('/auth/<email>/<int:reset_code>', methods=['GET','POST'])
def reset_password(email, reset_code):
   if request.method == 'GET':
      try:
         user = User.query.filter_by(email=email).first()
         if user:
            if reset_code == user.resetToken:
               return render_template('pages/auth/password_reset.html')
            else:
               flash("Invalid code...", "error")
         
         else:
            flash("No user could be found", "error")
      except Exception as e:
         print(e)
   
   ## TODO ACTUALLY TEST
   # sanitise frontend first...
   if request.method == 'POST':
      return redirect(url_for('login'))
   


   # first enter email
   # see if email exists
   # if exists, send special code to user
   # 

# dashboard routes
@login_required
@app.route('/dashboard')
def dashboard():
   return render_template('pages/dashboard.html',forename=current_user.forename) 
"""
   if userInSession() is not None:
      return render_template('/pages/dashboard.html', user = user)
   else:
      flash("Error retrieving your details", "error")
      return redirect(url_for('login))



   user_id = session.get('user_id') # key exception with []
   if user_id is None:
      flash("You must log in to access the dashboard (tut tut)", "error")
      return redirect(url_for('login'))
   
   # retrieve user object
   try:
      user = User.query.filter_by(id = user_id).first()
   except Exception as e:
      print("Error retrieving user object after login, no user with this user id")
      flash("Error retrieving your details", "error")
      return redirect(url_for('login'))
   
   # pass user object to jinja thingy
   return render_template('/pages/dashboard.html', user = user)
"""

# events


def isSuperUser(user) -> bool:
   try:
      super_user = SuperUser.query.get(user.id)
      if super_user:
            return True 
      else:
            return False
   except Exception as e:
      print("Error occurred trying to determine if this user was a superuser")
      print(e)
      return False  

def isAttendee(user) -> bool:
   try: 
      attendee = User.query.filter_by(id = user.id).first()
      if attendee and attendee.emailVerified and not isSuperUser(user):
         return True 
      else:
         return False
   except Exception as e:
      print("Error occurred trying to determine if this user was an attendee")
      print(e)
      return False 
      

@app.route('/events/create', methods=['GET','POST'])
@login_required
def create_event():
   # check if user is superuser
   if isSuperUser(current_user):
      if request.method == 'GET':
         return render_template('pages/events/create-event.html')
      
      if request.method == 'POST':
         name = request.form['name']
         description = request.form['description']
         date = request.form['date']
         start_time = request.form['start_time']
         duration= request.form['duration']
         capacity = request.form['capacity']
         location = request.form['location']
         
         # try creating event object
         try:
            event = Event(
               name=name,
               date=datetime.strptime(date,'%Y-%m-%d').date(), # db.Date only accepts date type
               description=description,
               start_time=datetime.strptime(start_time, '%H:%M').time(), # db.Time only accepts time objects
               duration=datetime.strptime(duration, '%H:%M').time(), # db.Time only accepts time objects
               capacity=capacity, 
               location=location,
            )

            # add event to database
            db.session.add(event)
            db.session.commit()

            # send notification to the superuser , logging
            send_notification(
               title="Event Created",
               description=f"Event {event.name} was created",
               user_id = int(current_user.get_id())
            )

         except Exception as e:
            flash("An error occured whilst trying to create an event", "error")
            print("Error occured trying to create a new event and adding it to the database")
            print(e)
            return redirect(url_for('create_event'))
         
         flash("Event Was Succesfully Created", "success")
         print("Event created")

         return redirect(url_for('create_event'))
   else:
      flash("Only superusers can create events", "error")
      return redirect(url_for('dashboard'))

@app.route('/events/all')
def all_events():
   allEvents = Event.query.all()

   nonSuperUserEvents = Event.query.filter( 
   Event.date > datetime.now(), # events in the future
   Event.cancelled == False, # that aren't cancelled
   ).all()
   
   if isSuperUser(current_user):
       events = allEvents
   else:
       events = nonSuperUserEvents
   
   return render_template('/pages/events/events.html', 
                          events=events, 
                          current_user=current_user,
                          isSuperUser=isSuperUser,
                          isAttendee=isAttendee)


@login_required       
@app.route('/events/edit/<int:event_id>', methods=['GET','POST'])
def edit_event(event_id):
   if isSuperUser(current_user):
   ## first check if event exists
      try:
         event = Event.query.get(event_id)
      except Exception as e:
         print(e)
         print(f"Erorr occured trying to get details for event {event_id}")
         flash("Error fetching event details", "error")
         return redirect(url_for('all_events'))
      
      if event is None:
         print("Event does not exist")
         flash("This event doesn't exist", "error")
         return redirect(url_for('all_events'))
      

      if request.method == 'GET':   
         # Superuser can only edit the event if tickets allocatedis less 
         # than expected capacity
         return render_template('/pages/events/edit-event.html', 
                                 event = event
                              )

      if request.method == 'POST':
         try:
            new_capacity = int(request.form['new_capacity'])

            if new_capacity < event.tickets_allocated:
               flash("New capacity cannot be less than remaining capacity.", "error");
               return redirect(url_for('all_events'))

            elif new_capacity > event.capacity and event.tickets_allocated == event.capacity:
               flash("This event has already been filled up", "error")
               return redirect(url_for('all_events'))
            
            # get old capacity for notifications sake
            old_capacity= event.capacity
            event.capacity = new_capacity


            change_type = "increased" if new_capacity > event.capacity else "decreased"

            # send notifications to ticekt holders on the update in capacity
            ## TODO , change for other attributes if i implement such, for additional features
            for ticket in event.tickets:
               send_notification(
                  title="Capacity Change",
                  description=f"The capacity for {event.name} has been {change_type} from {old_capacity} to {new_capacity}",
                  user_id=ticket.user_id
               )
                  

            db.session.commit()
            flash(f"{event.name}'s capacity updated to {new_capacity}", "success")

            # send notifications to users with ticket to this evnet of updation
         

            return redirect(url_for('all_events'))

         except Exception as e:
            flash("An error occurred while updating capacity", "error")
            print("Error:", e)
            return redirect(url_for('all_events'))
   else:
      flash("Only superusers can edit events", "error")
      return redirect(url_for('dashboard'))
   
@app.route('/events/cancel/<int:event_id>', methods =['GET'])
def cancel_event(event_id):
   try:
      event = Event.query.get(event_id)
   except Exception as e:
      print(e)
      print(f"Erorr occured trying to get details for event {event_id}")
      flash("Error fetching event details", "error")
      return redirect(url_for('all_events'))
   
   if event is None:
      print(f"Event does not exist {event_id}")
      flash("This event doesn't exist", "error")
      return redirect(url_for('all_events'))
   else:
      
      # cancel the event
      event.cancelled = True

      # send notification to 
      send_notification(
         title="Event Cancelled",
         description= f"Event {event.name} was cancelled",
         user_id= current_user.get_id()
      )
      
      # send cancellation notificaiton to every user who has a ticket for this event
      for ticket in event.tickets:
         send_notification(
         title="Event Cancelled",
         description=f"Event {event.name} was cancelled",
         user_id=ticket.user.id
         )
      
      # send notlifications
      db.session.commit()

      flash(f"{event.name} has been cancelled", "success")
      return redirect(url_for('all_events'))



# notifcations
   

@app.route('/dashboard/notifications', methods=['GET','POST'])
def notifications():
   if request.method == 'GET':
      try:
         # get all notifications for this user
         notifications = Notification.query.filter_by(user_id = current_user.get_id()).all()
         return render_template('pages/notifications.html', notifications = notifications)
      except Exception as e:
         print(f"Error fetching notifications for user {current_user.get_id()}")
         print(e)
         flash("Error retrieving your notifications", "error")
         return redirect(url_for('all_events'))


   


## TODO check every time a ticket is claimed the capcaity of the event
# to send email to superuser
   

# ticketing routes

def generate_barcode_id():
    # VERY UNECEESARY, but i plan to work on this application after the coursework
    # on the off chance, barcode number already exists, keep making new ones
      barcode_id = str(randint(1000000000000000, 10000000000000000)) 
      return barcode_id
        

@login_required
@app.route('/events/book/<int:event_id>', methods=['GET','POST'])
def book_ticket(event_id):
   # check capacity of the event being booked
   try:
      event = Event.query.get(event_id)
      if not event:
         flash("This event doesn't exist ")
         print(f"Event id {event_id} doesn't exist", "success")
         return redirect(url_for('all_events'))

      # in the rare case that someone else just snatched a ticket
      elif event.tickets_allocated == event.capacity:
         flash("This event is now full")
         return redirect(url_for('all_events'))

      # generate barcode for the ticket
      # create ticket
      # push to db

      # generate random 15 digit number ( i think thats the standard )
      # https://www.geeksforgeeks.org/how-to-generate-barcode-in-python/

      # generate barcode

      barcode_id = generate_barcode_id()
      barcode = EAN13(str(barcode_id))
      barcode_path = f"static/assets/barcodes/{barcode_id}.png"
      barcode.save(barcode_path)


      ticket = Ticket(
         user_id = current_user.get_id(), 
         event_id = event.id,
      )
      barcode = Barcode(
         id=barcode_id,
         ticket_id = ticket.id,
         event_id = event.id
      )

      db.session.add_all([ticket, barcode])
      db.session.commit()

      # send notification to user
      send_notification(
         title="You Booked A Ticket",
         description=f"You booked a ticket for {event.name}",
         user_id=current_user.get_id()
      )

      send_notification(
         title="Ticket Allocation",
         description=f"{current_user.forename} {current_user.surname} was allocated a ticket for {event.name}",
         user_id = getSuperUser().id
      )

      

      flash(f"You succesfully booked a ticket for {event.name}", "success")
      return redirect(url_for('all_events'))

   except Exception as e:
      flash("An error occured whilst trying to book this event", "error")
      print(e)
      return redirect(url_for('all_events'))


@login_required
@app.route('/tickets/<int:ticket_id>/cancel')
def cancel_ticket(ticket_id):
   pass
