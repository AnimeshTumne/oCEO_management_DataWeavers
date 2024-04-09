from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
from flask import session, redirect, url_for, render_template_string

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
                sql = f"INSERT INTO applied_student (roll_number, first_name, middle_name, last_name, email_id, password) VALUES ({new_roll_number},'{first_name}','{middle_name}','{last_name}','{email}','{hashed_password}');"
                cursor.execute(sql)
                db.connection.commit()
                cursor.close()
                return render_template_string(f"""
                    <script>
                        alert("User registered successfully! Query Executed: {sql}");
                        window.location.href = "{{{{ url_for('index') }}}}";
                    </script>
                """)

        elif userType == "professor":
            sql = f"SELECT count(*) FROM faculty WHERE email_id='{email}'"
            cursor.execute(sql)
            isPresent = cursor.fetchone()[0]

            if isPresent==1:
                error_message = ("User already exists. Please choose a different username.")
                return render_template("newuser.html", error_message=error_message)
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                sql = f"INSERT INTO faculty (faculty_id, first_name, middle_name, last_name, email_id, password, dept_name) VALUES ({new_roll_number},'{first_name}','{middle_name}','{last_name}','{email}','{hashed_password}', 'Not Added');"
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
            return render_template_string(f"""
                <script>
                    // Show popup
                    alert("Successfully logged in as a Student. Successfully Executed:{sql}'");
                    // Redirect to the desired page
                    window.location.href = "{{{{ url_for('after_login_student') }}}}";
                </script>
            """)
        else:
            return redirect(url_for("errorpage"))

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



@app.route("/errorpage")
def errorpage(error_message="Bad Credentials!"):
    # error_message = "Bad Credentials!"
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
                case 'my_jobs':
                    return redirect(url_for('student_my_jobs'))
                case 'logout':
                    return redirect(url_for('logout'))
                case _:
                    return render_template('student/after_login.html')  
            
        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT first_name FROM applied_student WHERE roll_number = {roll_number};")
        student_name = cursor.fetchone()[0]
        cursor.close()
        return render_template('student/after_login.html', student_name=student_name) # student homepage
    
    else:
        return redirect(url_for('errorpage', error_message="You are not authorised to view this page. Please login first."))

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
            if request.form['submit_button'] == 'Update Profile': 
                return redirect(url_for('student_personal_info_change'))
            elif request.form['submit_button'] == 'Change Password':
                return redirect(url_for('change_password'))
            elif request.form['submit_button'] == 'Bank Details':
                return redirect(url_for('student_bank_details'))

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

        print("########################################################")
        print("########################################################")
        print(fetched_phone)
        print("########################################################")
        print("########################################################")
        cursor.close()
        
        return render_template('student/personal_info.html', student_data=fetched_data, student_phone = fetched_phone)
    
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/personal_info/bank_details', methods=['GET', 'POST'])
def student_bank_details():
    if "roll_number" in session:
        
        if request.method == 'POST':
            if request.form['submit_button'] == 'Edit':
                return redirect(url_for('student_edit_bank_details'))

        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT bank_name, account_number, IFSC_code FROM bank_details WHERE roll_number = '{roll_number}';")
        fetched_data = cursor.fetchall()
        cursor.close()
        return render_template('student/bank_details.html', bank_data=fetched_data)
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/edit_bank_details', methods=['GET', 'POST'])
def student_edit_bank_details():
    if "roll_number" in session:
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT * FROM bank_details WHERE roll_number = {session['roll_number']};")
        bank_data = cursor.fetchall()
        if request.method == 'POST':
            roll_number = session['roll_number']

            bank_name = request.form.get('bank_name')
            account_number = request.form.get('account_number')
            ifsc_code = request.form.get('ifsc_code')

            # --------------------
            cursor = db.connection.cursor()
            cursor.execute(f"SELECT count(*) FROM bank_details WHERE roll_number = {roll_number};")
            is_existing_roll_number = cursor.fetchone()[0]

            if is_existing_roll_number:
                update_query = f"UPDATE bank_details SET bank_name = '{bank_name}', account_number = {account_number}, IFSC_code = '{ifsc_code}' WHERE roll_number = {roll_number};"
                cursor.execute(update_query)
            else:
                cursor.execute(f"INSERT INTO bank_details (roll_number, bank_name, account_number, IFSC_code) VALUES ({roll_number}, '{bank_name}', {account_number}, '{ifsc_code}');")
            # --------------------

            db.connection.commit()
            cursor.close()
            # return redirect(url_for('student_bank_details'))
            return render_template_string(f"""
                <script>
                    alert("Bank details updated successfully! Query Executed: {update_query}");
                    window.location.href = "{{{{ url_for('student_bank_details') }}}}";
                </script>
            """)
        return render_template('student/edit_bank_details.html', bank_data=bank_data)
    else:
        return redirect(url_for('errorpage'), error_message="You are not authorised to view this page. Please login first.")

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
            phone_2 = request.form.get('alternate_contact_number')
            print("########################################################")
            print("########################################################")
            print(phone_1, phone_2)
            print("########################################################")
            print("########################################################")
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
            if phone_2: 
                cursor.execute(f"INSERT INTO applied_student_phone (roll_number, phone_number) VALUES ({roll_number}, {phone_2});")
                db.connection.commit()


            db.connection.commit()
            cursor.close()

            return redirect(url_for('student_personal_info'))

        # fetch all data
        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT * FROM applied_student WHERE roll_number = {roll_number};")
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
        return render_template('student/personal_info_change.html', student_data = fetched_data, student_phone = fetched_phone)

    else:
        return redirect(url_for('errorpage'))

