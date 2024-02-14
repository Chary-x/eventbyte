from flask_sqlalchemy import SQLAlchemy

# create the database interface
db = SQLAlchemy()

# a model of a user for the database
class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.column(db.String, unique = True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.Integer)
    


# put some data into the tables
def dbinit():
    pass

    """
    user_list = [
        User("Felicia"), 
        User("Petra")
        ]
    db.session.add_all(user_list)

    # find the id of the user Felicia
    felicia_id = User.query.filter_by(username="Felicia").first().id

    all_lists = [
        List("Coursework",felicia_id), 
        List("Private Study",felicia_id)
        ]
    db.session.add_all(all_lists)

    # find the ids of the lists Coursework and Private Study

    coursework_id = List.query.filter_by(name="Coursework").first().id
    study_id= List.query.filter_by(name="Private Study").first().id

    all_items = [
        ListItem("CS130",study_id), 
        ListItem("CS131", study_id),
        ListItem("CS139",coursework_id), 
        ListItem("CS132",coursework_id)
        ]
    db.session.add_all(all_items)

    # commit all the changes to the database file
    db.session.commit()

    """