
# flask imports
from flask import Flask, render_template

# database imports


# model class imports
from content.models import db, dbinit, User


app = Flask(__name__)

#select datbase filename
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