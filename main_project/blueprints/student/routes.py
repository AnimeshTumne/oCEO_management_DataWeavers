
from flask import Flask, render_template, request, redirect, url_for, session, Blueprint,current_app,g
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
from flask import session, redirect, url_for, render_template_string
from main_project import bcrypt
from sqlalchemy import create_engine, text
import datetime
import base64

from PIL import Image
from io import BytesIO

student_bp = Blueprint('student_bp', __name__,template_folder='templates',static_url_path='/static',static_folder='static')

@student_bp.before_request
def login_required():
    if 'email' not in session:
        # Redirect to the Google OAuth flow if the user is not authenticated
        return redirect(url_for('auth_bp.google',user_type='student'))



def get_db_connection():
    engine = create_engine('mysql://oceoAdmin:oceoAdmin@localhost/oceo_management')
    print("Engine created")
    return engine.connect()

def check_authorization(roll_number,job_id):
    cursor = get_db_connection()
    sql = f"SELECT * FROM application_status WHERE roll_number = {roll_number} AND job_id = {job_id};"
    result = cursor.execute(text(sql))
    cursor.close()
    if result.fetchone() is not None:
        return True
    else:
        return False
    



# ---------------------------------------------- STUDENT --------------------------------------------------------
@student_bp.route('', methods=['GET', 'POST']) # student homepage
def after_login_student():
    # db=get_db()
    if "roll_number" in session:

        # roll_number = session['roll_number']
        # studen_name = 
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'personal_info':
                    return redirect(url_for('student_bp.student_personal_info'))
                case 'jobs_available':
                    return redirect(url_for('student_bp.student_jobs_available'))
                case 'applied_jobs':
                    return redirect(url_for('student_bp.student_applied_jobs')) 
                case 'my_jobs':
                    return redirect(url_for('student_bp.student_my_jobs'))
                case 'logout':
                    return redirect(url_for('student_bp.logout'))
                case _:
                    return render_template('student/after_login.html')  
            
        cursor = get_db_connection()
        roll_number = session['roll_number']
        
        
      
        student_name = cursor.execute(text(f"SELECT first_name FROM applied_student WHERE roll_number = {roll_number};")).fetchone()[0]
        cursor.close()
        return render_template('student/after_login.html', student_name=student_name) # student homepage
    
    else:
        return redirect(url_for('auth_bp.errorpage', error_message="You are not authorised to view this page. Please login first."))

def phone_num_exist(roll_number):
    # db=get_db()
    cursor = get_db_connection()
    check_phone_query = f"SELECT count(*) FROM applied_student_phone WHERE roll_number = {roll_number};"
    
    phone_count = cursor.execute(text(check_phone_query)).fetchone()[0]
    cursor.close()
    return phone_count != 0

@student_bp.route('/personal_info', methods=['GET', 'POST'])
def student_personal_info():
    # db=get_db()
    if "roll_number" in session:
        if request.method == 'POST': 
            # profile update
            if request.form['submit_button'] == 'Update Profile': 
                return redirect(url_for('student_bp.student_personal_info_change'))
            elif request.form['submit_button'] == 'Change Password':
                return redirect(url_for('student_bp.change_password'))
            elif request.form['submit_button'] == 'Bank Details':
                return redirect(url_for('student_bp.student_bank_details'))

        cursor = get_db_connection()
        roll_number = session['roll_number']
        fetched_data =  cursor.execute(text(f"SELECT * FROM applied_student WHERE roll_number = '{roll_number}';")).fetchall()

        image_result=cursor.execute(text(f"SELECT person_img FROM applied_student WHERE roll_number = {roll_number};"))
        image_data = image_result.fetchone()[0]
        #convert the blob image data to base64
        image_data = base64.b64encode(image_data).decode('utf-8')

        # check if phone number exists
        if phone_num_exist(roll_number):
            # fetch existing phone numbers
            phone_query = f"SELECT phone_number,isMain FROM applied_student_phone WHERE roll_number = {roll_number};"
           
            
            fetched_phone = cursor.execute(text(phone_query)).fetchall()

        else:
            fetched_phone = ("Not Added", "Not Added")


        cursor.close()
        
        return render_template('student/personal_info.html', student_data=fetched_data, student_phone = fetched_phone, image_data=image_data)
    
    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/personal_info/bank_details', methods=['GET', 'POST'])
