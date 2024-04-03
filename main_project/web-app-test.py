from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'mySecretKey'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "oceoAdmin"
app.config["MYSQL_PASSWORD"] = "oceoAdmin"
app.config["MYSQL_DB"] = "oceo_management"

db = MySQL(app)
# ------------------------------------------------------------------------------------------------------

# Home Page - Select User Type
@app.route("/")
def index():
    return render_template("index.html")

# NEW USER REGISTRATION
@app.route("/login/new_user", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        new_roll_number = request.form["roll_number"]
        email = request.form["email"]
        userType = request.form.get('userType') 
        password = request.form["password"]
        on_probation = request.form.get('on_probation') == 'Yes'
        cursor = db.connection.cursor()
        
        if userType == "student":
            sql = f"SELECT count(*) FROM applied_student WHERE email_id='{email}'"
            cursor.execute(sql)
            isPresent = cursor.fetchone()[0]
            
            # remove integrity constraint on "on_probation" field
            on_probation_alter = "ALTER TABLE applied_student MODIFY on_probation BOOLEAN;"
            cursor.execute(on_probation_alter)
            db.connection.commit()

            # user already exists
            if isPresent==1:
                error_message = ("User already exists. Please choose a different username.")
                return render_template("newuser.html", error_message=error_message)
            
            # new user registration
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                sql = f"INSERT INTO applied_student (roll_number, first_name, middle_name, last_name, email_id, password, on_probation) VALUES ({new_roll_number},'{first_name}','{middle_name}','{last_name}','{email}','{hashed_password}',{on_probation});"
                cursor.execute(sql)
                db.connection.commit()
                cursor.close()
                return redirect(url_for("index"))

        # TODO non-student new user
        else:
            return redirect(url_for("errorpage"))
    
    return render_template("newuser.html")

# ------------------------------------------------------------------------------------------------------
# check the credentials of the user 
def authenticate(email, password):
    cursor = db.connection.cursor()
    sql = f"SELECT password FROM applied_student WHERE email_id='{email}'"
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    if bcrypt.check_password_hash(result[0], password):
        return True
    else:
        return False

@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form["username"]
        password = request.form["password"]

        # fetch roll number from database
        cursor = db.connection.cursor()
        sql = f"SELECT roll_number FROM applied_student WHERE email_id='{email}'"
        cursor.execute(sql)
        roll_number = cursor.fetchone()[0]
        cursor.close()

        if authenticate(email, password):
            # ACTIVATES THE SESSION (logged in)
            session["roll_number"] = roll_number
            return redirect(url_for("after_login_student"))
        else:
            return redirect(url_for("errorpage"))

    return render_template('student.html')

@app.route('/login/professor', methods=['GET', 'POST'])
def login_professor():
    return render_template('professor/professor.html')

@app.route("/errorpage")
def errorpage():
    error_message = "Bad Credentials!"
    return render_template("errorpage.html", error_message=error_message)


# -----------AUTHORISED ACCESS ONLY----------------------------------------------------------------

@app.route('/student', methods=['GET', 'POST']) # student homepage
def after_login_student():
    if "roll_number" in session:
        cursor = db.connection.cursor()
        # roll_number = session['roll_number']
        # studen_name = 
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'personal_info':
                    return redirect(url_for('student_personal_info'))
                case 'jobs_available':
                    return redirect(url_for('student_jobs_available'))
                case 'applied_jobs':
                    return redirect(url_for('student_applied_jobs')) 
                case 'logout':
                    session.pop("roll_number", None) # todo Test logout
                    return redirect(url_for('index'))
                case _:
                    return render_template('student/after_login.html')  
            
        return render_template('student/after_login.html') # student homepage
    
    else:
        return redirect(url_for('errorpage'))

def phone_num_exist(roll_number):
    cursor = db.connection.cursor()
    check_phone_query = f"SELECT count(*) FROM applied_student_phone WHERE roll_number = {roll_number};"
    cursor.execute(check_phone_query)
    phone_count = cursor.fetchone()[0]
    cursor.close()
    return phone_count != 0

@app.route('/student/personal_info', methods=['GET', 'POST'])
def student_personal_info():
    if "roll_number" in session:
        if request.method == 'POST': 
            # profile update
            if request.form['submit_button'] == 'Update_Profile': 
                return redirect(url_for('student_personal_info_change'))

        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT * FROM applied_student WHERE roll_number = '{roll_number}';")
        fetched_data = cursor.fetchall()

        # check if phone number exists
        if phone_num_exist(roll_number):
            # fetch existing phone numbers
            phone_query = f"SELECT phone_number FROM applied_student_phone WHERE roll_number = {roll_number};"
            cursor.execute(phone_query)
            fetched_phone = cursor.fetchall()
        else:
            fetched_phone = ("Not Added", "Not Added")

        cursor.close()
        
        return render_template('student/personal_info.html', student_data=fetched_data, student_phone = fetched_phone)
    
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/update_profile', methods=['GET', 'POST'])
def student_personal_info_change():
    if "roll_number" in session:
        if request.method == 'POST':
            roll_number = session['roll_number']
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name')
            last_name = request.form.get('last_name')
            cpi = request.form.get('cpi')
            last_sem_spi = request.form.get('last_sem_spi')
            on_probation = 1 if request.form.get('on_probation') == 'Yes' else 0
            phone_1 = request.form.get('contact_number')
            phone_2 = request.form.get('alternate_contact_number', '')
            # fetch uploaded image
            cursor = db.connection.cursor()
            
            cursor.execute(f"UPDATE applied_student SET first_name = '{first_name}', middle_name = '{middle_name}', last_name='{last_name}',cpi = {cpi}, last_sem_spi = {last_sem_spi}, on_probation = {on_probation} WHERE roll_number = {roll_number};")
            db.connection.commit()

            if 'image' in request.files:
                image = request.files['image']
                image_data = image.read()
                cursor.execute(f"UPDATE applied_student SET image = {image_data} WHERE roll_number = {roll_number};")
                db.connection.commit()
        
            # check if phone number exists
            if phone_num_exist(roll_number):
                # update existing phone numbers
                delete_query = f"DELETE FROM applied_student_phone WHERE roll_number={roll_number};"
                cursor.execute(delete_query)
                db.connection.commit()

            # add new phone numbers
            cursor.execute(f"INSERT INTO applied_student_phone (roll_number, phone_number) VALUES ({roll_number}, {phone_1});")
            db.connection.commit()
            if phone_2!="": 
                cursor.execute(f"INSERT INTO applied_student_phone (roll_number, phone_number) VALUES ({roll_number}, {phone_2});")
                db.connection.commit()


            db.connection.commit()
            cursor.close()

            return redirect(url_for('student_personal_info'))

        # fetch all data
        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT * FROM applied_student WHERE roll_number = '{roll_number}';")
        fetched_data = cursor.fetchall()

        # check if phone number exists
        if phone_num_exist(roll_number):
            # fetch existing phone numbers
            phone_query = f"SELECT phone_number FROM applied_student_phone WHERE roll_number = {roll_number};"
            cursor.execute(phone_query)
            fetched_phone = cursor.fetchall()
        else:
            fetched_phone = ("Not Added", "Not Added")

        return render_template('student/personal_info_change.html', student_data = fetched_data, student_phone = fetched_phone)

    else:
        return redirect(url_for('errorpage'))

@app.route('/student/jobs_available', methods=['GET', 'POST'])
def student_jobs_available():
    if "roll_number" in session:
        # if "Apply" button is pressed
        if request.method == 'POST': 
            if request.form['submit_button'] == 'Apply':
                return render_template('student/apply_job.html',job_id=request.form['job_id'])   
        
        # GET request handling:
        # fetch unapplied jobs
        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT job.* FROM job LEFT JOIN application_status ON job.job_id = application_status.job_id AND application_status.roll_number = {roll_number} WHERE job.is_position_open = 1 AND (application_status.application_id IS NULL);")
        job_data = cursor.fetchall()
        
        # fetch column names
        cursor.execute("SHOW COLUMNS FROM job")
        job_head = cursor.fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
         
        return render_template('student/jobs_available.html', job_data=job_data, job_head = column_names)
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/apply_job', methods=['GET', 'POST'])
def student_apply_job():
    if "roll_number" in session:
        roll_number = session['roll_number']
        if request.method == 'POST': # submits the application
            cursor = db.connection.cursor()
            # logic to generate new application_id # if no id exists, then generate random id, otherwise increment the max id by 1
            cursor.execute("SELECT count(*) FROM application_status")
            total_count = cursor.fetchone()[0]
            if total_count == 0:
                application_id = random.randint(12345678, 29999999)
            else:
                cursor.execute("SELECT MAX(application_id) FROM application_status")
                max_id = cursor.fetchone()[0]
                application_id = max_id + 1

            # fetch filled details
            cpi = request.form['cpi']
            last_sem_spi = request.form['last_sem_spi']
            job_id = request.form['job_id']
            so_motivation = request.form['statement_of_motivation']

            sql_update_cpi_spi = f"UPDATE applied_student SET cpi = {cpi}, last_sem_spi = {last_sem_spi} WHERE roll_number = {roll_number};"

            # add new application into 3 tables
            sql_app_id = f"INSERT INTO application_status (application_id, faculty_approved, oceo_coordinator_approved, SA_approved, dean_approved, statement_of_motivation, roll_number, job_id, approval) VALUES ({application_id}, 0, 0, 0, 0, '{so_motivation}', {roll_number}, {job_id}, 'pending');"

            sql_job_id = f"INSERT INTO job_application (job_id, application_id) VALUES ({job_id}, {application_id});"
            sql_student_id = f"INSERT INTO student_application (roll_number, application_id) VALUES ({roll_number}, {application_id});"
            # fill each table with new application info
            cursor.execute(sql_update_cpi_spi)
            db.connection.commit()
            cursor.execute(sql_app_id)
            db.connection.commit()
            cursor.execute(sql_job_id)
            db.connection.commit()
            cursor.execute(sql_student_id)
            db.connection.commit()
            cursor.close()

            return redirect(url_for('student_jobs_available'))
        
        # FOR RENDERING DROPDOWN MENU
        # fetch unapplied jobs id
        job_id = request.form['job_id']
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT job.* FROM job where job_id={job_id});")
        job = cursor.fetchall()


        # fetch job role names
        if job[1]=="ADH": 
            cursor.execute(f"SELECT course_id, course_name FROM adh WHERE job_id = {job[0]};")
            course_id, course_name = cursor.fetchone()
            job_role=(f"ADH: {course_id} - {course_name}")
        elif job[1]=="PAL": 
            cursor.execute(f"SELECT subjects_to_teach FROM subjects_under_pal WHERE job_id = {job[0]};")
            subjects_to_teach = cursor.fetchone()[0]
            job_role=(f"PAL: {subjects_to_teach}")
        else:
            cursor.execute(f"SELECT role_name FROM others WHERE job_id = {job[0]};")
            role_name = cursor.fetchone()[0]
            job_role=(f"{role_name}")                

        cursor.close()

        return render_template('student/apply_job.html', job_id = job_id,job_role=job_role) 
    
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/applied_jobs', methods=['GET', 'POST'])
def student_applied_jobs():
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = db.connection.cursor()

        # fetch applied jobs
        sql = f"SELECT application_status.application_id, job.job_id, job.job_type, job.job_description, application_status.approval FROM job JOIN application_status ON job.job_id = application_status.job_id WHERE application_status.roll_number = {roll_number};"
        cursor.execute(sql)
        applied_jobs = cursor.fetchall()

        # fetch column names
        # cursor.execute("SHOW COLUMNS FROM job")
        # job_head = cursor.fetchall()
        # column_names = tuple(row[0] for row in job_head)
        # cursor.close()

        #Mannualy fix the Column Heading
        column_names=('Application Id', 'Job Id', 'Job Type', 'Job Description', 'Approval Status')
        
        # logic for application deletion
        if request.method == 'POST':
            if request.form['submit_button'] == 'cancel_application':
                application_id = request.form['application_id']

                # Perform cascading deletes using SQL queries
                cursor = db.connection.cursor()
                sql_delete_application = f"DELETE FROM application_status WHERE application_id = {application_id};"
                sql_delete_job_application = f"DELETE FROM job_application WHERE application_id = {application_id};"
                sql_delete_student_application = f"DELETE FROM student_application WHERE application_id = {application_id};"

                cursor.execute(sql_delete_student_application)
                db.connection.commit()

                cursor.execute(sql_delete_job_application)
                db.connection.commit()

                cursor.execute(sql_delete_application)
                db.connection.commit()
                cursor.close()

                return redirect(url_for('student_applied_jobs'))
        
        return render_template('student/applied_jobs.html', job_data = applied_jobs, job_head = column_names)

    else:
        return redirect(url_for('errorpage'))


# ------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)




# Under testings: job application section
# Under review: using CREATE USER and GRANT querires (e.g. to protect tables, etc.)


# todo: image testing and rendering on frontend
# todo: `password_change` feature
# todo: bank_details frontend
# todo: time_card frontend
# todo: /my_jobs page


