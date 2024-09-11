

from flask import Flask, render_template, request, redirect, url_for, session, Blueprint,current_app,g
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
from sqlalchemy import create_engine, text
from flask import session, redirect, url_for, render_template_string

from main_project.blueprints.auth.routes import authenticate

others_bp = Blueprint('others_bp', __name__,template_folder='templates',static_url_path='/static',static_folder='static')

def get_db_connection():
    engine = create_engine('mysql://oceoAdmin:oceoAdmin@localhost/oceo_management')
    print("Engine created")
    return engine.connect()




#----------------------START OF Others-----------------------------------------------------------------


@others_bp.route('/<type>/after_login_other', methods=['GET', 'POST'])
def after_login_other(type):
    # db=get_db()
    if "email" in session:
        if request.method == 'POST':
            testvar = request.form['submit_button']
            match testvar:
                case 'applications_to_review':
                    return redirect(url_for('others_bp.review_application', type = type))
                case 'approved_jobs':
                    return redirect(url_for('others_bp.jobs_approved', type =type))
                case 'logout':
                    return redirect(url_for('others_bp.professor_logout'), type = type)
                case 'time_card':
                    return redirect(url_for('others_bp.timecard_for_payment', type = type))
                case 'pending_payments':
                    return redirect(url_for('others_bp.pending_payments', type = type))
                case "time_card_approve":
                    return redirect(url_for("others_bp.timecard_for_oceo_coordinator", type=type))
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


@others_bp.route('/<type>/pending_payments', methods=['GET', 'POST'])
def pending_payments(type):
    # db=get_db()
    if "email" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'payment_done':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                cursor = get_db_connection() 
                cursor.execute(text("LOCK TABLES time_card WRITE"))
                cursor.execute(text(f"UPDATE time_card SET payment_status ='done'  WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';"))
                cursor.commit()
                cursor.execute(text('UNLOCK TABLES'))
                cursor.close()
            return redirect(url_for('others_bp.pending_payments',type=type))
        
        cursor = get_db_connection()
        cursor.execute(text("select job_id, roll_number, pay_per_hour*hours_worked, account_number, IFSC_code, bank_name from job natural join time_card natural join bank_details where faculty_approval='approved' and payment_status ='pending'  order by job_id;"))
        timecard_data = cursor.fetchall()
        column_names = ['job_id', 'roll_number', 'amount', 'account_number', 'IFSC_code', 'bank_name']
        cursor.close()
        return render_template('others/admin/pending_payments.html', timecard_data=timecard_data, timecard_head=column_names,type1 = type)
    else:
        return redirect(url_for('auth_bp.errorpage'))


@others_bp.route('/<type>/timecard_for_payment', methods=['GET', 'POST'])
def timecard_for_payment(type):
    # db=get_db()
    if "email" in session:
        if request.method == 'POST':
            if request.form['submit_button'] == 'payment_done':
                job_id = request.form['job_id']
                roll_number = request.form['roll_number']
                month = request.form['month']
                print("#"*10)
                print(job_id, roll_number, month)
                print("#"*10)

                cursor = get_db_connection()
                cursor.execute(text("LOCK TABLES time_card  WRITE"))
                cursor.execute(text(f"UPDATE time_card SET payment_status ='done'  WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';"))
                cursor.commit()
                cursor.execute(text("UNLOCK TABLES"))
                cursor.close()

            # elif request.form['submit_button'] == 'reject':
            #     job_id = request.form['job_id']
            #     roll_number = request.form['roll_number']
            #     month = request.form['month']
            #     cursor = db.connection.cursor()
            #     cursor.execute(f"UPDATE time_card SET SA_approval ='rejected' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
            #     db.connection.commit()
            #     cursor.close()
            return redirect(url_for('others_bp.timecard_for_payment',type=type))
        
        
        cursor = get_db_connection()
        result=cursor.execute(text("select job_id, roll_number, month, job_description, pay_per_hour, hours_worked, pay_per_hour*hours_worked, account_number, IFSC_code, bank_name from job natural join time_card natural join bank_details where faculty_approval='approved' and oceo_coordinator_approval = 'approved' and payment_status ='pending' order by job_id;"))
        # cursor.execute("SELECT job_id, roll_number, month, year, work_description, pay_per_hour*hours_worked, hours_worked FROM job NATURAL JOIN time_card WHERE SA_approval='pending' ORDER BY job_id;")
        timecard_data = result.fetchall()
        column_names = ['job_id', 'roll_number', 'month', 'job_description', 'pay_per_hour', 'hours_worked', 'amount', 'account_number', 'IFSC_code', 'bank_name']
        cursor.close()
        return render_template('others/admin/timecard_for_SA.html', timecard_data=timecard_data, timecard_head=column_names,type1 = type)
    else:
        return redirect(url_for('auth_bp.errorpage'))
    
