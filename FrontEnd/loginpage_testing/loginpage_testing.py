from flask import Flask, render_template, request, redirect, url_for 
from flask import *
from werkzeug.security import generate_password_hash
import os
import flask_mysqldb as mysql
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date
import pymysql
# --------------------------------------------------------------------------------------------------------------------------------------

# connecting to the database
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'oceoAdmin'
app.config['MYSQL_PASSWORD'] = 'oceoAdmin'
app.config['MYSQL_DB'] = 'oceo_management'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# db.init_app(app)
db = MySQL(app)

# db = SQLAlchemy()
# change the following to better suit our database:
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     roll_number = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     role = db.Column(db.String(20), nullable=False)

# --------------------------------------------------------------------------------------------------------------------------------------
# MySQL Configuration - currently configured to oceoAdmin
# --------------------------------------------------------------------------------------------------------------------------------------

# Home Page - Select User Type, and if not, register for a new account
@app.route('/')
def index():
    return render_template('testing.html')

# --------------------------------------------------------------------------------------------------------------------------------------
# Student:
@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        # Handle student login authentication
        # Redirect to the query page on successful login
        # return redirect(url_for('query_page'))
        # on successful login, redirect to a page with the student's details like, personal info, jobs available, applied jobs, etc
        return redirect(url_for('after_login_student'))
    return render_template('student.html')

# the below url, /student and all urls linked through here, should only be
# accessible after the student has logged in i.e. after authorisation
@app.route('/student', methods=['GET', 'POST'])
def after_login_student():
    # four buttons - personal info, jobs available, applied jobs, logout
    if request.method == 'GET':
        testvar = request.args['submit_button']
        # personal info button
        if testvar == 'personal_info':
            return redirect(url_for('student_personal_info'))
        # jobs available button
        elif testvar == 'jobs_available':
            return redirect(url_for('student_jobs_available'))
        # isime apply job ka button chahiye

        # applied jobs button
        elif testvar == 'applied_jobs':
            return redirect(url_for('student_applied_jobs'))
        # isime remove application ka button bhi chahiye (?)

        # logout button
        elif testvar == 'logout':
            # isme upar auth ka sambhaalna padenga
            return redirect(url_for('index'))
        
    return render_template('student/after_login.html')

@app.route('/student/personal_info', methods=['GET', 'POST'])
def student_personal_info():
    # show personal info of the student by querying the database
    cursor = db.connection.cursor()
    roll_number = request.form['rollNumber']
    cursor.execute(f"SELECT FROM view_student WHERE roll_number = {roll_number};")
    data = cursor.fetchall()
    cursor.close()
    # add button to change data
    if request.method == 'POST':
        if request.form['submit_button'] == 'change_data':
            return redirect(url_for('student_personal_info_change'))
    return render_template('student/personal_info.html', data=data)

@app.route('/student/personal_info_change', methods=['GET', 'POST'])
def student_personal_info_change():
    # change personal info of the student by querying the database
    if request.method == 'POST':
        # change the personal info of the student in the database
        return redirect(url_for('student_personal_info'))
    return render_template('student/personal_info_change.html')

# query the database and find jobs available that student can apply to
@app.route('/student/jobs_available', methods=['GET', 'POST'])
def student_jobs_available():
    # show jobs available for the student by querying the database
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT * FROM job WHERE is_position_open = 1;")
    job_data = cursor.fetchall()
    cursor.close()
    # add button to apply for a job
    if request.method == 'POST':
        if request.form['submit_button'] == 'apply_job':
            return redirect(url_for('student_apply_job'))
    return render_template('student/jobs_available.html', job_data=job_data)

@app.route('/student/applied_jobs', methods=['GET', 'POST'])
def student_applied_jobs():
    # show jobs applied by the student by querying the database
    # add button to cancel the application
    if request.method == 'POST':
        if request.form['submit_button'] == 'cancel_application':
            return redirect(url_for('student_cancel_application'))
    return render_template('student/applied_jobs.html')

@app.route('/student/apply_job', methods=['GET', 'POST'])
def student_apply_job():
    # apply for a job by querying the database
    if request.method == 'POST':
        # apply for the job in the database
        return redirect(url_for('student_jobs_available'))
    return render_template('student/apply_job.html')

# --------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login/professor', methods=['GET', 'POST'])
def login_professor():
    if request.method == 'POST':
        # Handle professor login authentication
        # Redirect to the query page on successful login
        return redirect(url_for('query_page'))
    return render_template('professor.html')