@app.route('/student/jobs_available', methods=['GET', 'POST'])
def student_jobs_available():
    if "roll_number" in session:
        # if "Apply" button is pressed
        if request.method == 'POST': 
            if request.form['submit_button'] == 'Apply':
                return redirect(url_for('student_apply_job',job_id=request.form['job_id']) )  
        
        # GET request handling:
        # fetch unapplied jobs
        cursor = db.connection.cursor()
        roll_number = session['roll_number']
        cursor.execute(f"SELECT job.* FROM job LEFT JOIN application_status ON job.job_id = application_status.job_id AND application_status.roll_number = {roll_number} WHERE job.is_available = 'yes' AND (application_status.application_id IS NULL);")
        job_data = cursor.fetchall()
        
        # fetch column names
        cursor.execute("SHOW COLUMNS FROM job")
        job_head = cursor.fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
         
        return render_template('student/jobs_available.html', job_data=job_data, job_head = column_names)
    else:
        return redirect(url_for('errorpage'))

@app.route('/student/apply_job/<job_id>', methods=['GET', 'POST'])
def student_apply_job(job_id):
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
            so_motivation = request.form['statement_of_motivation']

            sql_update_cpi_spi = f"UPDATE applied_student SET cpi = {cpi}, last_sem_spi = {last_sem_spi} WHERE roll_number = {roll_number};"

            # add new application into 3 tables
            sql_app_id = f"INSERT INTO application_status (application_id, faculty_approved, oceo_coordinator_approved, SA_approved, dean_approved, statement_of_motivation, roll_number, job_id, approval) VALUES ({application_id}, 0, 0, 0, 0, '{so_motivation}', {roll_number}, {job_id}, 'pending');"

            # sql_job_id = f"INSERT INTO job_application (job_id, application_id) VALUES ({job_id}, {application_id});"
            # sql_student_id = f"INSERT INTO student_application (roll_number, application_id) VALUES ({roll_number}, {application_id});"
            # fill each table with new application info
            cursor.execute(sql_update_cpi_spi)
            db.connection.commit()
            cursor.execute(sql_app_id)
            db.connection.commit()
            # cursor.execute(sql_job_id)
            # db.connection.commit()
            # cursor.execute(sql_student_id)
            # db.connection.commit()
            cursor.close()

            return redirect(url_for('student_jobs_available'))
        
        # FOR RENDERING DROPDOWN MENU
        # fetch unapplied jobs id
        
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT job.* FROM job where job_id={job_id};")
        job = cursor.fetchone()


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
        return render_template('student/apply_job.html', job_id=job_id, job_role=job_role)
    
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
                # sql_delete_job_application = f"DELETE FROM job_application WHERE application_id = {application_id};"
                # sql_delete_student_application = f"DELETE FROM student_application WHERE application_id = {application_id};"

                # cursor.execute(sql_delete_student_application)
                # db.connection.commit()

                # cursor.execute(sql_delete_job_application)
                # db.connection.commit()

                cursor.execute(sql_delete_application)
                db.connection.commit()
                cursor.close()

                return render_template_string(f"""
                    <script>
                        alert("Application deleted successfully! Query Executed: {sql_delete_application}");
                        window.location.href = "{{{{ url_for('student_applied_jobs') }}}}";
                    </script>
                """)
        
        return render_template('student/applied_jobs.html', job_data = applied_jobs, job_head = column_names)

    else:
        return redirect(url_for('errorpage'))

@app.route('/student/my_jobs', methods=['GET', 'POST'])
def student_my_jobs():
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = db.connection.cursor()

        if request.method == 'POST':
            if request.form['submit_button'] == 'view':
                job_id = request.form['job_id']
                return redirect(url_for('student_timecard', job_id=job_id))
            elif request.form['submit_button'] == 'mentees':
                return redirect(url_for('student_mentees'))
                
        # fetch my jobs
        sql = f"SELECT application_status.application_id, job.job_id, job.job_type, job.job_description, application_status.approval FROM job JOIN application_status ON job.job_id = application_status.job_id WHERE application_status.roll_number = {roll_number} AND application_status.approval = 'approved';"
        cursor.execute(sql)
        my_jobs = cursor.fetchall()

        # fetch column names
        # cursor.execute("SHOW COLUMNS FROM job")
        # job_head = cursor.fetchall()
        # column_names = tuple(row[0] for row in job_head)
        # cursor.close()

        #Mannualy fix the Column Heading
        column_names=('Application Id', 'Job Id', 'Job Type', 'Job Description', 'Approval Status')
        
        return render_template('student/my_jobs.html', job_data = my_jobs, job_head = column_names)

    else:
        return redirect(url_for('errorpage'))