def student_bank_details():
    # db=get_db()
    if "roll_number" in session:
        
        if request.method == 'POST':
            if request.form['submit_button'] == 'Edit':
                return redirect(url_for('student_bp.student_edit_bank_details'))

        cursor = get_db_connection()
        roll_number = session['roll_number']
        
        fetched_data = cursor.execute(text(f"SELECT bank_name, account_number, IFSC_code FROM bank_details WHERE roll_number = '{roll_number}';")).fetchall()
        cursor.close()  
        return render_template('student/bank_details.html', bank_data=fetched_data)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/edit_bank_details', methods=['GET', 'POST'])
def student_edit_bank_details():
    # db=get_db()
    if "roll_number" in session:
        cursor = get_db_connection()
        
        bank_data = cursor.execute(text(f"SELECT * FROM bank_details WHERE roll_number = {session['roll_number']};")).fetchall()
        cursor.close()
        if request.method == 'POST':
            roll_number = session['roll_number']

            bank_name = request.form.get('bank_name')
            account_number = request.form.get('account_number')
            ifsc_code = request.form.get('ifsc_code')

            # --------------------
            cursor = get_db_connection()
          
            is_existing_roll_number =   cursor.execute(text(f"SELECT count(*) FROM bank_details WHERE roll_number = {roll_number};")).fetchone()[0]

            if is_existing_roll_number:
                update_query = f"UPDATE bank_details SET bank_name = '{bank_name}', account_number = {account_number}, IFSC_code = '{ifsc_code}' WHERE roll_number = {roll_number};"
                cursor.execute(text(update_query))
                cursor.commit()
            else:
                update_query = f"INSERT INTO bank_details (roll_number, bank_name, account_number, IFSC_code) VALUES ({roll_number}, '{bank_name}', {account_number}, '{ifsc_code}');"
                cursor.execute(text(f"INSERT INTO bank_details (roll_number, bank_name, account_number, IFSC_code) VALUES ({roll_number}, '{bank_name}', {account_number}, '{ifsc_code}');"))
                cursor.commit()
            # --------------------

           
            cursor.close()
            # return redirect(url_for('student_bank_details'))
            return redirect(url_for('student_bp.student_bank_details'))
            return render_template_string(f"""
                <script>
                    alert("Bank details updated successfully! Query Executed: {update_query}");
                    window.location.href = "{{{{ url_for('student_bank_details') }}}}";
                </script>
            """)
        return render_template('student/edit_bank_details.html', bank_data=bank_data)
    else:
        return redirect(url_for('auth_bp.errorpage'), error_message="You are not authorised to view this page. Please login first.")

# ---------------------------------------------------------------
def resize_image(image_data, max_size=(200, 200)):
    image = Image.open(BytesIO(image_data))
    image.thumbnail(max_size)  # Resize to max_size while maintaining aspect ratio
    
    output = BytesIO()
    if image.format == 'PNG':
        image = image.convert('RGB')  # Convert PNG to JPEG (no transparency support)
        image.save(output, format='JPEG', quality=100)  # Save as JPEG with quality compression (if required)
    else:
        image.save(output, format=image.format)  # Save other formats without conversion
    
    return output.getvalue()

# ---------------------------------------------------------------


