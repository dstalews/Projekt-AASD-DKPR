# Importing require libraries
from flask import Flask, render_template, flash, redirect, request, session, logging, url_for

from flask_sqlalchemy import SQLAlchemy

from forms import LoginForm, RegisterForm, UserHealthForm
from wtforms import Form
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.ext.sqlalchemy.fields import QuerySelectField
# Now create flask application object
import subprocess
import shlex
from flask_script import Manager, Server
from main import run, run_agent, run_agent_start
from flask import request, jsonify

app = Flask(__name__)
manager = Manager(app)
# Database Configuration and Creating object of SQLAlchemy

app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/aasd'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create User Model which contains id [Auto Generated], name, username, email and password

class User(db.Model):

    __tablename__ = 'usertable'

    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(15), unique=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    gender = db.Column(db.String(2))    
    password = db.Column(db.String(256), unique=True)
    userhealth = db.relationship('UserHealth', backref='usertable', lazy=True)
    useraction = db.relationship('UserAction', backref='usertable', lazy=True)

class UserHealth(db.Model):

    __tablename__ = 'userhealthtable'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('usertable.id'))
    temperature = db.Column(db.Float)
    pressure = db.Column(db.Integer)
    heartbeat = db.Column(db.Integer)
    weight = db.Column(db.Integer)    
    hight = db.Column(db.Integer)
    age = db.Column(db.Integer)
    time = db.Column(db.DateTime, server_default=db.func.now())

class UserAction(db.Model):
    __tablename__ = 'useractiontable'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('usertable.id'))
    statusID = db.Column(db.Integer, db.ForeignKey('statustable.id'))
    actionID = db.Column(db.Integer, db.ForeignKey('actiontable.id'))
    time = db.Column(db.DateTime, server_default=db.func.now())
    
class Status(db.Model):
    __tablename__ = 'statustable'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(255), unique=True)


class Action(db.Model):
    __tablename__ = 'actiontable'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), unique=True)

@app.route('/')
def home():
    return render_template('index.html')

# User Registration Api End Point
@app.route('/register/', methods = ['GET', 'POST'])
def register():
    # Creating RegistrationForm class object
    form = RegisterForm(request.form)

    # Cheking that method is post and form is valid or not.
    if request.method == 'POST' and form.validate():
        # if all is fine, generate hashed paWssword
        hashed_password = generate_password_hash(form.password.data, method='sha256')

        # create new user model object
        new_user = User(
            name = form.name.data, 
            username = form.username.data, 
            email = form.email.data, 
            gender = form.gender.data,
            password = hashed_password )

        # saving user object into data base with hashed password
        db.session.add(new_user)
        db.session.commit()

        flash('You have successfully registered', 'success')

        new_userhealth = UserHealth(
            userID = new_user.id,
            temperature = 0 ,
            pressure = 0,
            heartbeat = 0,
            weight = 0 ,
            hight = 0,
            age = 0
        )

        db.session.add(new_userhealth)
        db.session.commit()

        flash('You have successfully added healthstatus', 'success')

        subprocess.call(shlex.split(f'./register.sh {new_user.id} {new_user.password}'))
        user = {'id' : new_user.id, 'password': new_user.password}
        run_agent_start(user)

        # if registration successful, then redirecting to login Api
        return redirect(url_for('login'))

    else:

        # if method is Get, than render registration form
        return render_template('register.html', form = form)

# Login API endpoint implementation
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    # Creating Login form object
    form = LoginForm(request.form)
    # verifying that method is post and form is valid
    if request.method == 'POST' and form.validate:
        # checking that user is exist or not by email
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            # if user exist in database than we will compare our database hased password and password come from login form 
            if check_password_hash(user.password, form.password.data):
                # if password is matched, allow user to access and save email and username inside the session
                flash('You have successfully logged in.', "success")

                session['logged_in'] = True

                session['id'] = user.id
                session['email'] = user.email   
                session['username'] = user.username

                health = UserHealth.query.filter_by(userID = user.id).order_by(UserHealth.time.desc()).first()

                session['temperature'] = health.temperature
                session['pressure'] = health.pressure
                session['heartbeat'] = health.heartbeat
                session['weight'] = health.weight
                session['hight'] = health.hight
                session['time'] = health.time
                session['age'] = health.age

                # After successful login, redirecting to home page
                return redirect(url_for('home'))

            else:

                # if password is in correct , redirect to login page
                flash('Username or Password Incorrect', "Danger")

                return redirect(url_for('login'))
    # rendering login page
    return render_template('login.html', form = form)