@app.route('/student/mentees', methods=['GET', 'POST'])
def student_mentees():
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = db.connection.cursor()

        # fetch mentees
        sql = f"select mentee_roll_number, first_name, middle_name, last_name from mentees natural join mentor_mentee where mentor_mentee.roll_number = {roll_number};"
        cursor.execute(sql)
        mentees = cursor.fetchall()

        # fetch column names
        column_names = cursor.description
        # cursor.execute("SHOW COLUMNS FROM mentor_mentee")
        # mentee_head = cursor.fetchall()
        column_names = tuple(row[0] for row in column_names)
        cursor.close()

        return render_template('student/mentees.html', mentee_data = mentees, mentee_head = column_names)

    else:
        return redirect(url_for('errorpage'))

@app.route('/student/timecard/<job_id>', methods=['GET', 'POST'])
def student_timecard(job_id):
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = db.connection.cursor()
        if request.method == 'POST':
            if request.form['submit_button'] == 'submit_timecard':
                return redirect(url_for('submit_timecard',job_id=job_id))

        # fetch timecard data
        sql = f"SELECT * FROM time_card WHERE roll_number = {roll_number} AND job_id = {job_id};"
        cursor.execute(sql)
        timecard_data = cursor.fetchall()
        timecard_head = cursor.description
        column_names = tuple(row[0] for row in timecard_head)
        cursor.close()
        return render_template('student/timecard.html', timecard_data = timecard_data, timecard_head = column_names,job_id=job_id)

@app.route('/student/submit_timecard/<job_id>', methods=['GET', 'POST'])
def submit_timecard(job_id):
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = db.connection.cursor()
        if request.method == 'POST':
            if request.form['submit_button'] == "submit_timecard":
                month = request.form.get('month')
                year = request.form.get('year')
                hours_worked = request.form.get('hours_worked')
                work_description = request.form.get('work_description')
                sql = f"INSERT INTO time_card (roll_number, job_id, month, year, hours_worked, work_description,is_approved) VALUES ({roll_number}, {job_id}, '{month}', {year}, {hours_worked}, '{work_description}',0);"
                cursor.execute(sql)
                db.connection.commit()
                cursor.close()  
                return redirect(url_for('student_timecard', job_id=job_id))
        return render_template('student/new_timecard.html', job_id=job_id)
    else:
        return redirect(url_for('errorpage'))    

@app.route('/student/change_password', methods=['GET', 'POST'])
def change_password():
    if "roll_number" in session:
        if request.method == 'POST':
            roll_number = session['roll_number']
            cursor = db.connection.cursor()
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            cursor.execute(f"SELECT password FROM applied_student WHERE roll_number = {roll_number};")
            hashed_password = cursor.fetchone()[0]
            cursor.close()
            if bcrypt.check_password_hash(hashed_password, old_password):
                if new_password == confirm_password:
                    new_hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    cursor = db.connection.cursor()
                    cursor.execute(f"UPDATE applied_student SET password = '{new_hashed_password}' WHERE roll_number = {roll_number};")
                    db.connection.commit()
                    cursor.close()
                    return redirect(url_for('student_personal_info'))
                else:
                    return redirect(url_for('errorpage'))
            else:
                return redirect(url_for('errorpage'))
        return render_template('student/change_password.html')
    else:
        return redirect(url_for('errorpage'))
                
@app.route('/student/logout')
def logout():
    session.pop('roll_number', None)
    return redirect(url_for('index'))

# ------------- END OF STUDENT -------------------------------------------------------------------------

# ------------- START OF PROF --------------------------------------------------------------------------

@app.route('/professor', methods=['GET', 'POST']) # professor homepage
def after_login_professor():
    if "faculty_id" in session:
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'personal_info':
                    return redirect(url_for('professor_personal_info'))
                case 'jobs_created':
                    return redirect(url_for('professor_jobs_created'))
                case 'timecard_for_review':
                    return redirect(url_for('professor_timecard_for_review'))
                case 'logout':
                    return redirect(url_for('professor_logout'))
                case _:
                    return render_template('professor/after_login.html')
        cursor = db.connection.cursor()
        faculty_id = session['faculty_id']
        cursor.execute(f"SELECT first_name FROM faculty WHERE faculty_id = {faculty_id};")
        faculty_name = cursor.fetchall()[0][0]
        cursor.close()
        return render_template('professor/after_login.html', faculty_name=faculty_name)
    else:
        return render_template('errorpage.html')

