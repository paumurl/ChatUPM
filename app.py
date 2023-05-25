from chatbot.chatBot import chatBot
from chatbot.similarity import similarity

# OTHER DEPENDENCIES
# For the scraping
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin
import lxml

# To convert pdfs to text
import PyPDF2
import io
import os

# Text wrangling
import pandas as pd
import numpy as np

# Time efficiency and optimization
import time
from concurrent.futures import ThreadPoolExecutor

# OpenAI access
import json
import openai

# To create new embeddings using convolutional networks
import tensorflow_hub as hub
import tensorflow_text

# Flask app
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, abort
import jinja2
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from django.utils.http import url_has_allowed_host_and_scheme
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sys

# Module management
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = 'b6b6ed9245db93cc393dbe62cca20781a45d10bd8315161e19b813200ef4dae6'
app.config["SECRET_KEY"] = "edb44a689a364929c455bc2bc0e3b65904ea26d3e2b051a8df2bce2c7fcf4dcd"
db = SQLAlchemy(app)
jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == user_id).first()

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chatbot'))

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('chatbot'))
        else:
            flash('El usuario y/o la contraseña son incorrectos. Revisa tus datos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # code to validate and add user to database goes here
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database
    
        if user:
            flash('Este nombre de usuario ya existe. Prueba con otro.')
            return redirect(url_for('signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
   
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/")
def home():
    auth_status = current_user.is_authenticated
    return render_template("index.html", auth_status=auth_status)


@app.route('/chatbot',  methods=['POST', 'GET'])
@login_required
def chatbot():
    # request.form.get('question')
    return render_template("chatbot.html")

@app.errorhandler(401)
def unauthorized(e):
    flash("Unauthorized access. Please log in.")
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return json.dumps({"Status": "The requested URL was not found on the server."}), 404

@app.errorhandler(500)
def page_not_found(e):
    return json.dumps({"Status": "Internal server error"}), 500



if __name__ == "__main__":
    #with app.app_context():
    #    db.create_all()
    #app.config['TIMEOUT'] = 300 # 5 minutes
    app.run(debug=True, port=5000, host="127.0.0.1", threaded=True)

