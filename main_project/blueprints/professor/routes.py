

from flask import Flask, render_template, request, redirect, url_for, session, Blueprint,current_app,g
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
from main_project import bcrypt
from sqlalchemy import create_engine, text
from flask import session, redirect, url_for, render_template_string




professor_bp = Blueprint('professor_bp', __name__,template_folder='templates',static_url_path='/static',static_folder='static')

def get_db_connection():
    engine = create_engine('mysql://oceoAdmin:oceoAdmin@localhost/oceo_management')
    print("Engine created")
    return engine.connect()




# ------------- START OF PROF --------------------------------------------------------------------------

@professor_bp.route('', methods=['GET', 'POST']) # professor homepage
def after_login_professor():
    if "faculty_id" in session:
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'personal_info':
                    return redirect(url_for('professor_bp.professor_personal_info'))
                case 'jobs_created':
                    return redirect(url_for('professor_bp.professor_jobs_created'))
                case 'timecard_for_review':
                    return redirect(url_for('professor_bp.professor_timecard_for_review'))
                case 'logout':
                    return redirect(url_for('professor_bp.professor_logout'))
                case _:
                    return render_template('professor/after_login.html')
        cursor =get_db_connection()
        faculty_id = session['faculty_id']
        faculty_name = cursor.execute(text(f"SELECT first_name FROM faculty WHERE faculty_id = {faculty_id};")).fetchall()[0][0]
        cursor.close()
        return render_template('professor/after_login.html', faculty_name=faculty_name)
    else:
        return render_template('errorpage.html')

@professor_bp.route('/personal_info', methods=['GET', 'POST'])
def professor_personal_info():
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'Update Profile':
                return redirect(url_for('professor_bp.professor_personal_info_change'))
            elif request.form['submit_button'] == 'Change Password':
                return redirect(url_for('professor_bp.professor_change_password'))
            
        cursor =get_db_connection()
        faculty_id = session['faculty_id']
        
        fetched_data = cursor.execute(text(f"SELECT * FROM faculty WHERE faculty_id = {faculty_id};")).fetchall()
        cursor.close()
        return render_template('professor/personal_info.html', professor_data=fetched_data)
    else:
        return redirect(url_for('auth_bp.errorpage'))
    
@professor_bp.route('/update_profile', methods=['GET', 'POST'])
def professor_personal_info_change():
    if "faculty_id" in session:
        if request.method == 'POST':
            faculty_id = session['faculty_id']
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name')
            last_name = request.form.get('last_name')
            dept_name = request.form.get('department_name')
            voip_id = request.form.get('voip_id')
            cursor =get_db_connection()
            cursor.execute(text(f"UPDATE faculty SET first_name = '{first_name}', middle_name = '{middle_name}', last_name = '{last_name}', dept_name = '{dept_name}', voip_id = {voip_id} WHERE faculty_id = {faculty_id}"))
            cursor.commit()

            if 'image' in request.files:
                image = request.files['image']
                image_data = image.read()
                cursor.execute(text(f"UPDATE faculty SET image = {image_data} WHERE faculty_id = {faculty_id};"))
                cursor.commit()
            
            cursor.close()
            return redirect(url_for('professor_bp.professor_personal_info'))
        cursor =get_db_connection()
        faculty_id = session['faculty_id']
        
        fetched_data = cursor.execute(text(f"SELECT * FROM faculty WHERE faculty_id = {faculty_id};")).fetchall()
        cursor.close()
        return render_template('professor/personal_info_change.html', professor_data=fetched_data)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/change_password', methods=['GET', 'POST'])
