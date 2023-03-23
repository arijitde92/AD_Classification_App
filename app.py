from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from werkzeug.utils import secure_filename

# *** Backend operation

# WSGI Application
# Defining upload folder path
UPLOAD_FOLDER = os.path.join('static', 'Images')
# # Define allowed files
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql12607691'
app.config['MYSQL_PASSWORD'] = '4FwHRIgU2j'
app.config['MYSQL_DB'] = 'sql12607691'
print(app.config)

# Intialize MySQL
mysql = MySQL(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home',  methods=['GET', 'POST'])
def home():
    msg_diagnised=''
    # Check if user is loggedin
    if 'loggedin' in session:
        print(session)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patientData WHERE patient_id = %s', [session['id']])
        account = cursor.fetchone()
        if account['image_path'] is not None and account['image_path'] != '':
            return render_template('home.html', account=account, image_path=account['image_path'])
        # Upload file flask
        elif request.method == 'POST':
            uploaded_img = request.files['uploaded-file']
            # Extracting uploaded data file name
            img_filename = secure_filename(uploaded_img.filename)
            # Upload file to database (defined uploaded folder in static path)
            uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename).replace("\\", "/"))
            email = session['email']
            session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename).replace("\\", "/")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE patientData SET image_path=%s where email=%s',
                           (session['uploaded_img_file_path'], email))
            # Storing uploaded file path in flask session
            mysql.connection.commit()
            # msg = 'You have successfully uploaded image!'
            return render_template('home.html', account=account, image_path=session['uploaded_img_file_path'])
        return render_template('home.html', account=account, msg='', image_path=None)

    # User is not loggedin redirect to login page
    return redirect(url_for('login')) #function login

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patientData WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['patient_id']
            session['email'] = account['email']
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home')) #takes session only to home page
        else:
            # Account doesnt exist or firstname/password incorrect
            msg = 'Incorrect email/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('firstname', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "firstname", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'dob' in request.form and 'email' in request.form and 'password' in request.form and 'phone' in request.form:
        # Create variables for easy access
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        # address = request.form['address']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patientData WHERE email = %s', [email])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            msg = 'firstname must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', lastname):
            msg = 'lastname must contain only characters and numbers!'
        elif not email or not password or not phone:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO patientData(patient_firstname,patient_lastname,dob,gender,email,password,phone) VALUES (%s, %s, %s, %s, %s, %s, %s)', (firstname,lastname,dob,gender,email,password,phone))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('index.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patientData WHERE patient_id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info

        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":

    app.run(debug=True)
