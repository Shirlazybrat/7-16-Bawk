# Import flask stuff
from flask import Flask, render_template, redirect, request, session, jsonify
# import the mysql module
from flaskext.mysql import MySQL
import bcrypt

# set up mySQL connection later
app = Flask(__name__)

app = Flask('sqlConn')
#create an instance of the mysql class
mysql = MySQL()
#add to the app (Flack object) som config data for our connection
app.config['MYSQL_DATABASE_USER'] = 'x' #username is x
app.config['MYSQL_DATABASE_PASSWORD'] = 'x' # password is x
app.config['MYSQL_DATABASE_DB'] = 'bawk'
#where the mysql database is located
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#use the mysql method, init_app, and pass it the flask object
mysql.init_app(app)

#Make one connection and use it over, and over, and over...
conn = mysql.connect()
# set up a cursor object whihc is what the sql object uses to connect and run queries
cursor = conn.cursor()

app.secret_key = "navlksnlakjwa8924hr8qoarhfvpui34"

@app.route('/')
def index():
	current_posts_query = "SELECT * FROM buzz LEFT JOIN user ON buzz.user_id = user.id LEFT JOIN votes on votes.post_id = buzz.id ORDER BY date DESC"
	cursor.execute(current_posts_query)
	current_posts_result = cursor.fetchall()
	return render_template('index.html',
		posts = current_posts_result)

@app.route('/process_vote', methods=['POST'])
def process_vote():
	print "Hello world"
	print session['user_id'] 
	post_id = request.form['vote_id'] #this is the post voted on from jquery ajax
	print post_id
	vote_type = request.form['voteType']
	# print "I am here %s"  % session['username']
	# print "I am here %r"  % session
	
	print vote_type
	print session['username']

	# check to see if the user voted on this item
	check_user_votes_query ="SELECT * FROM votes INNER JOIN user ON user.id = votes.user_id WHERE user.username = '%s' AND votes.post_id = '%s'" % (session['username'], post_id)
	cursor.execute(check_user_votes_query)
	check_user_votes_result = cursor.fetchone()

	
	if check_user_votes_result is None:
		insert_user_vote_query = "INSERT into votes (post_id, user_id, vote_type) values ('"+str(post_id)+"', '"+str(session['user_id'])+"', '"+str(vote_type)+"')"
		cursor.execute(insert_user_vote_query)
		conn.commit()
		cursor.execute(get_new_total_query)
		get_new_total_result = cursor.fetchone()
		return jsonify({'message':"voteChanged", 'voteTotal': get_new_total_result[0]})
		
		# return jsonify("voteCounted")	

	else: 
		check_user_vote_direction_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.user_id WHERE user.username = '%s' AND votes.post_id = '%s' AND votes.vote_type = '%s'" % (session['username'], post_id, vote_type)
		cursor.execute(check_user_vote_direction_query)
		check_user_vote_direction_result = cursor.fetchone()
		if check_user_vote_direction_result is None:
			# User has voted, but not this direction. Update
			update_user_vote_query = "UPDATE votes SET vote_type = '%d' WHERE user_id = '%d' AND post_id = '%d'" % (vote_type, session['user_id'], post_id)
			cursor.execute(update_user_vote_query)
			conn.commit()
			get_new_total_query = "SELECT sum(vote_type as vote_total FROM votes WHERE post_id = '%d' GROUP BY post_id" % post_id
			cursor.execute(get_new_total_result)
			get_new_total_result = cursor.fetchone()
			return jsonify({'message':"voteChanged", 'voteTotal': get_new_total_result[0]})
		else:
			# User has already voted this directino on this post. No dice.
			return jsonify({'messge': "alreadyVoted"})
			
	

	# vote_post_query = "UPDATE current_vote FROM buzz SET buzz.current_vote = buzz.current_vote + 1"
	# cursor.execute(vote_posts_query)
	# vote_posts_result = cursor.fetchall()
	# return render_template('index.html',
	# 	posts = vote_posts_result)


@app.route('/register')
def register():
	if request.args.get('username'):
		# the username is set in the query string
		return render_template('register.html',
			message = "That username is already taken.")
	else:
		return render_template('register.html')


