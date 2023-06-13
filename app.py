import os  
from flask import Flask, render_template, request, redirect, url_for  
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy_utils import UUIDType
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required  
import openai  

# Configure the Flask app:
app = Flask(__name__)  
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT")  
app.config["SECURITY_REGISTERABLE"] = False  
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False  
  
db = SQLAlchemy(app)  

# Create user and role models for Flask-Security
roles_users = db.Table("roles_users", db.Column("user_id", db.Integer(), db.ForeignKey("user.id")), db.Column("role_id", db.Integer(), db.ForeignKey("role.id")))  
  
class Role(db.Model, RoleMixin):  
    id = db.Column(db.Integer(), primary_key=True)  
    name = db.Column(db.String(80), unique=True)  
    description = db.Column(db.String(255))  
  
class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(255), unique=True)  
    password = db.Column(db.String(255))  
    active = db.Column(db.Boolean())  
    confirmed_at = db.Column(db.DateTime())  
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))  
    fs_uniquifier = db.Column(UUIDType(binary=False), unique=True, nullable=False)  


# Set up Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)  
security = Security(app, user_datastore)  

# Create an admin role and default admin user
@app.before_first_request  
def create_admin_user():  
    db.create_all()  
  
    admin_role = user_datastore.find_or_create_role('admin', description='Administrator')  
    admin_email = os.environ.get("ADMIN_EMAIL") 
    admin_password = os.environ.get("ADMIN_PASSWORD")
  
    if not user_datastore.get_user(admin_email):  
        user_datastore.create_user(email=admin_email, password=admin_password, roles=[admin_role])  
        db.session.commit()  

# Initialize the ChatGPT API
openai.api_key = os.environ["CHATGPT_API_KEY"]  

# Create routes for your web app
@app.route("/")  
@login_required  
def index():  
    return render_template("index.html")  
  
@app.route("/chat", methods=["POST"])  
@login_required  
def chat():  
    message = request.form["message"]  
    response = openai.Completion.create(
        engine="gpt432k-dep",
        prompt=message, 
        max_tokens=16000, 
        n=1, 
        stop=None, 
        temperature=0.4
        )  
    return {"response": response.choices[0].text.strip()}  
  
if __name__ == "__main__":  
    app.run()  
