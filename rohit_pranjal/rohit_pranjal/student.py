from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask import Flask
import random

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "oceoAdmin"
app.config["MYSQL_PASSWORD"] = "oceoAdmin"
app.config["MYSQL_DB"] = "oceo_management"

db = MySQL(app)

# ------------------------------------------------------------------------------------------------------
# check the credentials of the user
def authenticate(email, password):
    cursor = db.connection.cursor()

    sql = "SELECT hashed_password FROM student_credentials WHERE email=%s"
    cursor.execute(sql, (email,))
    result = cursor.fetchone()
    cursor.close()
    if bcrypt.check_password_hash(result["hashed_password"], password):
        return True
    else:
        return False

# DONE
@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form["username"]
        password = request.form["password"]

        if authenticate(email, password):
            session["email"] = email
            return redirect(url_for("after_login_student"))
        else:
            return redirect(url_for("errorpage"))

    return render_template('student.html')

# DONE
@app.route("/errorpage")
def errorpage():
    error_message = "Bad Credentials!"
    return render_template("admin.html", error_message=error_message)


# -----------AUTHORISED ACCESS ONLY----------------------------------------------------------------

# DONE
@app.route('/student', methods=['GET', 'POST'])
def after_login_student():
    if "email" in session:
        # STUDENT HOMEPAGE
        
        if request.method == 'POST':
            testvar = request.args['submit_button']
            match testvar:
                case 'personal_info':
                    return redirect(url_for('student_personal_info'))
                case 'jobs_available':
                    return redirect(url_for('student_jobs_available')) # APPLY FOR JOB
                    # isime apply job ka button chahiye
                case 'applied_jobs':
                    return redirect(url_for('student_applied_jobs')) # REMOVE APPLICATION
                case 'logout':
                    return redirect(url_for('index')) # LOGOUT
                case _:
                    return render_template('student/after_login.html')  
            
        return render_template('student/after_login.html')
    
    else:
        return redirect(url_for('errorpage'))

# DONE
@app.route('/student/personal_info', methods=['GET', 'POST'])
def student_personal_info():
    if "email" in session:
        # fetch all info from database using email id
        cursor = db.connection.cursor()
        email = session["email"]
        cursor.execute(f"SELECT * FROM applied_student WHERE email_id = {email};")
        fetched_data = cursor.fetchall()

        #fetch column names
        cursor.execute("SHOW COLUMNS FROM applied_student")
        student_head = cursor.fetchall()
        column_names = tuple(row[0] for row in student_head)
        cursor.close()

        # profile update
        if request.method == 'POST':
            if request.form['submit_button'] == 'change_data': 
                return redirect(url_for('student_personal_info_change'))
        
        return render_template('student/personal_info.html', student_data=fetched_data, student_head = column_names)
    
    else:
        return redirect(url_for('errorpage'))

