from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'mySecretKey'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "oceoAdmin"
app.config["MYSQL_PASSWORD"] = "oceoAdmin"
app.config["MYSQL_DB"] = "oceo_management"

db = MySQL(app)

# ------------------------------------------------------------------------------------------------------

@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form["username"]
        password = request.form["password"]

        # fetch roll number from database

        if authenticate(email, password, "student"):
            cursor = db.connection.cursor()
            sql = f"SELECT roll_number FROM applied_student WHERE email_id='{email}'"
            cursor.execute(sql)
            roll_number = cursor.fetchone()[0]
            cursor.close()
            # ACTIVATES THE SESSION (logged in)
            session["roll_number"] = roll_number
            # Render a template with JavaScript to show a popup
            return redirect(url_for('after_login_student'))
            return render_template_string(f"""
                <script>
                    // Show popup
                    alert("Successfully logged in as a Student. Successfully Executed:{sql}'");
                    // Redirect to the desired page
                    window.location.href = "{{{{ url_for('after_login_student') }}}}";
                </script>
            """)
        else:
            return render_template("errorpage.html", error_message="Bad Credentials! Change password or email, and try again.")

    return render_template('student.html')

@app.route('/login/professor', methods=['GET', 'POST'])
def login_professor():
    if request.method == 'POST':
        email = request.form["username"]
        password = request.form["password"]

        if authenticate(email, password, "professor"):
            # ACTIVATES THE SESSION (logged in)
            # fetch faculty id from database
            cursor = db.connection.cursor()
            sql = f"SELECT faculty_id FROM faculty WHERE email_id='{email}'"
            cursor.execute(sql)
            faculty_id = cursor.fetchone()[0]
            cursor.close()
            session["faculty_id"] = faculty_id
            return redirect(url_for('after_login_professor'))
            return render_template_string(f"""
                <script>
                    // Show popup
                    alert("Successfully logged in as a Professor. Successfully Executed:{sql}'");
                    // Redirect to the desired page
                    window.location.href = "{{{{ url_for('after_login_professor') }}}}";
                </script>
            """)
            # return redirect(url_for("after_login_professor"))
        else:
            return redirect(url_for("errorpage", error_message="Bad Credentials! Change password or email, and try again."))
    return render_template('professor.html')

@app.route('/login/others',  methods=['GET', 'POST'])
def others_login(): 
    if request.method == 'POST':
        email = request.form["username"] 
        password = request.form["password"]
        userType = request.form["userType"]
        # #fetch roll number from database
        # cursor = db.connection.cursor()
        # sql = f"SELECT user_type FROM other WHERE email='{email}'"
        # cursor.execute(sql)
        # user= cursor.fetchone()[0]
        # cursor.close()

        if authenticate(email, password, "others"):
            # ACTIVATES THE SESSION (logged in)
            session["email"] = email
            if userType == 'Admin':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'admin';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_home", type = 'admin'))
                else:
                    return redirect(url_for("errorpage"))
            elif userType == 'Dean':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'dean';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_home", type = 'dean'))
                else:
                    return redirect(url_for("errorpage"))
                
            elif userType == 'SA JS':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'sa_js';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_home", type = 'sa_js'))
                else:
                    return redirect(url_for("errorpage"))
                
            elif userType == 'oCEO Coordinator':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'oceo_coordinator';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_home", type = 'oceo_coordinator'))
                else:
                    return redirect(url_for("errorpage"))
            # elif userType =='accounts':
            #     cursor = db.connection.cursor()
            #     sql = "SELECT email FROM other WHERE user_type = 'accounts';"
            #     cursor.execute(sql)
            #     admin_email =  cursor.fetchone()[0]
            #     # admin_email = cursor.fetchall()[0]
            #     print("33333333333333333333333333333333333333333333333333333333333333333333333")
            #     print("33333333333333333333333333333333333333333333333333333333333333333333333")
            #     print(admin_email)
            #     print("33333333333333333333333333333333333333333333333333333333333333333333333")
            #     print("33333333333333333333333333333333333333333333333333333333333333333333333")
            #     cursor.close()

            #     if admin_email == email :
            #         return redirect(url_for("others_home", type = 'accounts'))
            #     else:
            #         return redirect(url_for("errorpage", message="Invalid Credentials for accounts login"))    
                
            
        else:
            return redirect(url_for("errorpage", message="Invalid Credentials for <type> login"))
    return render_template('others.html')

# -----------------------------------------------------------------------------------------------------

@app.route("/errorpage")
def errorpage(error_message="Bad Credentials! Go back and try again."):
    # error_message = "Bad Credentials!"
    return render_template("errorpage.html", error_message=error_message if error_message else "You are not authorised to view this page. Please login first.")

# ------------------------------------------------------------------------------------------------------
# check the credentials of the user 
def authenticate(email, password, userType):
    cursor = db.connection.cursor()
    if userType == "student":
        sql = f"SELECT COUNT(*) FROM applied_student WHERE email_id='{email}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result[0] > 0:
            sql = f"SELECT password FROM applied_student WHERE email_id='{email}'"
        else:
            return False
    elif userType == "professor":
        sql = f"SELECT COUNT(*) FROM faculty WHERE email_id='{email}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result[0] > 0:
            sql = f"SELECT password FROM faculty WHERE email_id='{email}'"
        else:
            return False
        # sql = f"SELECT password FROM faculty WHERE email_id='{email}'"
    elif userType == "others":
        sql = f"SELECT COUNT(*) FROM other WHERE email='{email}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result[0] > 0:
            sql = f"SELECT password FROM other WHERE email='{email}'"
        else:
            return False
        sql = f"SELECT password FROM other WHERE email = '{email}'"
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    if bcrypt.check_password_hash(result[0], password):
        return True
    else:
        return False
