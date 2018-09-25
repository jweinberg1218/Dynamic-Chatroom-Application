from flask_sqlalchemy import SQLAlchemy

### Initialize

db = SQLAlchemy()

### Models

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80), unique=False)
	chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'))

	def __init__(self, username, password, chatroom_id):
		self.username = username
		self.password = password
		self.chatroom_id = chatroom_id
		
	def __repr__(self):
		return '<User %r>' % self.username

class Chatroom(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	messages = db.relationship('Message', backref='chatroom', lazy='dynamic')

	def __init__(self, name):
		self.name = name

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(255), unique=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'))

	def __init__(self, content, user_id, chatroom_id):
		self.content = content
		self.user_id = user_id
		self.chatroom_id = chatroom_id