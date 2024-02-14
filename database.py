# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


app = Flask(__name__)

# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///prodwork.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set up a 'model' for the data you want to store
from db_schema import db, User, List, ListItem, dbinit

# init the database so it can connect with our app
db.init_app(app)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = False
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()


#route to the index
@app.route('/')
def index():
    items = ListItem.query.all()
    lists = List.query.all()
    return render_template('db_index.html', lists=lists, items=items)
