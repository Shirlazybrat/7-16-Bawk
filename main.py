# Import flask stuff
from flask import Flask, render_template, redirect, request, session
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
	return render_template('index.html')

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
 	hashed_password_from_mysql = "SELECT password FROM user WHERE username = '%s' " % request.form['username']
 	cursor.execute(hashed_password_from_mysql)
 	hashed_password = cursor.fetchone()
	#to check a hash
	if hashed_password == None:
		return render_template("/sign_in.html",
 			message = "Try Again")
	if bcrypt.checkpw(password, hashed_password[0].encode('utf-8')):	
 		session['username'] = request.form['username']
 		return redirect('/')
 	else: 
 		return render_template("/sign_in.html",
 			message = "Try Again")

@app.route('/logout')
def logout():
	#nuke the session vars. This will end the session which is what we use to let the user in
	session.clear()
	return redirect('/sign_in?YouAreLogedOut')


if __name__ == "__main__":
	app.run(debug= True)