@student_bp.route('/update_profile', methods=['GET', 'POST'])
def student_personal_info_change():
    # db=get_db()
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
            cursor = get_db_connection()
            
            try:
                with cursor.begin():

                    cursor.execute(text(f"UPDATE applied_student SET first_name = '{first_name}', middle_name = '{middle_name}', last_name='{last_name}',cpi = {cpi}, last_sem_spi = {last_sem_spi}, on_probation = {on_probation} WHERE roll_number = {roll_number};"))
                    # cursor.commit()
                    if 'image' in request.files:
                        image = request.files['image']
                        image_data = image.read()
                        image_data = resize_image(image_data)

                        #convert image to blob
                        # image_data_blob = base64.b64encode(image_data)
                        imgQuery = text(f"UPDATE applied_student SET person_img = :imageData WHERE roll_number = :rollNo;")
                        cursor.execute(imgQuery, {"imageData": image_data, "rollNo": roll_number})
                        # cursor.commit()

                    if phone_num_exist(roll_number):
                        # update existing phone numbers
                        delete_query = f"DELETE FROM applied_student_phone WHERE roll_number={roll_number};"
                        cursor.execute(text(delete_query))
                        # cursor.commit()

                    # add new phone numbers
                    cursor.execute(text(f"INSERT INTO applied_student_phone (roll_number, phone_number,isMain) VALUES ({roll_number}, {phone_1},1);"))
                    # cursor.commit()
                    if phone_2: 
                        cursor.execute(text(f"INSERT INTO applied_student_phone (roll_number, phone_number,isMain) VALUES ({roll_number}, {phone_2},0);"))
                        # cursor.commit()
                    cursor.commit()
            except Exception as e:
                cursor.rollback()
                print(f"\n==============\n==============\nError occurred: \n{e}\n==============\n==============\n")
            finally:
                cursor.close()

            return redirect(url_for('student_bp.student_personal_info'))

        # fetch all data
        cursor = get_db_connection()
        roll_number = session['roll_number']
        
        fetched_data = cursor.execute(text(f"SELECT * FROM applied_student WHERE roll_number = {roll_number};")).fetchall()

        # check if phone number exists
        if phone_num_exist(roll_number):
            # fetch existing phone numbers
            phone_query = f"SELECT phone_number FROM applied_student_phone WHERE roll_number = {roll_number};"
           
            fetched_phone =  cursor.execute(text(phone_query)).fetchall()
        else:
            fetched_phone = ("Not Added", "Not Added")

        cursor.close()
        return render_template('student/personal_info_change.html', student_data = fetched_data, student_phone = fetched_phone)

    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/upload_image', methods=['GET', 'POST'])
def student_upload_image():
    # db=get_db()
    print("entered")
    if "roll_number" in session:
        if request.method == 'POST':
            roll_number = session['roll_number']
            cursor = get_db_connection()
            image = request.files['image']
            image_data = image.read()
            #convert image to blob
            
            image_data_blob = base64.b64encode(image_data)
            cursor.execute(text(f"UPDATE applied_student SET person_img = {image_data_blob} WHERE roll_number = {roll_number};"))
            cursor.commit()
            cursor.close()
            return redirect(url_for('student_bp.student_personal_info_change'))
        return render_template('student/personal_info_change.html')
    else:
        return redirect(url_for('auth_bp.errorpage'))    

@student_bp.route('/jobs_available', methods=['GET', 'POST'])
def student_jobs_available():
    # db=get_db()
    if "roll_number" in session:
        # if "Apply" button is pressed
        if request.method == 'POST': 
            if request.form['submit_button'] == 'Apply':
                return redirect(url_for('student_bp.student_apply_job',job_id=request.form['job_id']) )  
        
        # GET request handling:
        # fetch unapplied jobs
        cursor = get_db_connection()
        roll_number = session['roll_number']
        
        job_data = cursor.execute(text(f"SELECT job.* FROM job LEFT JOIN application_status ON job.job_id = application_status.job_id AND application_status.roll_number = {roll_number} WHERE job.is_available = 'yes' AND (application_status.application_id IS NULL);")).fetchall()
        
        # fetch column names
        
        job_head = cursor.execute(text("SHOW COLUMNS FROM job")).fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
         
        return render_template('student/jobs_available.html', job_data=job_data, job_head = column_names)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/apply_job/<job_id>', methods=['GET', 'POST'])