@app.route('/professor/personal_info', methods=['GET', 'POST'])
def professor_personal_info():
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'Update_Profile':
                return redirect(url_for('professor_personal_info_change'))
            elif request.form['submit_button'] == 'Change_Password':
                return redirect(url_for('professor_change_password'))
            
        cursor = db.connection.cursor()
        faculty_id = session['faculty_id']
        cursor.execute(f"SELECT * FROM faculty WHERE faculty_id = {faculty_id};")
        fetched_data = cursor.fetchall()
        cursor.close()
        return render_template('professor/personal_info.html', professor_data=fetched_data)
    else:
        return redirect(url_for('errorpage'))
    
@app.route('/professor/update_profile', methods=['GET', 'POST'])
def professor_personal_info_change():
    if "faculty_id" in session:
        if request.method == 'POST':
            faculty_id = session['faculty_id']
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name')
            last_name = request.form.get('last_name')
            dept_name = request.form.get('department_name')
            voip_id = request.form.get('voip_id')
            cursor = db.connection.cursor()
            cursor.execute(f"UPDATE faculty SET first_name = '{first_name}', middle_name = '{middle_name}', last_name = '{last_name}', dept_name = '{dept_name}', voip_id = {voip_id} WHERE faculty_id = {faculty_id}")
            db.connection.commit()

            if 'image' in request.files:
                image = request.files['image']
                image_data = image.read()
                cursor.execute(f"UPDATE faculty SET image = {image_data} WHERE faculty_id = {faculty_id};")
                db.connection.commit()
            
            cursor.close()
            return redirect(url_for('professor_personal_info'))
        cursor = db.connection.cursor()
        faculty_id = session['faculty_id']
        cursor.execute(f"SELECT * FROM faculty WHERE faculty_id = {faculty_id};")
        fetched_data = cursor.fetchall()
        cursor.close()
        return render_template('professor/personal_info_change.html', professor_data=fetched_data)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/change_password', methods=['GET', 'POST'])
def professor_change_password():
    if "faculty_id" in session:
        if request.method == 'POST':
            faculty_id = session['faculty_id']
            cursor = db.connection.cursor()
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            cursor.execute(f"SELECT password FROM faculty WHERE faculty_id = {faculty_id};")
            hashed_password = cursor.fetchone()[0]
            cursor.close()
            if bcrypt.check_password_hash(hashed_password, old_password):
                if new_password == confirm_password:
                    new_hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    cursor = db.connection.cursor()
                    cursor.execute(f"UPDATE faculty SET password = '{new_hashed_password}' WHERE faculty_id = {faculty_id};")
                    db.connection.commit()
                    cursor.close()
                    return redirect(url_for('professor_personal_info'))
                else:
                    return redirect(url_for('errorpage'))
            else:
                return redirect(url_for('errorpage'))
        return render_template('professor/change_password.html')
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/jobs_created', methods=['GET', 'POST'])
def professor_jobs_created():
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'job_page':
                job_id = request.form['job_id']
                return redirect(url_for('professor_job_page', job_id=job_id))
            
        
        cursor = db.connection.cursor()
        faculty_id = session['faculty_id']
        cursor.execute(f"SELECT job_id,job_type,job_description,pay_per_hour,start_date,end_date,is_available FROM job WHERE job.faculty_id = {faculty_id};")
        job_data = cursor.fetchall()
        job_head =  cursor.description
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
        return render_template('professor/jobs_created.html', job_data=job_data, job_head=column_names)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/add_job', methods=['GET', 'POST'])