def professor_change_password():
    if "faculty_id" in session:
        if request.method == 'POST':
            faculty_id = session['faculty_id']
            cursor =get_db_connection()
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            hashed_password = cursor.execute(text(f"SELECT password FROM faculty WHERE faculty_id = {faculty_id};")).fetchone()[0]
            cursor.close()
            if bcrypt.check_password_hash(hashed_password, old_password):
                if new_password == confirm_password:
                    new_hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    cursor =get_db_connection()
                    cursor.execute(text(f"UPDATE faculty SET password = '{new_hashed_password}' WHERE faculty_id = {faculty_id};"))
                    cursor.commit()
                    cursor.close()
                    return redirect(url_for('professor_bp.professor_personal_info'))
                else:
                    return redirect(url_for('auth_bp.errorpage'))
            else:
                return redirect(url_for('auth_bp.errorpage'))
        return render_template('professor/change_password.html')
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/jobs_created', methods=['GET', 'POST'])
def professor_jobs_created():
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'job_page':
                job_id = request.form['job_id']
                return redirect(url_for('professor_bp.professor_job_page', job_id=job_id))
            
        
        cursor =get_db_connection()
        faculty_id = session['faculty_id']
        result=cursor.execute(text(f"SELECT job_id,job_type,job_description,pay_per_hour,start_date,end_date,is_available FROM job WHERE job.faculty_id = {faculty_id};"))
        job_data = result.fetchall()
        
        column_names =['job_id','job_type','job_description','pay_per_hour','start_date','end_date','is_available']
        cursor.close()
        return render_template('professor/jobs_created.html', job_data=job_data, job_head=column_names)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/add_job', methods=['GET', 'POST'])
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
            cursor =get_db_connection()
            result=cursor.execute(text("SELECT count(*) FROM job"))
            total_count = result.fetchone()[0]
            if total_count == 0:
                job_id = random.randint(12345678, 29999999)
            else:
                
                max_id = cursor.execute(text("SELECT MAX(job_id) FROM job")).fetchone()[0]
                job_id = max_id + 1

            cursor.execute(text(f"INSERT INTO job (job_id, job_type, job_description, min_qualifications, job_criteria, prerequisites, additional_info, pay_per_hour, no_of_positions, start_date, end_date, tenure, faculty_id, is_available, application_deadline) VALUES ({job_id}, '{job_type}', '{job_description}', '{min_qualifications}', '{job_criteria}', '{prerequisites}', '{additional_info}', {pay_per_hour}, {no_of_positions}, '{start_date}', '{end_date}', '{tenure}', {faculty_id}, {is_position_open}, '{application_deadline}');"))
            cursor.commit()
            if job_type == 'ADH':
                course_id = request.form.get('course_id')
                course_name = request.form.get('course_name')
                cursor.execute(text(f"INSERT INTO adh (job_id, course_id, course_name) VALUES ({job_id}, '{course_id}', '{course_name}');"))
                cursor.commit()
            elif job_type == 'PAL':
                subjects_to_teach = request.form.get('subjects_to_teach')
                cursor.execute(text(f"INSERT INTO subjects_under_pal (job_id, subjects_to_teach) VALUES ({job_id}, '{subjects_to_teach}');"))
                cursor.commit()
            else:
                role_name = request.form.get('role_name')
                cursor.execute(text(f"INSERT INTO others (job_id, role_name) VALUES ({job_id}, '{role_name}');"))
                cursor.commit()
            
            cursor.close()
            return redirect(url_for('professor_bp.professor_jobs_created'))
        return render_template('professor/add_job.html')
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/job_page/<job_id>', methods=['GET', 'POST'])
def professor_job_page(job_id):
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form.get('submit_button') == 'change_job_details':
                return redirect(url_for('professor_bp.professor_jobs_change_details', job_id=job_id))
            elif request.form.get('submit_button') == 'delete_job':
                return redirect(url_for('professor_bp.professor_delete_job', job_id=job_id))
            elif request.form.get('submit_button') == 'view_applications':
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
            elif request.form.get('submit_button') == 'approved_applications':
                return redirect(url_for('professor_bp.professor_approved_applications', job_id=job_id))
            # elif idhar sochha tha kuch yaad nahi aa ra baadme dekh lena
            elif request.form.get('submit_button') == "assign_mentees":
                roll_number = request.form.get('roll_number')
                return redirect(url_for('professor_bp.professor_assign_mentees', job_id=job_id, roll_number=roll_number))
            elif request.form.get('submit_button') == "stop_accepting_applications":
                return redirect(url_for('professor_bp.professor_stop_accepting_applications', job_id=job_id))
                        
        cursor =get_db_connection()
        query_get_students_under_job = f"SELECT roll_number,first_name,middle_name,last_name,email_id FROM applied_student WHERE roll_number IN (SELECT roll_number FROM application_status WHERE job_id = '{job_id}' and approval='approved');"
        result=cursor.execute(text(query_get_students_under_job))
        student_under_job_data = result.fetchall()
        # cursor.execute("SHOW COLUMNS FROM job")
        # job_head = cursor.fetchall()
        
        student_under_job_head = ['roll_number','first_name','middle_name','last_name','email_id']
        query_job_type = f"SELECT * FROM job WHERE job_id = {job_id};"
        
        job = cursor.execute(text(query_job_type)).fetchall()
        cursor.close()

        return render_template('professor/job_page.html', student_under_job_head=student_under_job_head, student_under_job_data=student_under_job_data,job_id=job_id,job=job)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/assign_mentees/<job_id>&<roll_number>', methods=['GET', 'POST'])
