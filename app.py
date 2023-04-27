#!user/ishit/anaconda3/python3

# Imports
import MySQLdb.cursors
import os
import re
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from inference import test_main
from werkzeug.utils import secure_filename


# Initialize flask app
app = Flask(__name__)

# Defining upload folder path
UPLOAD_FOLDER = os.path.join('static', 'Images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Model Configurations
app.config['MODEL_PATH'] = "Trained_Models"
app.config['CLASS_MAP'] = {0: "Normal", 1: "EMCI", 2: "LMCI", 3: "AD"}

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql12613930'
app.config['MYSQL_PASSWORD'] = 'YBv6W6YXiB'
app.config['MYSQL_DB'] = 'sql12613930'

# Initialize MySQL
mysql = MySQL(app)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home',  methods=['GET', 'POST'])
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patientData WHERE patient_id = %s', [session['id']])
        account = cursor.fetchone()
        headings = ("sr_no", "p_id", "date", "image", "diag")
        # data = (("1", "1", "12-04", "image", "diag"),
        #       ("2", "1", "12-04", "image", "diag"),
        #     ("3", "1", "12-04", "image", "diag"))
        cursor1 = mysql.connection.cursor()
        cursor1.execute('SELECT * FROM submissions where patient_id = %s', [session['id']])
        data1 = cursor1.fetchall()
        cursor.execute('SELECT * FROM submissions where patient_id = %s', [session['id']])
        data = cursor.fetchone()
        if data:
            if data['image_path'] is not None and data['image_path'] != '':
                return render_template('home.html', account=account, image_path=data['image_path'], headings=headings, data= data1) # atleast once image uploaded, submit not clciked
        # Upload file flask
        elif request.method == 'POST':
            uploaded_img = request.files['uploaded-file']
            # Extracting uploaded data file name
            img_filename = secure_filename(uploaded_img.filename)
            # Save file in location:app.config['UPLOAD_FOLDER']
            uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename).replace("\\", "/"))
            # Storing uploaded file path in flask session
            session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename).replace("\\",
                                                                                                                "/")

            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # p_id = [session['id']]
            # u_date = date.today()
            # i_path = session['uploaded_img_file_path']
            # cursor.execute(
            #     'INSERT INTO submissions(patient_id,upload_date,image_path) VALUES (%s, %s, %s, %s)',
            #     [p_id, u_date, i_path])
            # mysql.connection.commit()
            return render_template('home.html', account=account, image_path=session['uploaded_img_file_path']) #first time iamge upload by submiting
        return render_template('home.html', account=account, msg='', image_path=None)  #no image ever submitted, submit not pressed

    # User is not loggedin redirect to login page
    return redirect(url_for('login')) #redirects to function login


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
        cursor.execute('SELECT * FROM patientData WHERE email = %s AND passowrd = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['patient_id']
            session['email'] = account['email']
            # Redirect to home page
            return redirect(url_for('home')) #takes session only to home page
        else:
            # Account doesnt exist or email/password incorrect
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
            # Account does not exist and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO patientData(patient_firstname,patient_lastname,dob,gender,email,passowrd,phone) VALUES (%s, %s, %s, %s, %s, %s, %s)', [firstname,lastname,dob,gender,email,password,phone])
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
        cursor.execute('SELECT * FROM submissions WHERE patient_id = %s', [session['id']])
        data = cursor.fetchone()
        print(data)
        # Show the profile page with account info
        return render_template('profile.html', account=account, data=data)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/diagnose', methods=['POST'])
def diagnose():
    # Upload file flask
    if request.method == 'POST':
        uploaded_img = request.files['uploaded-file']
        # Extracting uploaded data file name
        img_filename = secure_filename(uploaded_img.filename)
        # Upload file to database (defined uploaded folder in static path)
        save_file_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename).replace("\\", "/")
        uploaded_img.save(save_file_path)
        session['uploaded_img_file_path'] = save_file_path
        prediction, subject_name = test_main(save_file_path, app.config['MODEL_PATH'].replace("\\", "/"), app.config['CLASS_MAP'])

        # For Displaying Patient name
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from patientData where patient_id=%s',[session['id']])
        account = cursor.fetchone()

        # Insert into submissions table in database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        p_id = [session['id']]
        u_date = date.today()
        i_path = session['uploaded_img_file_path']
        cursor.execute(
            'INSERT INTO submissions(patient_id,upload_date,image_path,diagnosis) VALUES (%s, %s, %s, %s)',
            [p_id, u_date, i_path, app.config['CLASS_MAP'].get(prediction)])
        mysql.connection.commit()
        cursor.execute('SELECT * FROM submissions WHERE patient_id = %s', [session['id']])
        data = cursor.fetchone()

        # for dispalying submissions table content
        headings = ("sr_no", "p_id", "date", "image", "diag")
        cursor1 = mysql.connection.cursor()
        cursor1.execute('SELECT * FROM submissions where patient_id = %s', [session['id']])
        data1 = cursor1.fetchall()

        if data['image_path'] is not None and data['image_path'] != '':
            return render_template('home.html', account=account, image_path=data['image_path'], headings=headings, data=data1)
        else:
            return render_template('home.html', account=account, image_path=None, headings=headings, data=data1)


if __name__ == "__main__":
    app.run(debug=True)
