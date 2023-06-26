# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Import classes from chatbot folder
from model.chatbot.chatBot import ChatBot
from model.chatbot.similarity import Similarity

# Flask app
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


# Construct the path for the desired database location
db_path = os.path.join(script_dir, 'instance', 'dev.sqlite3')

app = Flask(__name__)

chatupm = ChatBot()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] =  os.environ['JWT_SECRET_KEY'] #generated with secrets.token_hex(64)
app.config["SECRET_KEY"] = os.environ['SECRET_KEY'] #generated with secrets.token_hex(64)
db = SQLAlchemy(app)

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
        new_user = User(username=username, password=generate_password_hash(password))
   
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


@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        user = current_user.username
        userText = request.form.get('msg')
        botText = chatupm.answer(userText)
        response = {'botText': botText,
                    'user': user}
        return jsonify(response)
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



#if __name__ == "__main__":
    #with app.app_context():
    #    db.create_all()
    
#    app.run(debug=False, port=5000, host="127.0.0.1", threaded=True)