@app.route('/register_submit', methods = ['POST'])
def register_submit():
	# return render_template('register_submit.html')
	# Fist, check to see if the email is already taken
	# this means select statement
	check_username_query = "SELECT * FROM user WHERE username = '%s' " % request.form['username']
	print check_username_query
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	if check_username_result is None:
		# no match. Insert
		real_name = request.form['real_name']
		username = request.form['username']
		password = request.form['password'].encode('utf-8')
		email = request.form['email']
		# avatar = request.form['avatar']
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		print hashed_password
		username_insert_query = "INSERT INTO user VALUES (default, '"+username+"', '"+email+"', '"+hashed_password+"', null, '"+real_name+"')"
		cursor.execute(username_insert_query)
		conn.commit()
		session['username'] = username
		return render_template('index.html')
	else: 
		return redirect('/register?username=taken')
	print check_username_result
	return "Done"

	# second, if it is taken, send thmt back to the register page with a message
	# if not taken, insert into sql



@app.route('/sign_in', methods=['GET','POST'])
def sign_in():
	return render_template('sign_in.html')


@app.route('/sign_in_submit', methods=['POST'])
def sign_in_submit():
 	password = request.form['password'].encode('utf-8')
 	hashed_password_from_mysql = "SELECT password, id FROM user WHERE username = '%s'" % request.form['username']
 	cursor.execute(hashed_password_from_mysql)
 	hashed_password = cursor.fetchone()
 	check_username_result = hashed_password[1]
	#to check a hash
	if hashed_password == None:
		return render_template("/sign_in.html",
 			message = "Cannot find you in the system. Try Again")
	if bcrypt.checkpw(password, hashed_password[0].encode('utf-8')):	
 		session['username'] = request.form['username']
 		session['user_id'] = check_username_result
 		print session['user_id']
 		return redirect('/')
 	else: 
 		return render_template("/sign_in.html",
 			message = "Wrong password. Try Again")

@app.route('/logout')
def logout():
	#nuke the session vars. This will end the session which is what we use to let the user in
	session.clear()
	return redirect('/sign_in?YouAreLogedOut')


@app.route('/post_submit', methods=["POST"])
def post_submit():
	post_content = request.form['post_content']
	get_user_id_query = "SELECT id FROM user WHERE username = '%s'" % session['username']
	print session['username']
	cursor.execute(get_user_id_query)
	get_user_id_result = cursor.fetchone()
	user_id = get_user_id_result[0]
	print user_id
	insert_post_query = "INSERT INTO buzz (user_id, post_content, current_vote) VALUES ("+str(user_id)+", '"+post_content+"', 0)"
	cursor.execute(insert_post_query)
	conn.commit()
	return redirect('/')

@app.route('/follow')
def follow():
	get_all_not_me_users_query = "SELECT * FROM user WHERE id != '%s' " % session['id'] 
	
	get_all_following_query = "SELECT * FROM follow LEFT JOIN user ON user.id = follow.uid_of_user_following = '%s'" % session['id']
	
	# who user is get_all_following_query
	# we want username and id
	get_all_following_query = "SELECT u.username, f.uid_of_user_followed FROM follow f  LEFT JOIN user u ON u.id = f.uid_of_user_followed WHERE f.uid_of_user_following = '%s'" % session['id']
	cursor.execute(get_all_following_query)
	get_all_following_result = cursor.fetchall()
	# who is the user not following
	# who user is not following -- all users in the table minus those user is following
	get_all_not_following_query = "SELECT * FROM user WHERE id NOT IN (SELECT uid_of_user_followed WHERE uid_of_user_following = '%s') AND id != '%s')" % (session['id'], session['id'])
	cursor.execute(get_all_not_following_query)
	get_all_not_following_result = cursor.fetchall()


	return render_template('follow.html',
		following_list = get_all_following_result,
		not_following_list = get_all_not_following_result)

@app.route('/follow_user')
def follow_user():
	user_id_to_follow = request.args.get('user_id')
	follow_query = "INSERT INTO follow (uid_of_user_followed, uid_of_user_following) VALUES ('%s', '%s')" %(user_id_to_follow, session['id'])
	# return unfollow_query
	cursor.execute(follow_query)
	conn.commit()
	return redirect('/follow')

@app.route('/unfollow_user')
def unfollow_user():
	user_id_to_unfollow = request.args.get('user_id')
	unfollow_query = "DELETE FROM follow WHERE uid_id_user_followed = '%s' AND uid_of_user_following = '%s'" %(user_id_to_unfollow, session['id'])
	cursor.execute(unfollow_query)
	conn.commit()
	return redirect('/unfollow')




if __name__ == "__main__":
	app.run(debug= True)