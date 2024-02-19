
# flask imports
import pickle
from flask_mail import Mail, Message
from flask import Flask,session, flash, render_template, request, jsonify, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
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

@app.route('/auth/login')
def login():
   return render_template('pages/auth/login.html')

@app.route('/auth/register')
def register():
   return render_template('pages/auth/register.html')

@app.route('/auth/register-user', methods=['POST'])
def register_user():
   if request.method == 'POST':
      email = request.form['email'].lower() # get email from form
      ## check if email already exists
      if isExistingEmail(email):
         flash("Email already exists","error")
         return redirect(url_for('register'))
      else:

         forename = request.form['forename']
         surname = request.form['surname']
         # hash password again with bcrypt
         password = request.form['password']

         # create and add user to db
         user = User(
            email=email,
            forename=forename,
            surname = surname,
            passwordHash= generate_password_hash(password)
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
         
         flash('Email confirmation sent', 'success')

         return redirect(url_for('register'))

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


# todo -> login and forgot password
@app.route('/auth/forgot-password')
def forgot_password():
   pass