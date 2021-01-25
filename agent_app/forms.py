# Importing Require Module

from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField

from wtforms.validators import DataRequired

# Creating Login Form contains email and password
class LoginForm(Form):
    email = StringField("Email", validators=[validators.Length(min=7, max=50), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])

# Creating Registration Form contains username, name, email, password and confirm password.

class RegisterForm(Form):

    name = StringField("Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address")])
    age = IntegerField("Age", validators=[ validators.DataRequired(message="Please Fill This Field")])
    gender = StringField("Gender", validators=[validators.Length(min=1, max=3), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[

        validators.DataRequired(message="Please Fill This Field"),
        validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
    ])

    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")])

class UserHealthForm(Form):
    temperature = IntegerField("Temperature", validators=[ validators.DataRequired(message="Please Fill This Field")])
    pressure = IntegerField("Pressure", validators=[ validators.DataRequired(message="Please Fill This Field")]) 
    heartbeat = IntegerField("Heartbeat", validators=[ validators.DataRequired(message="Please Fill This Field")])
    weight = IntegerField("Weight", validators=[ validators.DataRequired(message="Please Fill This Field")])
    hight = IntegerField("Hight", validators=[ validators.DataRequired(message="Please Fill This Field")])