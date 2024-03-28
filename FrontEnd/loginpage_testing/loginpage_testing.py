from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home Page - Select User Type
@app.route('/')
def index():
    return render_template('loginpage_testing.html')

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

@app.route('/login/successful_test', methods=['GET', 'POST'])
def login_successful():
    return render_template('loginpage_successful.html')

# Query Page
@app.route('/query', methods=['GET', 'POST'])
def query_page():
    if request.method == 'POST':
        # Handle SELECT query execution
        # Display result if successful, otherwise prompt user to input another query
        return render_template('query_result.html', result=result)
    return render_template('query.html')

if __name__ == '__main__':
    app.run(debug=True)