def professor_add_job():
    if "faculty_id" in session:
        if request.method == 'POST':
            faculty_id = session['faculty_id']
            job_type = request.form.get('job_type')
            job_description = request.form.get('job_description')
            min_qualifications = request.form.get('minimum_qualification')
            job_criteria = request.form.get('job_criteria')
            prerequisites = request.form.get('prerequisites')
            additional_info = request.form.get('additional_information')
            pay_per_hour = request.form.get('pay_per_hour')
            no_of_positions = request.form.get('number_of_positions')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            tenure = request.form.get('tenure')
            application_deadline = request.form.get('application_deadline')
            is_position_open = 1
            cursor = db.connection.cursor()
            cursor.execute("SELECT count(*) FROM job")
            total_count = cursor.fetchone()[0]
            if total_count == 0:
                job_id = random.randint(12345678, 29999999)
            else:
                cursor.execute("SELECT MAX(job_id) FROM job")
                max_id = cursor.fetchone()[0]
                job_id = max_id + 1

            cursor.execute(f"INSERT INTO job (job_id, job_type, job_description, min_qualifications, job_criteria, prerequisites, additional_info, pay_per_hour, no_of_positions, start_date, end_date, tenure, faculty_id, is_available, application_deadline) VALUES ({job_id}, '{job_type}', '{job_description}', '{min_qualifications}', '{job_criteria}', '{prerequisites}', '{additional_info}', {pay_per_hour}, {no_of_positions}, '{start_date}', '{end_date}', '{tenure}', {faculty_id}, {is_position_open}, '{application_deadline}');")
            db.connection.commit()
            if job_type == 'ADH':
                course_id = request.form.get('course_id')
                course_name = request.form.get('course_name')
                cursor.execute(f"INSERT INTO adh (job_id, course_id, course_name) VALUES ({job_id}, '{course_id}', '{course_name}');")
                db.connection.commit()
            elif job_type == 'PAL':
                subjects_to_teach = request.form.get('subjects_to_teach')
                cursor.execute(f"INSERT INTO subjects_under_pal (job_id, subjects_to_teach) VALUES ({job_id}, '{subjects_to_teach}');")
                db.connection.commit()
            else:
                role_name = request.form.get('role_name')
                cursor.execute(f"INSERT INTO other (job_id, role_name) VALUES ({job_id}, '{role_name}');")
                db.connection.commit()
            
            cursor.close()
            return redirect(url_for('professor_jobs_created'))
        return render_template('professor/add_job.html')
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/job_page/<job_id>', methods=['GET', 'POST'])
def professor_job_page(job_id):
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form.get('submit_button') == 'change_job_details':
                return redirect(url_for('professor_jobs_change_details', job_id=job_id))
            elif request.form.get('submit_button') == 'delete_job':
                return redirect(url_for('professor_delete_job', job_id=job_id))
            elif request.form.get('submit_button') == 'view_applications':
                return redirect(url_for('professor_view_applications', job_id=job_id))
            elif request.form.get('submit_button') == 'approved_applications':
                return redirect(url_for('professor_approved_applications', job_id=job_id))
            # elif idhar sochha tha kuch yaad nahi aa ra baadme dekh lena
            elif request.form.get('submit_button') == "assign_mentees":
                roll_number = request.form.get('roll_number')
                return redirect(url_for('professor_assign_mentees', job_id=job_id, roll_number=roll_number))
            elif request.form.get('submit_button') == "stop_accepting_applications":
                return redirect(url_for('professor_stop_accepting_applications', job_id=job_id))
                        
        cursor = db.connection.cursor()
        query_get_students_under_job = f"SELECT roll_number,first_name,middle_name,last_name,email_id FROM applied_student WHERE roll_number IN (SELECT roll_number FROM application_status WHERE job_id = {job_id} and approval='approved');"
        cursor.execute(query_get_students_under_job)
        student_under_job_data = cursor.fetchall()
        # cursor.execute("SHOW COLUMNS FROM job")
        # job_head = cursor.fetchall()
        student_under_job_head = cursor.description
        student_under_job_head = tuple(row[0] for row in student_under_job_head)
        query_job_type = f"SELECT * FROM job WHERE job_id = {job_id};"
        cursor.execute(query_job_type)
        job = cursor.fetchall()
        cursor.close()

        return render_template('professor/job_page.html', student_under_job_head=student_under_job_head, student_under_job_data=student_under_job_data,job_id=job_id,job=job)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/assign_mentees/<job_id>&<roll_number>', methods=['GET', 'POST'])
def professor_assign_mentees(job_id, roll_number):
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'assign_mentees':
                
                # roll_number = request.form['roll_number']
                mentee_roll_number = request.form['mentee_roll_number']
                first_name = request.form['first_name']
                middle_name = request.form['middle_name']
                last_name = request.form['last_name']
                
                cursor = db.connection.cursor()
                cursor.execute(f"INSERT INTO mentees (mentee_roll_number, first_name, middle_name, last_name) values ({mentee_roll_number}, '{first_name}', '{middle_name}', '{last_name}');")
                db.connection.commit()
                cursor.execute(f"INSERT INTO mentor_mentee (mentee_roll_number, roll_number, job_id) VALUES ({mentee_roll_number}, {roll_number}, {job_id});")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_job_page', job_id=job_id, roll_number=roll_number))
                
            # elif request.form['submit_button'] == 'import':
            #     file = request.files['file']
            #     if file:
            #         # Read the file data using pandas
            #         if file.filename.endswith('.csv'):
            #             df = pd.read_csv(file)
            #         elif file.filename.endswith('.xlsx'):
            #             df = pd.read_excel(file)
            #         else:
            #             return "Invalid file format"

            #         # Iterate over each row and add it to the database
            #         for index, row in df.iterrows():
            #             # Access the data from each column using row['column_name']
            #             # Add the data to the database using appropriate SQL queries
            #             mentee_roll_number = row['roll_number']
            #             first_name = row['first_name']
            #             middle_name = row['middle_name']
            #             last_name = row['last_name']

            #             cursor = db.connection.cursor()
            #             cursor.execute(f"insert into mentees (mentee_roll_number, first_name, middle_name, last_name) values ({mentee_roll_number}, '{first_name}', '{middle_name}', '{last_name}');")
            #             db.connection.commit()
            #             cursor.execute(f"INSERT INTO mentor_mentee (mentee_roll_number, roll_number, job_id) VALUES ({mentee_roll_number}, {roll_number}, {job_id});")
            #             db.connection.commit()
            #             cursor.close()

            #         return redirect(url_for('professor_job_page', job_id=job_id))
            
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT roll_number, first_name, middle_name, last_name FROM applied_student WHERE roll_number IN (SELECT roll_number FROM application_status WHERE job_id = {job_id} AND approval = 'approved');")
        mentee_data = cursor.fetchall()
        cursor.close()
        return render_template('professor/assign_mentees.html', mentee_data=mentee_data, job_id=job_id, roll_number=roll_number)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/change_job_details/<job_id>', methods=['GET', 'POST'])