def student_apply_job(job_id):
    # db=get_db()
    if "roll_number" in session:
        roll_number = session['roll_number']
        if request.method == 'POST': # submits the application
            cursor = get_db_connection()
            # logic to generate new application_id # if no id exists, then generate random id, otherwise increment the max id by 1
            
            total_count = cursor.execute(text("SELECT count(*) FROM application_status")).fetchone()[0]
            if total_count == 0:
                application_id = random.randint(12345678, 29999999)
            else:
                
                max_id = cursor.execute(text("SELECT MAX(application_id) FROM application_status")).fetchone()[0]
                application_id = max_id + 1

            # fetch filled details
            cpi = request.form['cpi']
            last_sem_spi = request.form['last_sem_spi']
            so_motivation = request.form['statement_of_motivation']

            sql_update_cpi_spi = f"UPDATE applied_student SET cpi = {cpi}, last_sem_spi = {last_sem_spi} WHERE roll_number = {roll_number};"

            # add new application into 3 tables
            sql_app_id = f"INSERT INTO application_status (application_id, faculty_approved, oceo_coordinator_approved, SA_approved, dean_approved, statement_of_motivation, roll_number, job_id, approval) VALUES ({application_id}, 'pending', 'pending', 'pending', 'pending', '{so_motivation}', {roll_number}, {job_id}, 'pending');"

            # sql_job_id = f"INSERT INTO job_application (job_id, application_id) VALUES ({job_id}, {application_id});"
            # sql_student_id = f"INSERT INTO student_application (roll_number, application_id) VALUES ({roll_number}, {application_id});"
            # fill each table with new application info
            cursor.execute(text(sql_update_cpi_spi))
            cursor.commit()
            # cursor.close()


            
            # cursor = get_db_connection()
            cursor.execute(text(sql_app_id))
            cursor.commit()
            cursor.close()

            return redirect(url_for('student_bp.student_jobs_available'))
        
        # FOR RENDERING DROPDOWN MENU
        # fetch unapplied jobs id
        
        cursor = get_db_connection()
        
        job = cursor.execute(text(f"SELECT job.* FROM job where job_id={job_id};")).fetchone()


        # fetch job role names
        if job[1]=="ADH": 
            
            course_id, course_name = cursor.execute(text(f"SELECT course_id, course_name FROM adh WHERE job_id = {job[0]};")).fetchone()
            job_role=(f"ADH: {course_id} - {course_name}")
        elif job[1]=="PAL": 
            
            subjects_to_teach = cursor.execute(text(f"SELECT subjects_to_teach FROM subjects_under_pal WHERE job_id = {job[0]};")).fetchone()[0]
            job_role=(f"PAL: {subjects_to_teach}")
        else:
            
            role_name = cursor.execute(text(f"SELECT role_name FROM others WHERE job_id = {job[0]};")).fetchone()[0]
            job_role=(f"{role_name}")                

        cursor.close()
        return render_template('student/apply_job.html', job_id=job_id, job_role=job_role)
    
    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/applied_jobs', methods=['GET', 'POST'])
def student_applied_jobs():
    # db=get_db()
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = get_db_connection()

        # fetch applied jobs
        sql = f"SELECT application_status.application_id, job.job_id, job.job_type, job.job_description, application_status.approval FROM job JOIN application_status ON job.job_id = application_status.job_id WHERE application_status.roll_number = {roll_number};"
        
        applied_jobs = cursor.execute(text(sql)).fetchall()
        cursor.close()

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
                cursor = get_db_connection()
                sql_delete_application = f"DELETE FROM application_status WHERE application_id = {application_id};"
                # sql_delete_job_application = f"DELETE FROM job_application WHERE application_id = {application_id};"
                # sql_delete_student_application = f"DELETE FROM student_application WHERE application_id = {application_id};"

                # cursor.execute(sql_delete_student_application)
                # db.connection.commit()

                # cursor.execute(sql_delete_job_application)
                # db.connection.commit()

                cursor.execute(text(sql_delete_application))
                cursor.commit()
                cursor.close()
                return redirect(url_for('student_bp.student_applied_jobs'))
                return render_template_string(f"""
                    <script>
                        alert("Application deleted successfully! Query Executed: {sql_delete_application}");
                        window.location.href = "{{{{ url_for('student_applied_jobs') }}}}";
                    </script>
                """)
        
        return render_template('student/applied_jobs.html', job_data = applied_jobs, job_head = column_names)

    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/my_jobs', methods=['GET', 'POST'])
def student_my_jobs():
    # db=get_db()
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = get_db_connection()

        if request.method == 'POST':
            if request.form['submit_button'] == 'view':
                job_id = request.form['job_id']
                return redirect(url_for('student_bp.student_timecard', job_id=job_id))
            elif request.form['submit_button'] == 'mentees':
                return redirect(url_for('student_bp.student_mentees'))
                
        # fetch my jobs
        sql = f"SELECT application_status.application_id, job.job_id, job.job_type, job.job_description, application_status.approval FROM job JOIN application_status ON job.job_id = application_status.job_id WHERE application_status.roll_number = {roll_number} AND application_status.approval = 'approved';"
        
        my_jobs = cursor.execute(text(sql)).fetchall()
        cursor.close()

        # fetch column names
        # cursor.execute("SHOW COLUMNS FROM job")
        # job_head = cursor.fetchall()
        # column_names = tuple(row[0] for row in job_head)
        # cursor.close()

        #Mannualy fix the Column Heading
        column_names=('Application Id', 'Job Id', 'Job Type', 'Job Description', 'Approval Status')
        
        return render_template('student/my_jobs.html', job_data = my_jobs, job_head = column_names)

    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/mentees', methods=['GET', 'POST'])