@app.route('/login/others', methods=['GET', 'POST'])
def login_others():
    if request.method == 'POST':
        # Handle admin login authentication
        admin_username = request.form['username']
        admin_password = request.form['password']

        # Check if admin credentials are valid
        if admin_username == 'admin' and admin_password == 'admin':
            # Redirect to the query page on successful login
            return redirect(url_for('query_page'))
        else:
            # Invalid credentials, show error message
            error_message = "Invalid admin credentials. Please input correct username and password."
            return render_template('others.html', error_message=error_message)
            # change the above to redirect to one with an error message
        # return redirect(url_for('query_page'))
    return render_template('others.html')

# --------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login/new_user', methods=['GET', 'POST'])
def login_new_user():
    
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        roll_number = request.form['rollNumber']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['userType']

        # Hash password
        # hashed_password = generate_password_hash(password)
        hashed_password = password

        # --------------------------------------------------------------------------------------------------------------------------------------
        # Add new user to the database, and grant appropriate view accesses to the particular user by type:

        cursor.execute(f"CREATE USER {roll_number} IDENTIFIED BY '{hashed_password}';")
        # if user_type == 'student':
        #     cursor.execute(f"GRANT SELECT ON view_student TO {roll_number};")
        # elif user_type == 'professor':
        #     cursor.execute(f"GRANT SELECT ON view_professor* TO {roll_number};")
        # elif user_type == 'Admin':
        #     cursor.execute(f"GRANT SELECT ON view_admin* TO {roll_number};")
        # elif user_type == 'Dean':
        #     cursor.execute(f"GRANT SELECT ON view_dean* TO {roll_number};")
        # elif user_type == 'saJs':
        #     cursor.execute(f"GRANT SELECT ON view_SAJS* TO {roll_number};")
        # elif user_type == 'oceoCoordinator':
        #     cursor.execute(f"GRANT SELECT ON view_oceoCoordinator* TO {roll_number};")
        # upper code is very basic - change as needed

        # --------------------------------------------------------------------------------------------------------------------------------------

        cursor.commit()
        cursor.close()
        # Add new user to the database
        # db.session.add(new_user)
        # db.session.commit()

        # Redirect to the login page after successful registration
        # return redirect(url_for('nu_aftersubmit'))
        return redirect(url_for('index'))

    return render_template('newuser.html')

# --------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login/nu_aftersubmit', methods=['GET', 'POST'])
def nu_aftersubmit():
    return render_template('aftersubmit.html')

# --------------------------------------------------------------------------------------------------------------------------------------

# Query Page
@app.route('/query', methods=['GET', 'POST'])
def query_page():
    
    if request.method == 'POST':
        cursor = db.connection.cursor()
        query = request.form['query']

        # try:
        #     cursor.execute(query)
        #     # If there are no syntax errors, the query is valid
        #     valid_query = True
        # except pymysql.Error as e:
        #     # If there is a syntax error, the query is invalid
        #     valid_query = False
        #     error_message = str(e)
        #     return render_template('query.html', error_message=error_message)

        cursor.execute(query)
        
        allData = cursor.fetchall()
        
        # Convert the date attribute to a string representation
        # allData = [{k: str(v) if isinstance(v, date) else v for k, v in row.items()} for row in allData]
        
        cursor.close()
        
        # if query.lower().startswith('insert'):
        db.connection.commit()  # Commit the insert query
            
        if allData:
            json_string = json.dumps(allData, default=lambda o: str(o) if isinstance(o, (date)) else None)
            return redirect(url_for('query_result', body=json_string))
        else:
            return redirect(url_for('nu_aftersubmit'))
            return redirect(url_for('query_input', result="query qyert qyetr"))

        # return redirect(url_for('query_result', body=json.dumps(allData)))
        # return render_template('queryinput.html', result=query)
        
    return render_template('query.html')

# Query Input Page
@app.route('/query/input', methods=['GET', 'POST'])
def query_input():
    result = request.args.get('result')
    return render_template('queryinput.html', result=result)

# Query Result Page
@app.route('/query/result', methods=['GET', 'POST'])
def query_result():
    data = json.loads(request.args.get("body")) # data is list type

    # query = 'select * from application_status'
    # Separate the query string into individual tuples

    # query = [tuple(q.split(',')) for q in query]
    # cursor = db.connection.cursor()
    # cursor.execute(query)
    # result = cursor.fetchall()
    # cursor.close()

    return render_template('queryresult.html', allData=data)

if __name__ == '__main__':
    app.run(debug=True)
