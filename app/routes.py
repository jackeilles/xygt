#!/usr/bin/env python3

"""
XYGT.CC - Routes
A no-bullshit, anonymous, temporary file host.
"""

import os
import io
import random
from io import BytesIO
import magic
from flask import render_template, request, send_file, redirect, flash
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app import app, worker, bcrypt, loginManager, csrf
from app.models import User
from config import Config, Errors, quotes

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=32)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    tnc = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Config.users.find_one({"username": username.data})
        if user:
            raise ValueError("That username is taken. Try another.")
        
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=32)])
    submit = SubmitField('Login')

@loginManager.user_loader
def load_user(userid):
    user = User.get(userid)
    return user

@csrf.exempt
@app.route('/', methods=["GET", "POST"])
def index():
    
    # Check for a GET or POST request
    if request.method == "GET":
        randomQuote = random.choice(list(quotes.items()))
        author = randomQuote[0]
        quote = randomQuote[1]
        return render_template('index.html', author=author, quote=quote, title="Home")

    elif request.method == "POST":

        # Before anything else, we want to take the IP if the logging is enabled
        if Config.ipLogEnabled:
            ip = request.remote_addr
        else:
            # If not then return a 0
            ip = 0

        # Init variables before they're passed
        userid = request.form.get("userid") if request.form.get("userid") else None
        filename = request.form.get("filename") if request.form.get("filename") else None
        retention = int(request.form.get("retention")) if request.form.get("retention") else None
        id = request.form.get("filename") if Config.files.find_one({"id": filename}) is None else None

        # We got a file or a url?
        if 'file' in request.files:

            # Grab the file and store it, this is a FileStorage object
            file = request.files['file']

            # Call the function to upload the file, this will return either HTTP Status codes or a 200 with a URL.
            result, status = worker.uploadFile(file, ip, userid, filename, id, retention)

            return result, status

        elif 'file' in request.form:

            file = FileStorage(stream=BytesIO(request.form['file'].encode("utf-8")), filename=id, content_type="text/plain")

            result, status = worker.uploadFile(file, ip, userid, filename, id, retention)

            return result, status

        elif 'url' in request.form:

            url = request.form['url']

            result, status = worker.shortenURL(url, ip, userid, id, retention)

            return result, status

@app.route('/about')
def about():
    return render_template('about.html', title="About")

@app.route('/tos')
def tos():
    return render_template('tos.html', title="Terms of Service")

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', title="Privacy Policy")

@app.route('/faq')
def faq():
    return render_template('faq.html', title="FAQ")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact")

@app.route('/transparency')
def transparency():
    return render_template('transparency.html', title="Transparency Report")

@app.route('/transparency/public')
def public():
    return "Nothing here yet."

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', files=Config.files.find({"userid": current_user.userid}), urls=Config.url.find({"userid": current_user.userid}), title="Dashboard")

@app.route('/<id>')
def getData(id):

    # Does it exist in the files DB?
    if Config.files.find_one({"id": id}) is not None:
        data = Config.files.find_one({"id": id})

        with open(os.path.join(Config.fileDir, secure_filename(id)), "rb") as f:
            file = f.read()

        # Get MIME type from file, if fails then use magic
        try:
            mimetype = data["mimetype"]
        except KeyError:
            mimetype = magic.from_buffer(file, mime=True)

        # Return the file with the correct MIME type
        return send_file(io.BytesIO(file), mimetype=mimetype)

    # If not then check the URL Shortening DB
    elif Config.url.find_one({"id": id}) is not None:
        data = Config.url.find_one({"id": id})

        return redirect(data["url"])

    else:
        return random.choice(Errors.file404)

@app.route('/<id>/info')
def getInfo(id):

    return worker.idInfo(id)

@csrf.exempt
@app.route('/<id>/delete', methods=["POST"])
@login_required
def delete(id):
    if Config.files.find_one({"id": id}) is not None:

        data = Config.files.find_one({"id": id})
        
        if data["userid"] == current_user.userid:
            Config.files.delete_one({"id": id})
            os.remove(os.path.join(Config.fileDir, secure_filename(id)))
            return "File deleted."
        
        elif data["userid"] == request.form.get("userid") and bcrypt.check_password_hash(Config.user.find_one({"userid": data["userid"]})["idpass"], request.form.get("idpass")):
            Config.files.delete_one({"id": id})
            os.remove(os.path.join(Config.fileDir, secure_filename(id)))
            return "File deleted."
        
        else:
            return "You are not the owner of this file."

    elif Config.url.find_one({"id": id}) is not None:

        data = Config.url.find_one({"id": id})

        if data["userid"] == current_user.userid:
            Config.files.delete_one({"id": id})
            return "URL deleted."
        
        elif data["userid"] == request.form.get("userid") and bcrypt.check_password_hash(Config.user.find_one({"userid": data["userid"]})["idpass"], request.form.get("idpass")):
            Config.files.delete_one({"id": id})
            return "URL deleted."
        
        else:
            return "You are not the owner of this link."
    
    else:
        return "This ID does not exist."

@app.route('/teapot')
def teapot():
    return 'I\'m a teapot. 418.', 418

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "GET":
            return render_template("register.html", form=RegistrationForm(), title="Register")
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            res = worker.registerUser(username, password)

            if res == True:
                flash("Successfully registered!", "success")
                return redirect("/login")
            else:
                flash("Something went wrong, sorry.", "danger")
                return redirect("/register")

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "GET":
            return render_template("login.html", form=LoginForm(), title="Login")
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            userid = Config.users.find_one({"user": username})["userid"]
            user = User.get(userid)

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash("Successfully logged in!", "success")
                return redirect("/")
            else:
                flash("Incorrect username or password.", "danger")
                return redirect("/login")
            
@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

@app.route('/resetidpass')
def resetidpass():
    idpass = worker.resetIDPass(current_user.userid)
    if idpass == False:
        return "Something went wrong, sorry. Please try again."
    else:
        return f"Your new IDPass is \n {idpass}\n This will only be shown once, please save it somewhere safe."


@app.errorhandler(404)
def page_not_found(e):
    return random.choice(Errors.file404), 404