# DONE
@app.route('/student/jobs_available', methods=['GET', 'POST'])
def student_jobs_available():
    if "email" in session:
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT job.* FROM job LEFT JOIN application_status ON job.job_id = application_status.job_id AND application_status.roll_number = 20110015 WHERE job.is_position_open = 1 AND (application_status.application_id IS NULL);")
        job_data = cursor.fetchall()

        # fetch column names ___
        cursor.execute("SHOW COLUMNS FROM job")
        job_head = cursor.fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
        if request.method == 'POST':
            if request.form['submit_button'] == 'apply_job':
                return redirect(url_for('student_apply_job'))    
        return render_template('student/jobs_available.html', job_data=job_data, job_head = column_names)
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/apply_job', methods=['GET', 'POST'])
def student_apply_job():
    if "email" in session:
        if request.method == 'POST': # submits the application
            cursor = db.connection.cursor()

            # logic to generate new application_id
            # if no id exists, then generate random id, otherwise increment the max id by 1
            cursor.execute("SELECT count(*) FROM application_status")
            total_count = cursor.fetchone()[0]
            if total_count == 0:
                application_id = random.randint(12345678, 29999999)
            else:
                cursor.execute("SELECT MAX(application_id) FROM application_status")
                max_id = cursor.fetchone()[0]
                application_id = max_id + 1

            # fetch other filled information
            job_id = request.form['job_id']
            roll_number = request.form['roll_number']
            so_motivation = request.form['statement_of_motivation']

            # queries for 3 tables
            sql_app_id = f"INSERT INTO application_status (application_id, faculty_approved, oceo_coordinator_approved, SA_approved, dead_approved, statement of motivation, roll_number, job_id, approval) VALUES ({application_id}, 0, 0, 0, 0, {so_motivation}, {roll_number}, {job_id}, 'pending');"

            sql_job_id = f"INSERT INTO job_application (job_id, application_id) VALUES ({job_id}, {application_id});"
            sql_student_id = f"INSERT INTO student_application (roll_number, application_id) VALUES ({roll_number}, {application_id});"

            # fill each table with new application info
            cursor.execute(sql_app_id)
            cursor.execute(sql_job_id)
            cursor.execute(sql_student_id)
            db.connection.commit()
            cursor.close()

            return redirect(url_for('student_jobs_available'))
        
        return render_template('student/apply_job.html') # only show the unapplied jobs || Don't allow applying for already filled job
    else:
        return redirect(url_for('errorpage'))


# TODO: unsure if application_id captured by each cancel button correctly
# PENDING: fetch roll number from profile && cancel button (in each row) fetches the application_id when pressed && landing page after cancellation 
@app.route('/student/applied_jobs', methods=['GET', 'POST'])
def student_applied_jobs():
    if "email" in session:
        # fetch roll_number of student from profile
        cursor = db.connection.cursor()
        sql = f"SELECT roll_number FROM applied_student where email = {session['email']};"
        cursor.execute(sql)
        roll_number = cursor.fetchone()[0]

        # fetch applied jobs
        sql = f"SELECT application_status.application_id, job.job_id, job.job_type, job.job_description, application_status.approval FROM job JOIN application_status ON job.job_id = application_status.job_id  WHERE application_status.roll_number = {roll_number};"
        cursor.execute(sql)
        applied_jobs = cursor.fetchall()

        # fetch column names
        cursor.execute("SHOW COLUMNS FROM job")
        job_head = cursor.fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
        
        # logic for application deletion
        if request.method == 'POST':
            if request.form['submit_button'] == 'cancel_application':
                application_id = request.form['application_id']

                # Perform cascading deletes using SQL queries
                cursor = db.connection.cursor()
                sql_delete_application = f"DELETE FROM application_status WHERE application_id = {application_id};"
                sql_delete_job_application = f"DELETE FROM job_application WHERE application_id = {application_id};"
                sql_delete_student_application = f"DELETE FROM student_application WHERE application_id = {application_id};"

                cursor.execute(sql_delete_application)
                cursor.execute(sql_delete_job_application)
                cursor.execute(sql_delete_student_application)
                db.connection.commit()
                cursor.close()

                return redirect(url_for('student_applied_jobs'))
        
        return render_template('student/applied_jobs.html', job_data = applied_jobs, job_head = column_names)

    else:
        return redirect(url_for('errorpage'))

# DONE
@app.route('/student/update_profile', methods=['GET', 'POST'])
def student_personal_info_change():
    if "email" in session:
        if request.method == 'POST':
            cpi = request.form.get('cpi')
            last_sem_spi = request.form.get('last_sem_spi')
            on_probation = request.form.get('on_probation')

            cursor = db.connection.cursor()
            cursor.execute(f"UPDATE student SET cpi = {cpi}, last_sem_spi = {last_sem_spi}, on_probation = {on_probation} WHERE email_id = {session['email']};")
            
            db.connection.commit()
            cursor.close()

            return redirect(url_for('student_personal_info'))

        return render_template('student/personal_info_change.html')

    else:
        return redirect(url_for('errorpage'))



if __name__ == "__main__":
    app.run(debug=True)
