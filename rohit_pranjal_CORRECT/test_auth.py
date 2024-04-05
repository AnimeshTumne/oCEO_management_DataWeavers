from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import flask_mysqldb as mysql
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'  # Update with your MySQL configuration
db = MySQL(app)
bcrypt = Bcrypt(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Professor Model
class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Admin Model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Create tables
db.create_all()

# Routes for Student
@app.route('/student/register', methods=['POST'])
def student_register():
    data = request.json
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    email = data['email']
    
    # Check if student already exists
    if Student.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists!'}), 400
    
    # Create new student
    new_student = Student(username=username, password=password, email=email)
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({'message': 'Student registered successfully'}), 201

# Routes for Professor
@app.route('/professor/register', methods=['POST'])
def professor_register():
    data = request.json
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    email = data['email']
    
    # Check if professor already exists
    if Professor.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists!'}), 400
    
    # Create new professor
    new_professor = Professor(username=username, password=password, email=email)
    db.session.add(new_professor)
    db.session.commit()
    
    return jsonify({'message': 'Professor registered successfully'}), 201

# Routes for Admin
@app.route('/admin/register', methods=['POST'])
def admin_register():
    data = request.json
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    email = data['email']
    
    # Check if admin already exists
    if Admin.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists!'}), 400
    
    # Create new admin
    new_admin = Admin(username=username, password=password, email=email)
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({'message': 'Admin registered successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
