import json
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash
from models import db, User, Chatroom, Message

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'

db.init_app(app)

chatroom_id = 0
message_list = []
old_message_id_list = []
not_a_member_flag = False

@app.cli.command('initdb')
def initdb_command():
	"""Reinitializes the database"""
	db.drop_all()
	db.create_all()

# By default, direct to login
@app.route("/")
def default():
	return redirect(url_for("login"))
	
@app.route("/login/", methods=['GET', 'POST'])
def login():
	# First check if the user is already logged in
	if "username" in session:
		flash("Already logged in!")
		return redirect(url_for("browse_chatrooms", username=session['username']))

	# If not, and the incoming request is via POST, try to log them in
	if request.method == "POST":
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None or user.password != request.form['password']:
			flash("Invalid username and/or password.")
		else:
			session['username'] = request.form['username']
			flash("You are now logged in.")
			return redirect(url_for("browse_chatrooms"))

	# If all else fails, offer to log them in
	return render_template("login.html")

@app.route("/logout/")
def logout():
	# If logged in, log out, otherwise offer to log in
	if "username" in session:
		# Note, here we're calling the .clear() method for the python dictionary built-in
		session.clear()
		# Flashes are stored in session["_flashes"], so we need to clear the session /before/ we set the flash message!
		flash("Successfully logged out!")
	else:
		flash("Not currently logged in!")	
	return redirect(url_for("login"))

@app.route("/register/", methods=['GET', 'POST'])
def register():
	"""Registers the user."""
	if "username" in session:
		flash("Already logged in!")
		return redirect(url_for("browse_chatrooms", username=session['username']))
	if request.method == "POST":
		user = User.query.filter_by(username=request.form['username']).first()
		if not request.form['username']:
			flash("You have to enter a username")
		elif not request.form['password']:
			flash("You have to enter a password")
		elif request.form['password'] != request.form['password2']:
			flash("The two passwords do not match")
		elif user is not None:
			flash("The username is already taken")
		else:
			db.session.add(User(request.form['username'], request.form['password'], 0))
			db.session.commit()
			flash("You were successfully registered and can login now")
			return redirect(url_for("login"))
	return render_template("register.html")

@app.route("/createChatroom/", methods=['GET', 'POST'])
def create_chatroom():
	if request.method == "POST":
		chatroom = Chatroom.query.filter_by(name=request.form['name']).first()
		if chatroom is not None:
			flash("The chatroom name is already taken")
		else:
			db.session.add(Chatroom(request.form['name']))
			db.session.commit()
			flash("You have successfully created a new chat room")
			return redirect(url_for('browse_chatrooms'))
	return render_template('createChatroom.html')

@app.route("/browseChatrooms/", methods=['GET', 'POST'])
def browse_chatrooms():
	user = User.query.filter_by(username=session['username']).first()
	chatroom = Chatroom.query.get(user.chatroom_id)
	if user.chatroom_id != 0 and chatroom is not None:
		currentChatroom = chatroom.name
	else:
		currentChatroom = "None"
	chatrooms = Chatroom.query.all()
	return render_template('browseChatrooms.html', currentChatroom=currentChatroom, chatrooms=chatrooms)

@app.route("/chatroom/", methods=['GET', 'POST'])
def chatroom():
	global chatroom_id, not_a_member_flag
	chatroom_id = request.args.get("id")
	chatroom = Chatroom.query.get(chatroom_id)
	if chatroom is None:
		flash("Requested chatroom does not exist")
		return redirect(url_for("browse_chatrooms"))
	not_a_member_flag = False
	old_message_id_list.clear()
	return render_template("chatroom.html", name=chatroom.name)

@app.route("/chatroom/join/", methods=['GET', 'POST'])
def join_chatroom():
	global chatroom_id
	chatroom_id = request.args.get("id")
	chatroom = Chatroom.query.get(chatroom_id)
	if chatroom is None:
		flash("Requested chatroom does not exist")
		return redirect(url_for("browse_chatrooms"))
	user = User.query.filter_by(username=session['username']).first()
	user.chatroom_id = chatroom.id
	db.session.commit()
	flash("You have successfully joined a chatroom")
	return redirect(url_for("browse_chatrooms"))

@app.route("/chatroom/leave/", methods=['GET', 'POST'])
def leave_chatroom():
	global chatroom_id
	user = User.query.filter_by(username=session['username']).first()
	user.chatroom_id = 0
	db.session.commit()
	flash("You have successfully left a chatroom")
	return redirect(url_for("browse_chatrooms"))

@app.route("/chatroom/delete/", methods=['GET', 'POST'])
def delete_chatroom():
	chatroom_id = request.args.get("id")
	chatroom = Chatroom.query.get(chatroom_id)
	if chatroom is None:
		flash("Requested chatroom does not exist")
		return redirect(url_for("browse_chatrooms"))
	Message.query.filter_by(chatroom_id=chatroom.id).delete()
	User.query.filter_by(username=session['username']).update({User.chatroom_id: 0})
	db.session.delete(chatroom)
	db.session.commit()
	flash("You have successfully deleted a chatroom")
	return redirect(url_for("browse_chatrooms"))

@app.route("/newMessage", methods=['POST'])
def post_message():
	global not_a_member_flag
	user = User.query.filter_by(username=session['username']).first()
	if int(user.chatroom_id) == int(chatroom_id):
		message = json.loads(request.form['message'])
		db.session.add(Message(message, user.id, chatroom_id))
		db.session.commit()
	return "OK!"

@app.route("/messages")
def get_messages():
	global not_a_member_flag
	message_list.clear()	
	user = User.query.filter_by(username=session['username']).first()
	if int(user.chatroom_id) != int(chatroom_id):
		if not_a_member_flag == False:
			message_list.append(["", "You are not a member of this chatroom"])
			not_a_member_flag = True
	else:
		messages = Message.query.filter_by(chatroom_id=chatroom_id).all()
		for message in messages:
			if message.id not in old_message_id_list:
				user = User.query.get(message.user_id)
				message_list.append([user.username + ": ", message.content])
				old_message_id_list.append(message.id)	
	return json.dumps(message_list)

# Needed to use sessions
# Note that this is a terrible secret key
app.secret_key = "Jason's secret key"
