import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import UUIDType
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    UserMixin,
    RoleMixin,
    login_required,
)
import openai

# Specify OpenAI in Azure
openai.api_type = "azure"
openai.api_base = "https://openai-demo-nc2023.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

# Configure the Flask app:
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT")
app.config["SECURITY_REGISTERABLE"] = False
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False

db = SQLAlchemy(app)

# Create user and role models for Flask-Security
roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


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
    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
    )
    fs_uniquifier = db.Column(UUIDType(binary=False), unique=True, nullable=False)


# Set up Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create an admin role and default admin user
# @app.before_first_request
# def create_admin_user():
with app.app_context():
    db.create_all()
    admin_role = user_datastore.find_or_create_role(
        "admin", description="Administrator"
    )
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not user_datastore.find_user(email=admin_email):
        user_datastore.create_user(
            email=admin_email, password=admin_password, roles=[admin_role]
        )
        db.session.commit()

# Initialize the ChatGPT API
openai.api_key = os.environ["CHATGPT_API_KEY"]
print("API Key:", os.environ["CHATGPT_API_KEY"])


# Create routes for your web app
@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
@login_required
def chat():
    # message = request.form["message"]
    cv_input = request.form["message"]
    response = openai.ChatCompletion.create(
        engine="gpt432k-dep",  # replace this value with the deployment name you chose when you deployed the associated model.
        messages=[
            {
                "role": "system",
                "content": "You are a language model tasked with analyzing the writing style, attitudes, sentiment, and personality of a company i will provide. You will be provided with a collection of texts, including blog posts, social media updates, press releases, and customer reviews, to understand and capture the essence of the company's communication style. Your objective is to extract insights regarding the sentiment, personality traits, and overall tone of the company's written content.",
            },
            {
                "role": "assistant",
                "content": "I want you to create a professional CV in html format and using the below input:",
            },
            {"role": "assistant", "content": cv_input},
            {
                "role": "assistant",
                "content": """ when generating the output, use the exact format as in below:
 <!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <link rel="stylesheet" type="text/css" href="dep/normalize.css/normalize.css" />
    <link rel="stylesheet" type="text/css" href="dep/Font-Awesome/css/font-awesome.css" />
    <link rel="stylesheet" type="text/css" href="style.css" />
  </head>
  <body lang="en">
    <section id="main">
      <header id="title">
        <h1>John Doe</h1>
        <span class="subtitle">Plaintiff, defendant &amp; witness</span>
      </header>
      <section class="main-block">
        <h2>
          <i class="fa fa-suitcase"></i> Experiences
        </h2>
        <section class="blocks">
          <div class="date">
            <span>2015</span><span>present</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Some Position</h3>
              <span class="place">Some Workplace</span>
              <span class="location">(remote)</span>
            </header>
            <div>
              <ul>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec mi ante. Etiam odio eros, placerat eu metus id, gravida eleifend odio. Vestibulum dapibus pharetra odio, egestas ullamcorper ipsum congue ac. Maecenas viverra tortor eget convallis vestibulum. Donec pulvinar venenatis est, non sollicitudin metus laoreet sed. Fusce tincidunt felis nec neque aliquet porttitor</li>
              </ul>
              </div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
            <span>2014</span><span>2015</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Another Position</h3>
              <span class="place">Some Workplace</span>
              <span class="location">Some City, Some Country</span>
            </header>
            <div>
              <ul>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
              </ul>
            </div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
            <span>2013</span><span>2014</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Yet Another Job Position</h3>
              <span class="place">Some Workplace</span>
              <span class="location">Some City, Some Country</span>
            </header>
            <div>
              <ul>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec mi ante. Etiam odio eros, placerat eu metus id, gravida eleifend odio</li>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
              </ul>
              </div>
          </div>
        </section>
      </section>
      <section class="main-block">
        <h2>
          <i class="fa fa-folder-open"></i> Selected Projects
        </h2>
        <section class="blocks">
          <div class="date">
            <span>2015</span><span>2016</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Some Project 1</h3>
              <span class="place">Some workplace</span>
            </header>
            <div>
              <ul>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec mi ante. Etiam odio eros, placerat eu metus id, gravida eleifend odio. Vestibulum dapibus pharetra odio, egestas ullamcorper ipsum congue ac</li>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec mi ante. Etiam odio eros, placerat eu metus id, gravida eleifend odio</li>
              </ul>
            </div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
            <span>2014</span><span>2015</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Some Project 2</h3>
              <span class="place">Some workplace</span>
            </header>
            <div>
              <ul>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec mi ante. Etiam odio eros, placerat eu metus id, gravida eleifend odio. Vestibulum dapibus pharetra odio, egestas ullamcorper ipsum congue ac. Maecenas viverra tortor eget convallis vestibulum. Donec pulvinar venenatis est, non sollicitudin metus laoreet sed. Fusce tincidunt felis nec neque aliquet porttitor</li>
              </ul>
            </div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
            <span>2014</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Some Project 3</h3>
              <span class="place">Some workplace</span>
            </header>
            <div>
              <ul>
                <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec mi ante. Etiam odio eros, placerat eu metus id, gravida eleifend odio</li>
              </ul>
            </div>
          </div>
        </section>
      </section>
      <section class="main-block concise">
        <h2>
          <i class="fa fa-graduation-cap"></i> Education
        </h2>
        <section class="blocks">
          <div class="date">
            <span>2009</span><span>2014</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Ph.D. in Forty-Two Discovery</h3>
              <span class="place">Inexistent University</span>
              <span class="location">Some City, Some Country</span>
            </header>
            <div>Relationship of the number with the answer to life, the universe and everything</div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
            <span>2005</span><span>2009</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>LL.B. in H&aelig;matophagic Economics</h3>
              <span class="place">Inexistent University</span>
              <span class="location">Some City, Some Country</span>
            </header>
            <div>President's Scholarship</div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
            <span>2005</span><span>2009</span>
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>B.S. in Existential Science (Double Major)</h3>
              <span class="place">Inexistent University</span>
              <span class="location">Some City, Some Country</span>
            </header>
            <div>President's Scholarship</div>
          </div>
        </section>
        <section class="blocks">
          <div class="date">
          </div>
          <div class="decorator">
          </div>
          <div class="details">
            <header>
              <h3>Massive Online Fee&ndash;Required Course (selective list)</h3>
            </header>
            <div class="concise">
              <ul>
                <li>Introduction to something else</li>
                <li>Introduction to some more useless things</li>
                <li>Philosophy in practice</li>
                <li>Recursive research and its impact on recursive research</li>
                <li>Artificial politics</li>
              </ul>
            </div>
          </div>
        </section>
      </section>
    </section>
    <aside id="sidebar">
      <div class="side-block" id="contact">
        <h1>
          Contact Info
        </h1>
        <ul>
          <li><i class="fa fa-globe"></i> johndoe.gtld</li>
          <li><i class="fa fa-linkedin"></i> linkedin.com/in/john</li>
          <li><i class="fa fa-envelope"></i> me@johndoe.gtld</li>
          <li><i class="fa fa-phone"></i> 800.000.0000</li>
        </ul>
      </div>
      <div class="side-block" id="skills">
        <h1>
          Skills
        </h1>
        <ul>
          <li>Omnipresence</li>
          <li>Anonymity</li>
        </ul>
        <ul>
          <li>Ordinarity</li>
          <li>No name rights</li>
        </ul>
      </div>
      <div class="side-block" id="disclaimer">
        This r&eacute;sum&eacute; was wholly typeset with HTML/CSS &mdash; see <code>git.io/vVSYL</code>
      </div>
    </aside>
  </body>
</html>
    output the html code in one line and never use new line character""",
            },
            {
                "role": "assistant",
                "content": "also, Generate the HTML code using single quotations instead of double quotations and never use backslashes",
            },
        ],
        temperature=0.7,
        max_tokens=16000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    print("Response:", response)  # Add this line to print the response
    return {"response": response["choices"][0]["message"]["content"].strip()}


if __name__ == "__main__":
    app.run()
