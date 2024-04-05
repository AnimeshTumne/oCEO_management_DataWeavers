from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

plaintext_password = "admin"
hashed_password = bcrypt.generate_password_hash(plaintext_password).decode("utf-8")
print("hashed password")
print(hashed_password)