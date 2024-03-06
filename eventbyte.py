# flask imports

from flask_mail import Mail, Message
from flask import Flask,session, flash, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional
from datetime import datetime

from barcode import EAN13
from random import randint
import uuid

# database imports

# model class imports
from content.models import db, dbinit, User, Event,SuperUser, Barcode, Notification, Ticket

login_manager = LoginManager()
login_manager.login_view = 'login'
app = Flask(__name__)


# mail configs

# https://pythonbasics.org/flask-mail/ 

app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@warwick.ac.uk'
app.config['SECRET_KEY'] = "i'm a really secret key" # to be put in .env for future



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventbyte.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app inits
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

# UTILS


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

def send_verification_email(email, token):
   #link = f"127.0.0.1:{os.getenv('FLASK_RUN_PORT')}{url_for('verify_email', email=email)}"
   link = url_for('verify_email', email=email, _external=True)
   message = Message('Email Verification Link', recipients=[email])
   message.body = f'''Click the link to verify your email
                  \n {link} 
                  \n Your code is : {token}
                  '''
   
   print(f"Trying to send {message.body} To {email}")
   mail.send(message)


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



def getSuperUser():
   try:
      superuser = SuperUser.query.first()
      return superuser
   except Exception as e:
      print(e)
      print("Error trying to get super user object")      

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

def generate_barcode_id():
    # VERY UNECEESARY, but i plan to work on this application after the coursework
    # on the off chance, barcode number already exists, keep making new ones#
      # generate random 13 digit number
      barcode_id = randint(1000000000000, 10000000000000)
      return barcode_id


### AUTH ###

@app.route('/auth/register', methods=['POST','GET'])
def register(): 
   if request.method == 'GET':
      return render_template('pages/auth/register.html')

   if request.method == 'POST':

      email = request.form['email'].lower() # get email from form
      ## check if email already exists
      if isExistingEmail(email):
         return jsonify({
            "error" : "Email already exists"
         })
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

         # generate token

         token = uuid.uuid4()
         user.verificationCode = str(token)

         db.session.commit()

         # try sending verification email
         try:
            send_verification_email(email, token)

            flash("Sent you a verification email", "success")
            return jsonify({
               "success" : "Sent you a verification email"
            })
         
         except Exception as e:
            print(f"Failed to send verification email to {email} : {e}")
            print("\nError details : "  + str(e))
            return jsonify({
               "error" : "An error occured whilst attempting to send you a verification email"
            })
         
         # send visual feedback

         # redirect to login
         

@app.route('/auth/verify-email/<email>', methods =['GET','POST'])
def verify_email(email):
   if request.method == 'GET':
      return render_template('pages/auth/verify-email.html')
   
   if request.method == 'POST':
      try:
         token = request.form['token']

         user = User.query.filter_by(email=email).first()  # get user by email
         stored_token = user.verificationCode

         if stored_token == token:
            # update user email and verification status
            user.emailVerified = True
            db.session.commit()
            flash("Email verification successful! You can now log in", "success")
            return jsonify({
               "success" : "Email verification succesful"
            })
         else:
            return jsonify({
               "error" : "Invalid or expired verification link"
            })

      except Exception as e:
         print(e)
         return jsonify({
            "error" : 'An error occurred during email verification. Please try again later'
         })


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

            return jsonify({
               "error" : "This email does not exist"
            })
         
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

         if not user.emailVerified:
            return jsonify({
               "error" : "You must verify your email before logging in"
            })

         if check_password_hash(user.passwordHash, password):
            login_user(user)
            flash("Successful Login", "success")
            return jsonify({
               "success" : "Successful Login"
            })
         else:
            return jsonify({
               "error" : "Your password is incorrect, please try again"
            })
         
      except Exception as e:
         print("Error searching for user by email after login post req ")
         print(e)
         return jsonify({
            "error" : "An error occured, pelase try again later"
         })


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
   

@app.route('/auth/forgot_password', methods=['GET', 'POST'])
def forgot_password():
   if request.method == 'GET':
      return render_template('pages/auth/forgot_password.html')
   
   if request.method == 'POST':
      email = request.form['email']
      try:
         user = User.query.filter_by(email=email).first()
         if user:
            reset_code = str(uuid.uuid4())
            send_email(recipients=[email],
                        title="Reset Your Password", 
                        body=url_for('reset_password', 
                                     email=user.email, 
                                     reset_code=reset_code, 
                                     _external = True)
                        )
            user.resetCode = reset_code
            db.session.commit()

            flash("If your email is in our system, you'll receive a password reset", "success")
            return redirect(url_for('login'))
         else:
            flash("Please register first", "error")
            print("Email doesn't exist in db")
            return redirect(url_for('login'))
      except Exception as e:
         flash("Sorry, an error occurred", "error")
         print(e)

         
@app.route('/auth/reset_password/<email>/<reset_code>', methods=['GET', 'POST'])
def reset_password(email, reset_code):
   if request.method == 'GET':
      try:
         user = User.query.filter_by(email=email).first()
         if user and (reset_code == user.resetCode):
            return render_template('pages/auth/password_reset.html', email=email, reset_code=reset_code)
         else:
            flash("Invalid reset code", "error")
      except Exception as e:
         print(e)
         flash("Invalid reset link", "error")
      return redirect(url_for('login'))

   if request.method == 'POST':
      try:
         user = User.query.filter_by(email=email).first()
         password = request.form['password']
         if user and (reset_code == user.resetCode):
            user.passwordHash = generate_password_hash(password, salt_length = 10)

            flash("Password was succesfully changed", "success")
            return jsonify({
               "success" : "password succesfully changed"
            })
         else:
            return jsonify({
               "error" : "Invalid credentials"
            })
      except Exception as e:
         print(e)
         return jsonify({
            "error" : "An error occured"
         })


