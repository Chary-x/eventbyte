from database import db



class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.column(db.String, unique = True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.Integer)
    