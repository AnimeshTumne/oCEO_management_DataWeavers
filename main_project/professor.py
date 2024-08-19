from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
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

# ------------------------------------------------------------------------------------------------------

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
            if request.form['submit_button'] == 'Update Profile':
                return redirect(url_for('professor_personal_info_change'))
            elif request.form['submit_button'] == 'Change Password':
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
        query_get_students_under_job = f"SELECT roll_number,first_name,middle_name,last_name,email_id FROM applied_student WHERE roll_number IN (SELECT roll_number FROM application_status WHERE job_id = '{job_id}' and approval='approved');"
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

# change below function
# ???
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
                cursor.execute(f"UPDATE time_card SET faculty_approval = 'approved' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_timecard_for_review'))
            elif request.form['submit_button'] == 'reject':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor = db.connection.cursor()
                cursor.execute(f"UPDATE time_card SET faculty_approval = 'rejected' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                db.connection.commit()
                cursor.close()
                return redirect(url_for('professor_timecard_for_review'))
        cursor = db.connection.cursor()
        faculty_id = session['faculty_id']
        cursor.execute(f"SELECT time_card.*, applied_student.first_name, applied_student.middle_name, applied_student.last_name FROM time_card JOIN applied_student ON time_card.roll_number = applied_student.roll_number WHERE time_card.faculty_approval = 'pending' AND time_card.job_id IN (SELECT job_id FROM job WHERE faculty_id = {faculty_id});")
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

# ------------- END OF PROF --------------------------------------------------------------------------