from wtforms import fields

class StatusForm(Form):
    action = fields.StringField('Action', render_kw={'readonly': True})
    status = fields.StringField('Current Status', render_kw={'readonly': True})
    update_status = QuerySelectField('Current Status', query_factory=lambda: Status.query.all())

# Login API endpoint implementation
@app.route('/action/', methods = ['GET', 'POST'])
def action():
    # Creating UserHealthForm form object

    useractions = UserAction.query.filter_by(userID = session['id']).filter(UserAction.statusID != 3)
    a = []
    for useraction in useractions:
        status = Status.query.filter_by(id = useraction.statusID).first()
        action = Action.query.filter_by(id = useraction.actionID).first()
        a.append({'useractionID':useraction.id,'status':status.status,'action':action.action})
    
    if request.method == 'POST':
        
        for id, status in request.form.items():
            if status != 'not-completed':
                useraction = UserAction.query.filter_by(id = id).first()
                status = Status.query.filter_by(status = status).first()
                useraction.statusID = status.id
                db.session.commit()
                flash('You have successfully udpate action status.', "success")

        a = []
        for useraction in useractions:
            status = Status.query.filter_by(id = useraction.statusID).first()
            action = Action.query.filter_by(id = useraction.actionID).first()
            a.append({'useractionID':useraction.id,'status':status.status,'action':action.action})
        status = Status.query.filter(Status.status !='not-completed').all()
        return render_template('action.html',actions=a,status=status)

        # return redirect(url_for('home'))
    # rendering login page
    status = Status.query.filter(Status.status !='not-completed').all()
    print(status)
    return render_template('action.html',actions=a,status=status)

# Login API endpoint implementation
@app.route('/update/', methods = ['GET', 'POST'])
def update():
    # Creating UserHealthForm form object
    print(session['id'], flush=True)
    form = UserHealthForm(request.form)
    id = session['id']
    # verifying that method is post and form is valid
    if request.method == 'POST' and form.validate:
        # checking that user is exist or not by email

        session['temperature'] = form.temperature.data
        session['pressure'] = form.pressure.data
        session['heartbeat'] = form.heartbeat.data
        session['weight'] = form.weight.data
        session['hight'] = form.hight.data
        session['age'] = form.age.data

        new_userhealth = UserHealth(
            userID = session['id'],
            temperature = form.temperature.data ,
            pressure = form.pressure.data,
            heartbeat = form.heartbeat.data,
            weight = form.weight.data ,
            hight = form.hight.data,
            age = form.age.data
        )

        db.session.add(new_userhealth)
        db.session.commit()

        flash('You have successfully udpate health status.', "success")

        return redirect(url_for('home'))
    # rendering login page
    return render_template('update.html', form = form)

@app.route('/api/v1/resources/users/all', methods=['GET'])
def api_all():
    result = []
    users = User.query.all()
    for user in users:
        userhealth = UserHealth.query.filter_by(userID = user.id).order_by(UserHealth.time.desc()).first()
        data = {
        'id' : user.id ,
        'gender' : user.gender,
        'temperature' : userhealth.temperature,
	    'pressure' : userhealth.pressure,
	    'heartbeat' : userhealth.heartbeat,	
	    'weight' : userhealth.weight,
	    'hight' : userhealth.hight,
        'age' : userhealth.age 
        }
        result.append(data)
    return jsonify(result)

@app.route('/api/v1/resources/users', methods=['GET'])
def api_id():

    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    userhealth = UserHealth.query.filter_by(userID = id).order_by(UserHealth.time.desc()).first()
    user = User.query.filter_by(id = id).first()
    data = {
    'id' : user.id ,
    'gender' : user.gender,
    'temperature' : userhealth.temperature,
    'pressure' : userhealth.pressure,
    'heartbeat' : userhealth.heartbeat,	
    'weight' : userhealth.weight,
    'age' : userhealth.age ,
    'hight' : userhealth.hight
    }
    return jsonify(data)

@app.route('/logout/')
def logout():
    # Removing data from session by setting logged_flag to False.
    session['logged_in'] = False
    # redirecting to home page
    return redirect(url_for('home'))

users = User.query.all()
users = [{'id' : u.id, 'password' : u.password} for u in users]

manager.add_command('runserver', run(users))

if __name__ == '__main__':
    # Creating database tables

    db.create_all()

    # running server
    app.run(debug=True)