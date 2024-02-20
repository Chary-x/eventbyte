
# flask imports
import pickle
from flask_mail import Mail, Message
from flask import Flask,session, flash, render_template, request, jsonify, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional
# database imports

# sec imports
import os
from dotenv import load_dotenv

# model class imports
from content.models import db, dbinit, User

load_dotenv()
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
BASE_URL = os.getenv('BASE_URL')

mail = Mail(app)

#print(app.config.items())
#select datbase filename, other configs

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventbyte.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialise database ~ connect to app and add database
db.init_app(app)

resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

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
   link = f"{BASE_URL}{url_for('verify_email', email=email, token=token)}"
   message = Message('Email Verification Link', recipients=[email])
   message.body = f'Click the link to verify your email\n {link}'
   print(f"Trying to send {message.body} To {email}")
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
         if not user.emailVerified:
               flash('Unsucessful verification', 'error')
               return redirect(url_for('register'))
         else:
               return redirect(url_for('login'))
      else:
         flash('Invalid or expired verification link', 'error')
   except Exception as e:
      flash('An error occurred during email verification, Please try again later', 'error')
   return redirect(url_for('login')) # redirect to login


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

         if not user.emailVerified:
            flash("You must verify your email before logging in", "error")
            return redirect(url_for('login'))
         
         if check_password_hash(user.passwordHash, password):
            flash("Successful Login", "success")
            print("Succesful Login")
            # Store the user id in session... TODO : create a more secure method, like tokenising again
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))  # redirect to the dashboard route
         else:
               flash("Your password is incorrect, please try again", "error")
               return redirect(url_for('login'))  # redirect to login

      except Exception as e:
         print("Error searching for user by email after login post req ")
         print(e)
         flash("An error occurred. Please try again later.", "error")
         return redirect(url_for('login'))  # redirect to the login route

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
@app.route('/auth/forgot-password')
def forgot_password():
   pass


# dashboard routes
@app.route('/dashboard')
def dashboard():
   return render_template('pages/dashboard.html') 
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


@app.route('/events/upcoming')
def upcoming_events():
   pass


@app.route('/events/create', methods=['GET','POST'])
def create():
   pass