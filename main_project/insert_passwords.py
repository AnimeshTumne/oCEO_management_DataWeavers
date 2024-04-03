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
        passwords.append("'" + hashed_password + "'")
    
    cur = db.connection.cursor()
    
    # added query to add password column in applied_student table
    query_add_column_password = "ALTER TABLE applied_student ADD COLUMN password VARCHAR(255);"
    # cur.execute(query_add_column_password)
    # rename column Approved to approval
    query_rename_approved_column = "ALTER TABLE application_status RENAME COLUMN Approved TO approval;"
    # cur.execute(query_rename_approved_column)


    query_fetch_roll_numbers = "SELECT roll_number FROM applied_student;"
    cur.execute(query_fetch_roll_numbers)
    roll_numbers = [int(row[0]) for row in cur.fetchall()]

    for i in range(70):
        query_insert_pwd = f"UPDATE applied_student SET password={passwords[i]} WHERE roll_number={roll_numbers[i]};"
        cur.execute(query_insert_pwd)
        db.connection.commit()  

    cur.close()


    
    return render_template("testing2.html")


if __name__ == "__main__":
    app.run(debug=True)

