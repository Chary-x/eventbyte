from flask import Flask, render_template, request


# import models
from app.models import User  

# import db server
from database import db


# initialise  app and db
app = Flask(__name__)
db.init_app(app)



#route to the index
@app.route('/')
def index():
    with open('README.md') as readme:
      with open('requirements.txt') as req:
        return render_template('index.html', README=readme.read(), requirements=req.read())