def professor_jobs_change_details(job_id):
    if "faculty_id" in session:
        if request.method == 'POST':
            faculty_id = session['faculty_id']
            job_type = request.form.get('job_type')
            job_description = request.form.get('job_description')
            min_qualifications = request.form.get('minimum_qualification')
            job_criteria = request.form.get('job_criteria')
            prerequisites = request.form.get('prerequisites')
            additional_info = request.form.get('additional_information')
            pay_per_hour = request.form.get('pay_per_hour')
            no_of_positions = request.form.get('number_of_positions')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            tenure = request.form.get('tenure')
            application_deadline = request.form.get('application_deadline')
            cursor = db.connection.cursor()
            if job_type == 'ADH':
                course_id = request.form.get('course_id')
                course_name = request.form.get('course_name')
                cursor.execute(f"UPDATE adh SET course_id = '{course_id}', course_name = '{course_name}' WHERE job_id = {job_id};")
            elif job_type == 'PAL':
                subjects_to_teach = request.form.get('subjects_to_teach')
                cursor.execute(f"UPDATE subjects_under_pal SET subjects_to_teach = '{subjects_to_teach}' WHERE job_id = {job_id};")
            else:
                role_name = request.form.get('role_name')
                cursor.execute(f"UPDATE other SET role_name = '{role_name}' WHERE job_id = {job_id};")
            cursor.execute(f"UPDATE job SET job_type = '{job_type}', job_description = '{job_description}', min_qualifications = '{min_qualifications}', job_criteria = '{job_criteria}', prerequisites = '{prerequisites}', additional_info = '{additional_info}', pay_per_hour = {pay_per_hour}, no_of_positions = {no_of_positions}, start_date = '{start_date}', end_date = '{end_date}', tenure = '{tenure}', faculty_id = {faculty_id}, application_deadline = '{application_deadline}' WHERE job_id = {job_id};")
            db.connection.commit()
            cursor.close()
            return redirect(url_for('professor_jobs_created'))
        
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT job.* FROM job WHERE job.job_id = {job_id};")
        job_data = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM job")
        job_head = cursor.fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
        return render_template('professor/change_job_details.html', job_data=job_data, job_head=column_names)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/delete_job/<job_id>', methods=['GET', 'POST'])
def professor_delete_job(job_id):
    if "faculty_id" in session:
        cursor = db.connection.cursor()
        
        cursor.execute(f"select job_type from job where job_id = {job_id};")
        job_type = cursor.fetchone()[0]
        if job_type == "ADH":
            cursor.execute(f"DELETE FROM adh WHERE job_id = {job_id};")
        elif job_type == "PAL":
            cursor.execute(f"DELETE FROM subjects_under_pal WHERE job_id = {job_id};")
        else:
            cursor.execute(f"DELETE FROM other WHERE job_id = {job_id};")

        cursor.execute(f"DELETE FROM application_status WHERE job_id = {job_id};")
        cursor.execute(f"DELETE FROM time_card WHERE job_id = {job_id};")
        cursor.execute(f"DELETE FROM job WHERE job_id = {job_id};")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('professor_jobs_created'))
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/view_applications/<job_id>', methods=['GET', 'POST'])
def professor_view_applications(job_id):
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;")
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;")
        application_data = cursor.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        application_head = cursor.description
        column_names = tuple(row[0] for row in application_head)
        cursor.close()
        return render_template('professor/view_applications.html', application_data=application_data, application_head=column_names, job_id=job_id)
    else:
        return redirect(url_for('errorpage'))

def other_view_applications(job_id):
    if "other_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;")
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_view_applications', job_id=job_id))
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;")
        application_data = cursor.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        application_head = cursor.description
        column_names = tuple(row[0] for row in application_head)
        cursor.close()
        return render_template('professor/view_applications.html', application_data=application_data, application_head=column_names, job_id=job_id)
    else:
        return redirect(url_for('errorpage'))

