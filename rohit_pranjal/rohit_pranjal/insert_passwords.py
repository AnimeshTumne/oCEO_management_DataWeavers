from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
import re
import string

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'mySecretKey'

github_query = '''
create a python code which will generate 70 random passwords following the regex /^(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$/, then create their hashed version using bcrypt  and these hashed strings into password column of applied_student_test in the database db'''

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "oceoAdmin"
app.config["MYSQL_PASSWORD"] = "oceoAdmin"
app.config["MYSQL_DB"] = "oceo_management"

db = MySQL(app)


def generate_random_password(regex):
    while True:
        password = generate_random_string()
        if re.match(regex, password):
            return password

def generate_random_string():
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choice(characters) for _ in range(8))

@app.route("/")
def index():

    passwordRegex = r'^(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$'

    passwords = []
    for _ in range(70):
        password = generate_random_password(passwordRegex)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        passwords.append(hashed_password)
    
    # Insert hashed passwords into the database
    cur = db.connection.cursor()
    password_tuples = ",".join(["('"+password+"')" for password in passwords])

    query_insert_pwd = f"INSERT INTO applied_student_test (password) VALUES {password_tuples};"
    cur.execute(query_insert_pwd)
    db.connection.commit()
    cur.close()
    return render_template("testing2.html")


if __name__ == "__main__":
    app.run(debug=True)

