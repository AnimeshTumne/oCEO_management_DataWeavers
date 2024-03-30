from flask import Flask, render_template, request, redirect, url_for 
from flask import *
from werkzeug.security import generate_password_hash
import os
import flask_mysqldb as mysql
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date
# --------------------------------------------------------------------------------------------------------------------------------------

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

# Home Page - Select User Type
@app.route('/')
def index():
    return render_template('testing.html')

# --------------------------------------------------------------------------------------------------------------------------------------

# Login Pages
@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        # Handle student login authentication
        # Redirect to the query page on successful login
        return redirect(url_for('query_page'))
    return render_template('student.html')

@app.route('/login/professor', methods=['GET', 'POST'])
def login_professor():
    if request.method == 'POST':
        # Handle professor login authentication
        # Redirect to the query page on successful login
        return redirect(url_for('query_page'))
    return render_template('professor.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
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
            return render_template('admin.html', error_message=error_message)
            # change the above to redirect to one with an error message
        # return redirect(url_for('query_page'))
    return render_template('admin.html')

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

        # Create new user instance
        # new_user = User(roll_number=roll_number, email=email, password=hashed_password, role=user_type)
        cursor.execute(f"CREATE USER {roll_number} IDENTIFIED BY '{hashed_password}';")
        cursor.commit()
        cursor.close()
        # Add new user to the database
        # db.session.add(new_user)
        # db.session.commit()

        # Redirect to the login page after successful registration
        return redirect(url_for('nu_aftersubmit'))

    return render_template('newuser.html')

# --------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login/nu_aftersubmit', methods=['GET', 'POST'])
def nu_aftersubmit():
    return render_template('aftersubmit.html')

# Query Page
@app.route('/query', methods=['GET', 'POST'])
# def date_converter(o):
#     if isinstance(o, date):
#         return o.__str__()

def query_page():
    
    if request.method == 'POST':
        cursor = db.connection.cursor()
        # Handle SELECT query execution
        query = request.form.get("query")
        # query = "SELECT * FROM application_status;"
        # Execute the query and get the result
        # result = db.execute(query)
        cursor.execute(query)
        mysql.connection.commit()     
        allData = cursor.fetchall()
        # print(data)
        cursor.close()
        # Convert the result to a list of dictionaries
        # data = [dict(row) for row in data]
        # Pass the result to the query result page for display
        # return render_template('queryresult.html', application_status=data)
        # print(type(allData))

        json_string = json.dumps(allData, default=lambda o: str(o) if isinstance(o, (date)) else None)
        return redirect(url_for('query_result', body=json_string))
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