def student_mentees():
    # db=get_db()
    if "roll_number" in session:
        roll_number = session['roll_number']
        cursor = get_db_connection()

        # fetch mentees
        sql = f"select mentee_roll_number, first_name, middle_name, last_name from mentees natural join mentor_mentee where mentor_mentee.roll_number = {roll_number};"
        
        mentees = cursor.execute(text(sql)).fetchall()

        # fetch column names
        # cursor.execute("SHOW COLUMNS FROM mentor_mentee")
        # mentee_head = cursor.fetchall()
        column_names = ['Mentee Roll Number', 'First Name', 'Middle Name', 'Last Name']
        cursor.close()

        return render_template('student/mentees.html', mentee_data = mentees, mentee_head = column_names)

    else:
        return redirect(url_for('auth_bp.errorpage'))

@student_bp.route('/timecard/<job_id>', methods=['GET', 'POST'])
def student_timecard(job_id):
    # db=get_db()
    if "roll_number" in session and check_authorization(session['roll_number'],job_id):
        roll_number = session['roll_number']
        cursor = get_db_connection()
        if request.method == 'POST':
            if request.form['submit_button'] == 'submit_timecard':
                return redirect(url_for('student_bp.submit_timecard',job_id=job_id))

        # fetch timecard data
        sql = f"SELECT * FROM time_card WHERE roll_number = {roll_number} AND job_id = {job_id};"
        result=cursor.execute(text(sql))
        timecard_data = result.fetchall()
        column_names = ['job_id','roll_number', 'month', 'year', 'hours_worked', 'work_description', 'faculty_approval', 'payment_status','oceo_coordinator_approval']
        cursor.close()
        return render_template('student/timecard.html', timecard_data = timecard_data, timecard_head = column_names,job_id=job_id)

@student_bp.route('/submit_timecard/<job_id>', methods=['GET', 'POST'])
def submit_timecard(job_id):
    # db=get_db()
    if "roll_number" in session and check_authorization(session['roll_number'],job_id): 
        current_year = datetime.datetime.now().year
        roll_number = session['roll_number']
        cursor = get_db_connection()
        if request.method == 'POST':
            if request.form['submit_button'] == "submit_timecard":
                month = request.form.get('month')
                year = request.form.get('year')
                hours_worked = request.form.get('hours_worked')
                work_description = request.form.get('work_description')
                sql = f"INSERT INTO time_card (roll_number, job_id, month, year, hours_worked, work_description, faculty_approval, payment_status) VALUES ({roll_number}, {job_id}, '{month}', {year}, {hours_worked}, '{work_description}','pending', 'pending');"
                cursor.execute(text(sql))
                cursor.commit()
                cursor.close()  
                return redirect(url_for('student_bp.student_timecard', job_id=job_id))
        return render_template('student/new_timecard.html', job_id=job_id, current_year=current_year)
    else:
        return redirect(url_for('auth_bp.errorpage'))    

@student_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # db=get_db()
    if "roll_number" in session:
        if request.method == 'POST':
            roll_number = session['roll_number']
            cursor = get_db_connection()
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            result=cursor.execute(text(f"SELECT password FROM applied_student WHERE roll_number = {roll_number};"))
            hashed_password = result.fetchone()[0]
            cursor.close()
            if bcrypt.check_password_hash(hashed_password, old_password):
                if new_password == confirm_password:
                    new_hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    cursor = get_db_connection()
                    cursor.execute(text(f"UPDATE applied_student SET password = '{new_hashed_password}' WHERE roll_number = {roll_number};"))
                    cursor.commit()
                    cursor.close()
                    return redirect(url_for('student_bp.student_personal_info'))
                else:
                    return redirect(url_for('auth_bp.errorpage'))
            else:
                return redirect(url_for('auth_bp.errorpage'))
        return render_template('student/change_password.html')
    else:
        return redirect(url_for('auth_bp.errorpage'))
                
@student_bp.route('/logout')
def logout():
    session.pop('roll_number', None)
    return redirect(url_for('auth_bp.index'))

# ------------- END OF STUDENT -------------------------------------------------------------------------