# change below function
@app.route('/professor/approved_applications/<job_id>', methods=['GET', 'POST'])
def professor_approved_applications(job_id):  # cHanged this.
    if "faculty_id" in session:
        # if request.method == 'POST':
            # if request.form['submit_button'] == 'approve':
            #     application_id = request.form['application_id']
            #     cursor = db.connection.cursor()
            #     cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")

            #     # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
            #     cursor.execute(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};")
            #     db.connection.commit()
            #     cursor.close()
            #     return redirect(url_for('professor_view_applications', job_id=job_id))
            
        #     if request.form['submit_button'] == 'reject':
        #         application_id = request.form['application_id']
        #         cursor = db.connection.cursor()
        #         cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
        #         cursor.execute(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};")
        #         db.connection.commit()
        #         cursor.close()
        #         return redirect(url_for('professor_view_applications', job_id=job_id))
        # cursor = db.connection.cursor()
        # cursor.execute(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;")
        
        if request.method == 'POST':
            if request.form['submit_button'] == 'remove':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET approval = 'rejected' WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_approved_applications', job_id=job_id))
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 1;")
        application_data = cursor.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        application_head = cursor.description
        column_names = tuple(row[0] for row in application_head)
        cursor.close()
        return render_template('professor/approved_applications.html', application_data=application_data, application_head=column_names, job_id=job_id)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/timecard_for_review', methods=['GET', 'POST'])
def professor_timecard_for_review():
    if "faculty_id" in session:

        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                # timecard_id = request.form['timecard_id']
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor = db.connection.cursor()
                cursor.execute(f"UPDATE time_card SET is_approved = 1 WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_timecard_for_review'))
            elif request.form['submit_button'] == 'reject':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor = db.connection.cursor()
                cursor.execute(f"UPDATE time_card SET is_approved = 0 WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_timecard_for_review'))
        cursor = db.connection.cursor()
        faculty_id = session['faculty_id']
        cursor.execute(f"SELECT time_card.*, applied_student.first_name, applied_student.middle_name, applied_student.last_name FROM time_card JOIN applied_student ON time_card.roll_number = applied_student.roll_number WHERE time_card.is_approved = 0 AND time_card.job_id IN (SELECT job_id FROM job WHERE faculty_id = {faculty_id});")
        timecard_data = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM time_card")
        timecard_head = cursor.fetchall()
        column_names = tuple(row[0] for row in timecard_head)
        cursor.close()
        return render_template('professor/timecard_for_review.html', timecard_data=timecard_data, timecard_head=column_names)
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/stop_accepting_applications/<job_id>', methods=['GET', 'POST'])
def professor_stop_accepting_applications(job_id):
    if "faculty_id" in session:
        cursor = db.connection.cursor()
        cursor.execute(f"UPDATE job SET is_available = 'no' WHERE job_id = {job_id};")
        db.connection.commit()
        cursor.close()
        return redirect(url_for('professor_jobs_created'))
    else:
        return redirect(url_for('errorpage'))

@app.route('/professor/logout')
def professor_logout():
    session.pop('faculty_id', None)
    return redirect(url_for('index'))
# ------------------------------------------------------------------------------------------------------
#----------------------Others-----------------------------------------------------------------

@app.route('/login/others',  methods=['GET', 'POST'])
def others_login(): 
    if request.method == 'POST':
        email = request.form["email"] 
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
                    return redirect(url_for("after_login_other", type = 'admin'))
                else:
                    return redirect(url_for("errorpage"))
            elif userType == 'Dean':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'dean';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("after_login_other", type = 'dean'))
                else:
                    return redirect(url_for("errorpage"))
                
            elif userType == 'SA JS':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'sa_js';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("after_login_other", type = 'sa_js'))
                else:
                    return redirect(url_for("errorpage"))
                
            elif userType == 'oCEO Coordinator':
                cursor = db.connection.cursor()
                sql = "SELECT email FROM other WHERE user_type = 'oceo_coordinator';"
                cursor.execute(sql)
                admin_email =  cursor.fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("after_login_other", type = 'oceo_coordinator'))
                else:
                    return redirect(url_for("errorpage"))
                
            
        else:
            return redirect(url_for("errorpage"))
    return render_template('others.html')

@app.route('/<type>/after_login_other', methods=['GET', 'POST'])
def after_login_other(type):
    if "email" in session:
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'applications_to_review':
                    return redirect(url_for('review_application', type = type))
                case 'approved_jobs':
                    return redirect(url_for('jobs_approved', type =type))
                case 'logout':
                    return redirect(url_for('professor_logout'))
                case _:
                    return render_template('others/admin/admin.html', type = type)
        return render_template( 'others/admin/admin.html', type = type ) 


# @app.route('/admin/admin.html', methods=['GET', 'POST'])
# def after_login_admin():
#     if "email" in session:
#         if request.method == 'POST':
#             testvar = request.form['submit_button']
#             match testvar:
#                 case 'applications_to_review':
#                     return redirect(url_for('review_application', type = 'admin'))
#                 case 'approved_jobs':
#                     return redirect(url_for('jobs_approved', type ='admin'))
#                 case 'logout':
#                     return redirect(url_for('professor_logout'))
#                 case _:
#                     return render_template('others/admin/admin.html')
#     return render_template( 'others/admin/admin.html' ) 

