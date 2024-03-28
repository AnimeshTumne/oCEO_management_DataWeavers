from flask import Flask, render_template, request, redirect, url_for 
from flask import *
from werkzeug.security import generate_password_hash
import os
import flask_mysqldb as mysql
from flask_mysqldb import MySQL
# --------------------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# --------------------------------------------------------------------------------------------------------------------------------------

# Home Page - Select User Type
@app.route('/')
def index():
    return render_template('loginpage_testing.html')

# --------------------------------------------------------------------------------------------------------------------------------------

# Login Pages
@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        # Handle student login authentication
        # Redirect to the query page on successful login
        return redirect(url_for('query_page'))
    return render_template('loginpage_student.html')

@app.route('/login/professor', methods=['GET', 'POST'])
def login_professor():
    if request.method == 'POST':
        # Handle professor login authentication
        # Redirect to the query page on successful login
        return redirect(url_for('query_page'))
    return render_template('loginpage_professor.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        # Handle admin login authentication
        # Redirect to the query page on successful login
        return redirect(url_for('query_page'))
    return render_template('loginpage_admin.html')

# --------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login/new_user', methods=['GET', 'POST'])
def login_new_user():
    if request.method == 'POST':
        # Handle new user registration
        # username = request.form['username']
        # password = request.form['password']
        
        # # Execute the CREATE USER query using the form data
        # query = f"CREATE USER {username} IDENTIFIED BY '{password}'"
        # # Execute the query using your database library
        # # For example, if you are using MySQL library:
        # cur = mysql.connection.cursor()
        # cur.execute(query)
        # mysql.connection.commit()
        # cur.close()
        # Redirect to the query page on successful registration
        return redirect(url_for('nu_aftersubmit'))
    return render_template('loginpage_newuser.html')

# --------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login/nu_aftersubmit', methods=['GET', 'POST'])
def nu_aftersubmit():
    return render_template('loginpage_aftersubmit.html')

# Query Page
# @app.route('/query', methods=['GET', 'POST'])
# def query_page():
#     if request.method == 'POST':
#         # Handle SELECT query execution
#         # Display result if successful, otherwise prompt user to input another query
#         return render_template('query_result.html', result=result)
#     return render_template('query.html')

if __name__ == '__main__':
    app.run(debug=True)
