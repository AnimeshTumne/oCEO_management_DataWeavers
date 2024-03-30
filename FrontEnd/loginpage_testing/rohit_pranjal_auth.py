# Assumption: tables already exist: Student_credentials, Prof_credentials, Other_credentials

from flask import Flask, render_template, request, redirect, url_for, session
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


# Home Page - Select User Type
@app.route("/")
def index():
    return render_template("testing.html")


# LOGIN--------------LOGIN-----------------LOGIN--------------------LOGIN------------------LOGIN--------------------LOGIN--------------------LOGIN--------------------------


# check the credentials of the user
def authenticate(email, password):
    cursor = db.connection.cursor()

    sql = f"SELECT hashed_password FROM other_credentials WHERE email='{email}'"
    # cursor.execute(sql, (email,))
    cursor.execute(sql)
    correct_hash = cursor.fetchone()
    cursor.close()

    if bcrypt.check_password_hash(correct_hash[0], password):
        return True
    else:
        return False


# route handling the login page
@app.route("/login/admin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        if authenticate(email, password):
            session["email"] = email
            return redirect(url_for("query_page"))
        else:
            return redirect(url_for("errorpage"))

    return render_template("admin.html")  # page to enter login credentials


# error OR dashboard (based on the credentials)
@app.route("/errorpage", methods=["GET", "POST"])
def errorpage():
    error_message = "GALAT KAR RHE BHAIYA"
    return render_template("testing.html", error_message=error_message)

@app.route("/query", methods=["GET"])
def query_page():
    if "email" in session:
        return render_template("query.html")
    else:
        return redirect(url_for("errorpage"))


# logout from active session
@app.route('/logout/admin', methods=["GET"])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

# REGISTER-----------------------REGISTER--------------------------------REGISTER---------------------------REGISTER-----------------------------------------------


@app.route("/login/new_user", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        userType = request.form.get('userType')
        
        # Check if the username already exists in the database
        cursor = db.connection.cursor()
        userTable=userType+'_credentials'
        sql = f"SELECT * FROM {userTable} WHERE email='{email}'"
        # cursor.execute(sql, (userTable,email))
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            error_message = (
                "User already exists. Please choose a different username."
            )
            return render_template("newuser.html", error_message=error_message)
        else:
            # Insert the new user into the database
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            userTable=userType+'_credentials'
            sql = f"INSERT INTO {userTable} (email, hashed_password) VALUES ('{email}', '{hashed_password}')"
            # cursor.execute(sql, (, email, hashed_password))
            cursor.execute(sql)
            db.connection.commit()
            cursor.close()
            return redirect(url_for("login"))
    else:
        return render_template("newuser.html")


if __name__ == "__main__":
    app.run(debug=True)