@others_bp.route('/<type>/jobs_approved', methods=['GET','POST'] )
def jobs_approved(type):
    # db=get_db()
    if "email" in session: 
        # if request.method == 'POST':
        cursor = get_db_connection()
        if type =='admin':
            query = 'SELECT * FROM application_status WHERE faculty_approved = 1;'
        elif type =='dean':
            query = 'SELECT * FROM application_status WHERE dean_approved = 1;'
        elif type =='sa_js':
            query = 'SELECT * FROM application_status WHERE SA_approved = 1;'
        elif type =='oceo_coordinator':
            query = 'SELECT * FROM application_status WHERE oceo_coordinator_approved = 1;'

        # query  = f'SELECT * FROM application_status WHERE {type}_approved = 1;' 
        result=cursor.execute(text(query))
        application_data = result.fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        column_names = ['application_id','faculty_approved', 'oceo_coordinator_approved', 'SA_approved', 'dean_approved', 'statement_of_motivation','roll_number','job_id','approval']
        cursor.close()
        return render_template('others/admin/jobs_approved.html', application_data=application_data, application_head=column_names,type = type)
    else:
        return redirect(url_for('auth_bp.errorpage'))
    
@others_bp.route('/<type>/review_application', methods=['GET', 'POST'])
def review_application(type):
    # db=get_db()
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
                cursor = get_db_connection()
                cursor.execute(text("LOCK TABLES application_status WRITE"))
                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(text(f"UPDATE application_status SET {perm} = 1 WHERE application_id = {application_id};"))
                if perm == 'dean_approved':
                    cursor.execute(text(f"UPDATE application_status SET approval = 'approved' WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.execute(text("UNLOCK TABLES"))
                cursor.close()
                return redirect(url_for('others_bp.review_application',type=type))
            elif request.form['submit_button'] == 'Reject':
                application_id = request.form['application_id']
                cursor = get_db_connection()
                cursor.execute(text("LOCK TABLES application_status WRITE"))
                # cursor.execute(f"SELECT application_id FROM application_status WHERE job_id = {job_id};")
                cursor.execute(text(f"UPDATE application_status SET {perm}= 0 WHERE application_id = {application_id};"))
                cursor.execute(text(f"UPDATE application_status SET approval = 'rejected' WHERE application_id = {application_id};"))
                cursor.commit()
                cursor.execute(text("UNLOCK TABLES"))
                cursor.close()
                return redirect(url_for('others_bp.review_application',type=type))
            
        cursor = get_db_connection()
        if perm == 'faculty_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0;'
        elif perm == 'oceo_coordinator_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0 and faculty_approved = 1;'
        elif perm == 'SA_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0 and faculty_approved = 1 and oceo_coordinator_approved = 1;'
        elif perm == 'dean_approved':
            query = f'SELECT * FROM application_status WHERE {perm} = 0 and faculty_approved = 1 and oceo_coordinator_approved = 1 and SA_approved = 1;'
        # query = f'SELECT * FROM application_status WHERE {perm} = 0;'
       
        application_data =  cursor.execute(text(query)).fetchall()
        # cursor.execute("SHOW COLUMNS FROM application_status")
        column_names = ['application_id','faculty_approved', 'oceo_coordinator_approved', 'SA_approved', 'dean_approved', 'statement_of_motivation','roll_number','job_id','approval']
        
        cursor.close()
        return render_template('others/admin/review_application.html', application_data=application_data, application_head=column_names, type = type)
    else:
        return redirect(url_for('auth_bp.errorpage'))
    
@others_bp.route("/<type>/timecard_for_oceo_coordinator", methods=["GET", "POST"])
def timecard_for_oceo_coordinator(type):
    # db=get_db()
    if "email" in session:
        if request.method == "POST":
            if request.form["submit_button"] == "approve":
                job_id = request.form["job_id"]
                roll_number = request.form["roll_number"]
                month = request.form["month"]
                cursor = get_db_connection()
                cursor.execute(
                    text(f"UPDATE time_card SET oceo_coordinator_approval='approved' WHERE job_id = {job_id} AND roll_number = {roll_number} AND month = '{month}';")
                )
                cursor.commit()
                cursor.close()
            return redirect(url_for("others_bp.timecard_for_oceo_coordinator", type=type))

        cursor = get_db_connection()
        result=cursor.execute(
            text("select job_id, roll_number, month, job_description, pay_per_hour, hours_worked from job natural join time_card where oceo_coordinator_approval='pending' order by job_id;")
        )
        timecard_data = result.fetchall()
        column_names = ['job_id', 'roll_number', 'month', 'job_description', 'pay_per_hour', 'hours_worked']
        cursor.close()
        return render_template(
            "others/admin/timecard_for_oceo.html",
            timecard_data=timecard_data,
            timecard_head=column_names,
            type=type,
        )
    else:
        return redirect(url_for("auth_bp.errorpage"))
    
@others_bp.route('/<type>/logout')
def professor_logout(type):
    session.pop('faculty_id', None)
    return redirect(url_for('auth_bp.index'))
#----------------------END OF Others-----------------------------------------------------------------