### DASHBOARD ### 
@app.route('/dashboard')
@login_required
def dashboard():
   return render_template('pages/dashboard.html',
                          forename=current_user.forename,
                          is_super_user = isSuperUser(current_user)
                          ) 



@app.route('/dashboard/notifications', methods=['GET','POST'])
@login_required
def notifications():
   if request.method == 'GET':
      try:
         # get all notifications for this user, reverse order for ux
         notifications = Notification.query.filter_by(
            user_id = current_user.get_id()
            ).order_by(Notification.sent_at.desc()).all()
         
         return render_template('pages/notifications.html', notifications = notifications)
      except Exception as e:
         print(f"Error fetching notifications for user {current_user.get_id()}")
         print(e)
         flash("Error retrieving your notifications", "error")
         return redirect(url_for('all_events'))


### EVENTS ### 

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
         max_tickets_per_user = request.form['max_tickets_per_user']
         
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
               max_tickets_per_user=max_tickets_per_user
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

            print("Event created")

            return jsonify({
               "success" : "Event Was Succesfully Created"
            })

         except Exception as e:
         
            print("Error occured trying to create a new event and adding it to the database")
            print(e)
            return jsonify({
               "error" : "An error occured whilst trying to create an event"
            })
         
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

@login_required   
@app.route('/events/cancel/<int:event_id>', methods =['PUT'])
def cancel_event(event_id):
   if isSuperUser(current_user):
      try:
         event = Event.query.get(event_id)
      except Exception as e:
         print(e)
         print(f"Erorr occured trying to get details for event {event_id}")
         return jsonify({
            "error" : "Error fetching event details"
         })
      
      if event is None:
         print(f"Event does not exist {event_id}")
         return jsonify({
            "error" : "This event doesn't exist"
         })
      else:
         
         # cancel the event
         event.cancelled = True

         # send notification to 
         send_notification(
            title="Event Cancelled",
            description= f"Event {event.name} was cancelled",
            user_id= current_user.id
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

         return jsonify({
            "success" : f"{event.name} has been cancelled"
         })
   else:
      flash("Only superuser can cancel events", "error")
      return redirect(url_for('dashboard'))

        
@login_required
@app.route('/events/book/<int:event_id>', methods=['GET','POST'])
def book_ticket(event_id):
   # check capacity of the event being booked
   try:
      event = Event.query.get(event_id)
      if not event:
         print(f"Event id {event_id} doesn't exist")
         return jsonify({
            "error" : "This event doesn't exist"
         })

      # in the rare case that someone else just snatched a ticket
      elif event.tickets_allocated == event.capacity:
         return jsonify({
            "error" : "This event is now full"
         })

      # check for number of tickets user has for this event

      # generate random 15 digit number ( i think thats the standard )
      # https://www.geeksforgeeks.org/how-to-generate-barcode-in-python/

      # generate barcode
      

      user_tickets = Ticket.query.filter_by(user = current_user, event=event).count()
      if user_tickets >= event.max_tickets_per_user:    
      ## TODO finished here
         return jsonify({
            "error" : f"You've booked the maximum amount of tickets for this event",
         })

      barcode = EAN13(str(generate_barcode_id()))
      barcode_id = int(barcode.ean)
      #barcode_path = f"static/assets/barcodes/{barcode_id}.png"
      #barcode.save(barcode_path)
      
      ticket = Ticket(
         user_id = current_user.get_id(), 
         event_id = event.id,
         barcode_id = barcode_id
      )

      db.session.add(ticket)
      db.session.commit()

      barcode = Barcode(
         id = int(barcode.ean),
         svg_data = barcode.render().decode('utf-8') # decode to ut8 so jinja can use
      )

      db.session.add(barcode)
      db.session.commit()

      barcode = Barcode.query.get(barcode_id)
      print(barcode.get_svg_data())
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

      user_tickets = Ticket.query.filter_by(user = current_user, event=event).count()
      reached_max_tickets = user_tickets >= event.max_tickets_per_user
      ## TODO finished here
      return jsonify({
         "success" : f"You succesfully booked a ticket for {event.name}",
         "max_tickets" : reached_max_tickets
      })

   except Exception as e:
      print(e)
      return jsonify({
         "An error occured whilst trying to book this event", "error"
      })



# tickets
   
@login_required
@app.route('/tickets/my-tickets')
def my_tickets():
   try:
      # get all tickets the user has
      tickets = Ticket.query.filter_by(
         user = current_user
         ).order_by(Ticket.booked_at.desc()).all()

      return render_template('pages/my_tickets.html', tickets = tickets)

   except Exception as e:
      print(e)
      return jsonify({
         "error" : "An error occured"
      })
      


### TICKETS ### 
   
@login_required
@app.route('/tickets/<int:ticket_id>/cancel', methods = ['PUT'])
def cancel_ticket(ticket_id):
   try:
      ticket = Ticket.query.get(ticket_id)
      if ticket.user != current_user:
         return jsonify({
            "error": "You don't own this ticket"
         })
      
      ticket.cancelled = True
      event = Ticket.query.get(ticket_id).event
      event.tickets_allocated -= 1

      send_notification(
         "Ticket Cancellation",
         f"{current_user.forename} {current_user.surname} cancelled their ticket for {event.name}",
         getSuperUser().user_id
         )
      
      return jsonify({
         "success" : "Ticket Cancelled"
      })
   
   except Exception as e:
      return jsonify({
         "error" : "An error occured trying to cancel this ticket"
      })