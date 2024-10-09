
from flask import  render_template, request, redirect, url_for, session, Blueprint,current_app,flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask import session, redirect, url_for, render_template_string
from authlib.integrations.flask_client import OAuth
from sqlalchemy import create_engine, text
from main_project import db
from functools import wraps


auth_bp = Blueprint('auth_bp', __name__,template_folder='templates',static_url_path='/static',static_folder='static')




# ------------------------------------------------------------------------------------------------------



oauth = OAuth(current_app)
bcrypt = Bcrypt(current_app)

def get_db_connection():
    engine = create_engine('mysql://oceoAdmin:oceoAdmin@localhost/oceo_management')
    print("Engine created")
    return engine.connect()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in by verifying 'email' in session
        if 'email' not in session:
            flash('You need to log in first.', 'danger')
            # Save the next path to redirect after login
            session['next'] = request.url
            return redirect(url_for('auth_bp.google'))
        
        return f(*args, **kwargs)
    
    return decorated_function



@auth_bp.route('/google',methods=['GET', 'POST'])
def google():
    GOOGLE_CLIENT_ID = "483725292816-7o6i235adoidqqhfv1hi0738paa4cfvr.apps.googleusercontent.com"  # Your Google Client ID
    GOOGLE_CLIENT_SECRET = "GOCSPX_JN9R4EpLa0Xx2V_bdqv02X9cqzTM"  # Your Google Client Secret
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'

    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        acess_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        userinfo_endpoint='https://googleapis.com/oauth2/v3/userinfo',
        server_metadata_url=CONF_URL,
        client_kwargs={'scope': 'openid email profile'}
    )

    # Define the redirect URI to handle Google OAuth callback
    redirect_url = url_for('auth_bp.google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_url)


# Google OAuth Callback Route
@auth_bp.route('/google/auth')
def google_auth():
    session['email'] = "iitgn.ac.in"

    # Check if there's a next path and redirect after login
    next_path = session.pop('next', None)
    if next_path:
        return redirect(next_path)
    
    return redirect(url_for('auth_bp.index'))

# ------------------------------------------------------------------------------------------------------
#syntax for locking and unclockign
# cursor.execute('LOCK TABLES mytable WRITE')
# make some updates
# cursor.execute('UNLOCK TABLES')
# Home Page - Select User Type
@auth_bp.route("/")
def index():
    return render_template("index.html")



# ---------------------------------------------- NEW USER REGISTRATION--------------------------------------------------------
# NEW USER REGISTRATION

@auth_bp.route("/login/new_user", methods=["GET", "POST"])
@login_required
def register():
    cursor = get_db_connection()
  
    if request.method == "POST":
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        new_roll_number = request.form["roll_number"]
        email = request.form["email"]
        userType = request.form.get('userType') 
        password = request.form["password"]
        
  
        if userType == "student":
            sql = f"SELECT count(*) FROM applied_student WHERE email_id='{email}'"
           
            isPresent =  cursor.execute(text(sql)).fetchone()[0]
            
            # remove integrity constraint on "on_probation" field
            on_probation_alter = "ALTER TABLE applied_student MODIFY on_probation BOOLEAN;"
            cursor.execute(text(on_probation_alter))
            #db.connection.commit()

            # user already exists
            if isPresent==1:
                error_message = ("User already exists. Please choose a different username.")
                return render_template("newuser.html", error_message=error_message)
            
            # new user registration
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                sql = f"INSERT INTO applied_student (roll_number, first_name, middle_name, last_name, email_id, password) VALUES ({new_roll_number},'{first_name}','{middle_name}','{last_name}','{email}','{hashed_password}');"
                cursor.execute(text(sql))
                #db.connection.commit()
                #cursor.close()
                return redirect(url_for("auth_bp.index"))
                return render_template_string(f"""
                    <script>
                        alert("User registered successfully! Query Executed: {sql}");
                        window.location.href = "{{{{ url_for('auth_bp.index') }}}}";
                    </script>
                """)

        elif userType == "professor":
            sql = f"SELECT count(*) FROM faculty WHERE email_id='{email}'"
           
            isPresent =  cursor.execute(text(sql)).fetchone()[0]

            if isPresent==1:
                error_message = ("User already exists. Please choose a different username.")
                return render_template("newuser.html", error_message=error_message)
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                sql = f"INSERT INTO faculty (faculty_id, first_name, middle_name, last_name, email_id, password, dept_name) VALUES ({new_roll_number},'{first_name}','{middle_name}','{last_name}','{email}','{hashed_password}', 'Not Added');"
                cursor.execute(sql)
                #db.connection.commit()
                cursor.close()
                return redirect(url_for("auth_bp.index"))
        # TODO non-student new user
        else:
            return redirect(url_for("auth_bp.errorpage"))
    
    return render_template("newuser.html")





# -------------------------------------------------AUTHENTICATION-----------------------------------------------------
# check the credentials of the user 
def authenticate(email, password, userType):
    cursor = get_db_connection()
    
    if userType == "student":
        sql = f"SELECT COUNT(*) FROM applied_student WHERE email_id='{email}'"
        
        result = cursor.execute(text(sql)).fetchone()
        if result[0] > 0:
            sql = f"SELECT password FROM applied_student WHERE email_id='{email}'"
        else:
            return False
    elif userType == "professor":
        sql = f"SELECT COUNT(*) FROM faculty WHERE email_id='{email}'"
       
        result =  cursor.execute(text(sql)).fetchone()
        if result[0] > 0:
            sql = f"SELECT password FROM faculty WHERE email_id='{email}'"
        else:
            return False
        # sql = f"SELECT password FROM faculty WHERE email_id='{email}'"
    elif userType == "others":
        sql = f"SELECT COUNT(*) FROM other WHERE email='{email}'"
        
        result = cursor.execute(text(sql)).fetchone()
        if result[0] > 0:
            sql = f"SELECT password FROM other WHERE email='{email}'"
        else:
            return False
        sql = f"SELECT password FROM other WHERE email = '{email}'"
    
    result = cursor.execute(text(sql)).fetchone()
    cursor.close()
   
    if bcrypt.check_password_hash(result[0], password):
        return True
    else:
        return False
# -------------------------------------------------LOGIN PAGE-----------------------------------------------------
@auth_bp.route('/login/student', methods=['GET', 'POST'])
@login_required   
def login_student():
    cursor = get_db_connection()
    if request.method == 'POST':
        email = request.form["username"]
        password = request.form["password"]

        # fetch roll number from database

        if authenticate(email, password, "student"):
            
            sql = f"SELECT roll_number FROM applied_student WHERE email_id='{email}'"
            
            roll_number = cursor.execute(text(sql)).fetchone()[0]
            cursor.close()
            # ACTIVATES THE SESSION (logged in)
            session["roll_number"] = roll_number
            # Render a template with JavaScript to show a popup
            return redirect(url_for('student_bp.after_login_student'))
            return render_template_string(f"""
                <script>
                    // Show popup
                    alert("Successfully logged in as a Student. Successfully Executed:{sql}'");
                    // Redirect to the desired page
                    window.location.href = "{{{{ url_for('after_login_student') }}}}";
                </script>
            """)
        else:
            return render_template("errorpage.html", error_message="Bad Credentials! Change password or email, and try again.")

    return render_template('student.html')

@auth_bp.route('/login/professor', methods=['GET', 'POST'])
@login_required
def login_professor():
    cursor = get_db_connection()
    if request.method == 'POST':
        email = request.form["username"]
        password = request.form["password"]

        if authenticate(email, password, "professor"):
            # ACTIVATES THE SESSION (logged in)
            # fetch faculty id from database
           
            sql = f"SELECT faculty_id FROM faculty WHERE email_id='{email}'"
            
            faculty_id = cursor.execute(text(sql)).fetchone()[0]
            # cursor.close()
            session["faculty_id"] = faculty_id
            return redirect(url_for('professor_bp.after_login_professor'))
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
            return redirect(url_for("auth_bp.errorpage", error_message="Bad Credentials! Change password or email, and try again."))
    return render_template('professor.html')

@auth_bp.route('/login/others',  methods=['GET', 'POST'])
@login_required
def others_login():
    cursor = get_db_connection()
    if request.method == 'POST':
        email = request.form["username"] 
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
                
                sql = "SELECT email FROM other WHERE user_type = 'admin';"
                
                admin_email =  cursor.execute(text(sql)).fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_bp.after_login_other", type = 'admin'))
                else:
                    return redirect(url_for("auth_bp.errorpage"))
            elif userType == 'Dean':
              
                sql = "SELECT email FROM other WHERE user_type = 'dean';"
                
                admin_email =  cursor.execute(text(sql)).fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_bp.after_login_other", type = 'dean'))
                else:
                    return redirect(url_for("auth_bp.errorpage"))
                
            elif userType == 'SA JS':
                
                sql = "SELECT email FROM other WHERE user_type = 'sa_js';"
                # cursor.execute(text(sql))
                admin_email =  cursor.execute(text(sql)).fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_bp.after_login_other", type = 'sa_js'))
                else:
                    return redirect(url_for("auth_bp.errorpage"))
                
            elif userType == 'oCEO Coordinator':
                
                sql = "SELECT email FROM other WHERE user_type = 'oceo_coordinator';"
                
                admin_email =  cursor.execute(text(sql)).fetchone()[0]
                cursor.close()

                if admin_email == email :
                    return redirect(url_for("others_bp.after_login_other", type = 'oceo_coordinator'))
                else:
                    return redirect(url_for("auth_bp.errorpage"))
     
                       
        else:
            return redirect(url_for("auth_bp.errorpage", message="Invalid Credentials for <type> login"))
    return render_template('others.html')



@auth_bp.route("/errorpage")
def errorpage(error_message="Bad Credentials! Go back and try again."):
    # error_message = "Bad Credentials!"
    return render_template("errorpage.html", error_message=error_message if error_message else "You are not authorised to view this page. Please login first.")