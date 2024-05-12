from app import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), index=True,unique=True,nullable=False)
    game = db.Column(db.String(25), nullable=False)
    password_hash =  db.Column(db.String(128))
    player = db.relationship('Player', backref='coach', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash,password)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True,nullable=False)
    game = db.Column(db.String(25), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'))
    charts = db.relationship('Charts', backref='player')
    rawdata = db.relationship('RawData', backref='player')
    
    
class Charts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    charts = db.Column(db.LargeBinary)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))


class RawData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_data = db.Column(db.Text)
    creation_date = db.Column(db.DateTime(timezone=True), default=datetime.now)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))