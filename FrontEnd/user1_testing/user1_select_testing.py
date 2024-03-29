from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

# -----------------------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# -----------------------------------------------------------------------------------------------------------------------------------------

# MySQL Configuration - currently configured to user1
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'oceoAdmin'
app.config['MYSQL_PASSWORD'] = 'oceoAdmin'
app.config['MYSQL_DB'] = 'oceo_management'
mysql = MySQL(app)

# -----------------------------------------------------------------------------------------------------------------------------------------

# define various landing pages below:

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM application_status")
    data = cur.fetchall()
    cur.close()
    print(type(data))
    return render_template('user1_select_testing.html', application_status=data)

# -----------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