# @app.route('/dean/admin.html', methods=['GET', 'POST'])
# def after_login_dean():
#     if "email" in session:
#         if request.method == 'POST':
#             testvar = request.form['submit_button']
#             match testvar:
#                 case 'applications_to_review':
#                     return redirect(url_for('review_application', type = 'dean'))
#                 case 'approved_jobs':
#                     return redirect(url_for('jobs_approved', type ='dean'))
#                 case 'logout':
#                     return redirect(url_for('professor_logout'))
#                 case _:
#                     return render_template('others/admin/admin.html')
#     return render_template( 'others/admin/admin.html' ) 

# @app.route('/oceo_coordinator', methods=['GET', 'POST'])
# def after_login_oceo_coordinator():
#     if "email" in session:
#         if request.method == 'POST':
#             testvar = request.form['submit_button']
#             match testvar:
#                 case 'applications_to_review':
#                     return redirect(url_for('review_application', type = 'oceo_coordinator'))
#                 case 'approved_jobs':
#                     return redirect(url_for('jobs_approved'), type = 'oceo_coordinator')
#                 case 'logout':
#                     return redirect(url_for('professor_logout'))
#                 case _:
#                     return render_template('others/oceo_coordinator/admin.html')
#     return render_template( 'others/oceo_coordinator/admin.html' )

# @app.route('/oceo_coordinator', methods=['GET', 'POST'])
# def after_login_sa_js():
    if "email" in session:
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'applications_to_review':
                    return redirect(url_for('review_application', type = 'sa_js'))
                case 'approved_jobs':
                    return redirect(url_for('jobs_approved', type = 'sa_js'))
                case 'logout':
                    return redirect(url_for('professor_logout'))
                case _:
                    return render_template('others/admin/admin.html')
    return render_template( 'others/admin/admin.html' )


@app.route('/<type>/jobs_approved', methods=['GET','POST'] )
def jobs_approved(type):
    if "email" in session: 

        # if request.method == 'POST':
        cursor = db.connection.cursor()
        if type =='admin':
            query = 'SELECT * FROM application_status WHERE faculty_approved = 1;'
        elif type =='dean':
            query = 'SELECT * FROM application_status WHERE dean_approved = 1;'
        elif type =='sa_js':
            query = 'SELECT * FROM application_status WHERE SA_approved = 1;'
        elif type =='oceo_coordinator':
            query = 'SELECT * FROM application_status WHERE oceo_coordinator_approved = 1;'

        # query  = f'SELECT * FROM application_status WHERE {type}_approved = 1;' 
        cursor.execute(query)
        application_data = cursor.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        application_head = cursor.description
        column_names = tuple(row[0] for row in application_head)
        cursor.close()
        return render_template('others/admin/jobs_approved.html', application_data=application_data, application_head=column_names,type = type)
    else:
        return redirect(url_for('errorpage'))
    
@app.route('/<type>/review_application', methods=['GET', 'POST'])
def review_application(type):
    if "email" in session:
        if type =='admin':
            perm = 'faculty_approved'
        elif type =='dean':
            perm = 'dean_approved'
        elif type =='sa_js':
            perm  = 'SA_approved'
        elif type =='oceo_coordinator':
            perm = 'oceo_coordinator_approved'
        if request.method == 'POST':
            if request.form['submit_button'] == 'Approve':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET {perm} = 1 WHERE application_id = {application_id};")
                if perm == 'dean_approved':
                    cursor.execute(f"UPDATE application_status SET approval = 'approved' WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('review_application',type=type))
            elif request.form['submit_button'] == 'Reject':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET {perm}= 0 WHERE application_id = {application_id};")
                cursor.execute(f"UPDATE application_status SET approval = 'rejected' WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('review_application',type=type))
            
        cursor = db.connection.cursor()
        if perm == 'faculty_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0;'
        elif perm == 'oceo_coordinator_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0 and faculty_approved = 1;'
        elif perm == 'SA_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0 and faculty_approved = 1 and oceo_coordinator_approved = 1;'
        elif perm == 'dean_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0 and faculty_approved = 1 and oceo_coordinator_approved = 1 and SA_approved = 1;'
        # query = f'SELECT * FROM application_status WHERE {perm} = 0;'
        cursor.execute(query)
        application_data = cursor.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        application_head = cursor.description
        column_names = tuple(row[0] for row in application_head)
        cursor.close()
        return render_template('others/admin/review_application.html', application_data=application_data, application_head=column_names, type = type)
    else:
        return redirect(url_for('errorpage'))
    
@app.route('/<type>/logout')
def admin_logout(type):
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
