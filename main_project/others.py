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

# ----------------- OTHERS START ------------------------------------------------------------------------------

@app.route('/<type>/home', methods=['GET', 'POST'])
def others_home(type):
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
                case 'time_card':
                    return redirect(url_for('timecard_for_payment', type = type))
                case 'pending_payments':
                    return redirect(url_for('pending_payments', type = type))
                case "time_card_approve":
                    return redirect(url_for("timecard_for_oceo_coordinator", type=type))
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
    # if "email" in session:
    #     if request.method == 'POST':
    #         testvar = request.form['submit_button']
    #         match testvar:
    #             case 'applications_to_review':
    #                 return redirect(url_for('review_application', type = 'sa_js'))
    #             case 'approved_jobs':
    #                 return redirect(url_for('jobs_approved', type = 'sa_js'))
    #             case 'logout':
    #                 return redirect(url_for('professor_logout'))
    #             case _:
    #                 return render_template('others/admin/admin.html')
    # return render_template( 'others/admin/admin.html' )


@app.route('/<type>/pending_payments', methods=['GET', 'POST'])
def pending_payments(type):
    if "email" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'payment_done':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor = db.connection.cursor() 
                cursor.execute("LOCK TABLES time_card WRITE")
                cursor.execute(f"UPDATE time_card SET payment_status ='done'  WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                db.connection.commit()
                cursor.execute('UNLOCK TABLES')
                cursor.close()
            return redirect(url_for('pending_payments',type=type))
        
        cursor = db.connection.cursor()
        cursor.execute("select job_id, roll_number, pay_per_hour*hours_worked, account_number, IFSC_code, bank_name from job natural join time_card natural join bank_details where faculty_approval='approved' and payment_status ='pending'  order by job_id;")
        timecard_data = cursor.fetchall()
        timecard_head = cursor.description
        column_names = tuple(row[0] for row in timecard_head)
        cursor.close()
        return render_template('others/admin/pending_payments.html', timecard_data=timecard_data, timecard_head=column_names,type1 = type)
    else:
        return redirect(url_for('errorpage'))


@app.route('/<type>/timecard_for_payment', methods=['GET', 'POST'])
def timecard_for_payment(type):
    if "email" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'payment_done':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                print("#"*10)
                print(job_id, roll_number, month)
                print("#"*10)

                cursor = db.connection.cursor()
                cursor.execute("LOCK TABLES time_card  WRITE")
                cursor.execute(f"UPDATE time_card SET payment_status ='done'  WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                db.connection.commit()
                cursor.execute("UNLOCK TABLES")
                cursor.close()

            # elif request.form['submit_button'] == 'reject':
            #     job_id = request.form['job_id']
            #     roll_number = request.form['roll_number']
            #     month = request.form['month']
            #     cursor = db.connection.cursor()
            #     cursor.execute(f"UPDATE time_card SET SA_approval ='rejected' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
            #     db.connection.commit()
            #     cursor.close()
            return redirect(url_for('timecard_for_payment',type=type))
        
        
        cursor = db.connection.cursor()
        cursor.execute("select job_id, roll_number, month, job_description, pay_per_hour, hours_worked, pay_per_hour*hours_worked, account_number, IFSC_code, bank_name from job natural join time_card natural join bank_details where faculty_approval='approved' and oceo_coordinator_approval = 'approved' and payment_status ='pending' order by job_id;")
        # cursor.execute("SELECT job_id, roll_number, month, year, work_description, pay_per_hour*hours_worked, hours_worked FROM job NATURAL JOIN time_card WHERE SA_approval='pending' ORDER BY job_id;")
        timecard_data = cursor.fetchall()
        timecard_head = cursor.description
        column_names = tuple(row[0] for row in timecard_head)
        cursor.close()
        return render_template('others/admin/timecard_for_SA.html', timecard_data=timecard_data, timecard_head=column_names,type1 = type)
    else:
        return redirect(url_for('errorpage'))
    
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
                cursor.execute("LOCK TABLES application_status WRITE")
                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET {perm} = 1 WHERE application_id = {application_id};")
                if perm == 'dean_approved':
                    cursor.execute(f"UPDATE application_status SET approval = 'approved' WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.execute("UNLOCK TABLES")
                cursor.close()
                return redirect(url_for('review_application',type=type))
            elif request.form['submit_button'] == 'Reject':
                application_id = request.form['application_id']
                cursor = db.connection.cursor()
                cursor.execute("LOCK TABLES application_status WRITE")
                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(f"UPDATE application_status SET {perm}= 0 WHERE application_id = {application_id};")
                cursor.execute(f"UPDATE application_status SET approval = 'rejected' WHERE application_id = {application_id};")
                db.connection.commit()
                cursor.execute("UNLOCK TABLES")
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
    
@app.route("/<type>/timecard_for_oceo_coordinator", methods=["GET", "POST"])
def timecard_for_oceo_coordinator(type):
    if "email" in session:
        if request.method == "POST":
            if request.form["submit_button"] == "approve":
                job_id = request.form["job_id"]
                roll_number = request.form["roll_number"]
                month = request.form["month"]
                cursor = db.connection.cursor()
                cursor.execute(
                    f"UPDATE time_card SET oceo_coordinator_approval='approved' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';"
                )
                db.connection.commit()
                cursor.close()
            return redirect(url_for("timecard_for_oceo_coordinator", type=type))

        cursor = db.connection.cursor()
        cursor.execute(
            "select job_id, roll_number, month, job_description, pay_per_hour, hours_worked from job natural join time_card where oceo_coordinator_approval='pending' order by job_id;"
        )
        timecard_data = cursor.fetchall()
        timecard_head = cursor.description
        column_names = tuple(row[0] for row in timecard_head)
        cursor.close()
        return render_template(
            "others/admin/timecard_for_oceo.html",
            timecard_data=timecard_data,
            timecard_head=column_names,
            type=type,
        )
    else:
        return redirect(url_for("errorpage"))
    


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


#---------------------------------------------Accounts---------------------------------------------------------  

@app.route('/<type>/logout')
def admin_logout(type):
    session.pop('email', None)
    return redirect(url_for('index'))

# ----------------- OTHERS END ----------------------------------------------------------------------------------