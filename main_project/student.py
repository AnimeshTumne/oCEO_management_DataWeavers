from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
from flask import session, redirect, url_for, render_template_string
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

# importing all the functions from login_pages.py
from login_pages import login_student, login_professor, authenticate

# ----------- STUDENT STARTS ----------------------------------------------------------------

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
                update_query = f"INSERT INTO bank_details (roll_number, bank_name, account_number, IFSC_code) VALUES ({roll_number}, '{bank_name}', {account_number}, '{ifsc_code}');"
                cursor.execute(f"INSERT INTO bank_details (roll_number, bank_name, account_number, IFSC_code) VALUES ({roll_number}, '{bank_name}', {account_number}, '{ifsc_code}');")
            # --------------------

            db.connection.commit()
            cursor.close()
            # return redirect(url_for('student_bank_details'))
            return redirect(url_for('student_bank_details'))
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
                return redirect(url_for('student_applied_jobs'))
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
        current_year = datetime.datetime.now().year
        roll_number = session['roll_number']
        cursor = db.connection.cursor()
        if request.method == 'POST':
            if request.form['submit_button'] == "submit_timecard":
                month = request.form.get('month')
                year = request.form.get('year')
                hours_worked = request.form.get('hours_worked')
                work_description = request.form.get('work_description')
                sql = f"INSERT INTO time_card (roll_number, job_id, month, year, hours_worked, work_description, faculty_approval, payment_status) VALUES ({roll_number}, {job_id}, '{month}', {year}, {hours_worked}, '{work_description}','pending', 'pending');"
                cursor.execute(sql)
                db.connection.commit()
                cursor.close()  
                return redirect(url_for('student_timecard', job_id=job_id, current_year=current_year))
        return render_template('student/new_timecard.html', job_id=job_id, current_year=current_year)
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