def professor_assign_mentees(job_id, roll_number):
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'assign_mentees':
                
                # roll_number = request.form['roll_number']
                mentee_roll_number = request.form['mentee_roll_number']
                first_name = request.form['first_name']
                middle_name = request.form['middle_name']
                last_name = request.form['last_name']
                
                cursor =get_db_connection()
                cursor.execute(text(f"INSERT INTO mentees (mentee_roll_number, first_name, middle_name, last_name) values ({mentee_roll_number}, '{first_name}', '{middle_name}', '{last_name}');"))
                cursor.commit()
                cursor.execute(text(f"INSERT INTO mentor_mentee (mentee_roll_number, roll_number, job_id) VALUES ({mentee_roll_number}, {roll_number}, {job_id});"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_job_page', job_id=job_id, roll_number=roll_number))
                
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
            
        cursor =get_db_connection()
        result=cursor.execute(text(f"SELECT roll_number, first_name, middle_name, last_name FROM applied_student WHERE roll_number IN (SELECT roll_number FROM application_status WHERE job_id = {job_id} AND approval = 'approved');"))
        mentee_data = result.fetchall()
        cursor.close()
        return render_template('professor/assign_mentees.html', mentee_data=mentee_data, job_id=job_id, roll_number=roll_number)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/change_job_details/<job_id>', methods=['GET', 'POST'])
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
            cursor =get_db_connection()
            if job_type == 'ADH':
                course_id = request.form.get('course_id')
                course_name = request.form.get('course_name')
                cursor.execute(text(f"UPDATE adh SET course_id = '{course_id}', course_name = '{course_name}' WHERE job_id = {job_id};"))
            elif job_type == 'PAL':
                subjects_to_teach = request.form.get('subjects_to_teach')
                cursor.execute(text(f"UPDATE subjects_under_pal SET subjects_to_teach = '{subjects_to_teach}' WHERE job_id = {job_id};"))
            else:
                role_name = request.form.get('role_name')
                cursor.execute(text(f"UPDATE others SET role_name = '{role_name}' WHERE job_id = {job_id};"))
            cursor.execute(text(f"UPDATE job SET job_type = '{job_type}', job_description = '{job_description}', min_qualifications = '{min_qualifications}', job_criteria = '{job_criteria}', prerequisites = '{prerequisites}', additional_info = '{additional_info}', pay_per_hour = {pay_per_hour}, no_of_positions = {no_of_positions}, start_date = '{start_date}', end_date = '{end_date}', tenure = '{tenure}', faculty_id = {faculty_id}, application_deadline = '{application_deadline}' WHERE job_id = {job_id};"))
            cursor.commit()
            cursor.close()
            return redirect(url_for('professor_bp.professor_jobs_created'))
        
        cursor =get_db_connection()
        job_data = cursor.execute(text(f"SELECT job.* FROM job WHERE job.job_id = {job_id};")).fetchall()
        job_head = cursor.execute(text("SHOW COLUMNS FROM job")).fetchall()
        column_names = tuple(row[0] for row in job_head)
        cursor.close()
        return render_template('professor/change_job_details.html', job_data=job_data, job_head=column_names)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/delete_job/<job_id>', methods=['GET', 'POST'])
def professor_delete_job(job_id):
    if "faculty_id" in session:
        cursor =get_db_connection()
        
        result=cursor.execute(text(f"select job_type from job where job_id = {job_id};"))
        job_type = result.fetchone()[0]
        if job_type == "ADH":
            cursor.execute(text(f"DELETE FROM adh WHERE job_id = {job_id};"))
        elif job_type == "PAL":
            cursor.execute(text(f"DELETE FROM subjects_under_pal WHERE job_id = {job_id};"))
        else:
            cursor.execute(text(f"DELETE FROM others WHERE job_id = {job_id};"))

        cursor.execute(text(f"DELETE FROM application_status WHERE job_id = {job_id};"))
        cursor.execute(text(f"DELETE FROM time_card WHERE job_id = {job_id};"))
        cursor.execute(text(f"DELETE FROM job WHERE job_id = {job_id};"))
        cursor.commit()
        cursor.close()
        return redirect(url_for('professor_bp.professor_jobs_created'))
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/view_applications/<job_id>', methods=['GET', 'POST'])
def professor_view_applications(job_id):
    if "faculty_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
        cursor =get_db_connection()
        cursor.execute(text(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;"))
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
        cursor =get_db_connection()
        result=cursor.execute(text(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;"))
        application_data = result.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        column_names = ['application_id','roll_number','first_name','middle_name','last_name','cpi','last_sem_spi','on_probation','approval','statement_of_motivation']
        cursor.close()
        return render_template('professor/view_applications.html', application_data=application_data, application_head=column_names, job_id=job_id)
    else:
        return redirect(url_for('auth_bp.errorpage'))

def other_view_applications(job_id):
    if "other_id" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
        cursor =get_db_connection()
        cursor.execute(text(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;"))
        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))

                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 1 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
            elif request.form['submit_button'] == 'reject':
                application_id = request.form['application_id']
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))
                cursor.execute(text(f"UPDATE application_status SET faculty_approved = 0 WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_view_applications', job_id=job_id))
        cursor =get_db_connection()
        result=cursor.execute(text(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 0;"))
        application_data = result.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        application_head = result.description
        column_names = tuple(row[0] for row in application_head)
        cursor.close()
        return render_template('professor/view_applications.html', application_data=application_data, application_head=column_names, job_id=job_id)
    else:
        return redirect(url_for('auth_bp.errorpage'))

# change below function
@professor_bp.route('/approved_applications/<job_id>', methods=['GET', 'POST'])
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
                cursor =get_db_connection()
                cursor.execute(text(f"SELECT application_id FROM application_status WHERE job_id = {job_id};"))
                cursor.execute(text(f"UPDATE application_status SET approval = 'rejected' WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_approved_applications', job_id=job_id))
        cursor =get_db_connection()
        result=cursor.execute(text(f"SELECT application_status.application_id, application_status.roll_number, applied_student.first_name, applied_student.middle_name, applied_student.last_name, applied_student.cpi, applied_student.last_sem_spi, applied_student.on_probation, application_status.approval, application_status.statement_of_motivation FROM application_status JOIN applied_student ON application_status.roll_number = applied_student.roll_number WHERE application_status.job_id = {job_id} and application_status.faculty_approved = 1;"))
        application_data = result.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        column_names = ['application_id','roll_number','first_name','middle_name','last_name','cpi','last_sem_spi','on_probation','approval','statement_of_motivation']
        cursor.close()
        return render_template('professor/approved_applications.html', application_data=application_data, application_head=column_names, job_id=job_id)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/timecard_for_review', methods=['GET', 'POST'])
def professor_timecard_for_review():
    if "faculty_id" in session:

        if request.method == 'POST':
            if request.form['submit_button'] == 'approve':
                # timecard_id = request.form['timecard_id']
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor =get_db_connection()
                cursor.execute(text(f"UPDATE time_card SET faculty_approval = 'approved' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_timecard_for_review'))
            elif request.form['submit_button'] == 'reject':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor =get_db_connection()
                cursor.execute(text(f"UPDATE time_card SET faculty_approval = 'rejected' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';"))
                cursor.commit()
                cursor.close()
                return redirect(url_for('professor_bp.professor_timecard_for_review'))
        cursor =get_db_connection()
        faculty_id = session['faculty_id']
        result1=cursor.execute(text(f"SELECT time_card.*, applied_student.first_name, applied_student.middle_name, applied_student.last_name FROM time_card JOIN applied_student ON time_card.roll_number = applied_student.roll_number WHERE time_card.faculty_approval = 'pending' AND time_card.job_id IN (SELECT job_id FROM job WHERE faculty_id = {faculty_id});"))
        timecard_data = result1.fetchall()
        result=cursor.execute(text("SHOW COLUMNS FROM time_card"))
        timecard_head = result.fetchall()
        column_names = tuple(row[0] for row in timecard_head)
        cursor.close()
        return render_template('professor/timecard_for_review.html', timecard_data=timecard_data, timecard_head=column_names)
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/stop_accepting_applications/<job_id>', methods=['GET', 'POST'])
def professor_stop_accepting_applications(job_id):

    if "faculty_id" in session:
        cursor =get_db_connection()
        cursor.execute(text(f"UPDATE job SET is_available = 'no' WHERE job_id = {job_id};"))
        cursor.commit()
        cursor.close()
        return redirect(url_for('professor_bp.professor_jobs_created'))
    else:
        return redirect(url_for('auth_bp.errorpage'))

@professor_bp.route('/logout')
def professor_logout():
    session.pop('faculty_id', None)
    return redirect(url_for('auth_bp.index'))
# ---------------------------------------------END OF PROFESSOR---------------------------------------------------------