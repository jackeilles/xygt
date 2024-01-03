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
from config import Config, Errors

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
        print(current_user.is_authenticated)
        return render_template('index.html')

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

            result = "https://xygt.cc/{}".format(result)

            return result, status

        elif 'file' in request.form:

            file = FileStorage(stream=BytesIO(request.form['file'].encode("utf-8")), filename=id, content_type="text/plain")

            result, status = worker.uploadFile(file, ip, userid, filename, id, retention)
            
            result = "https://xygt.cc/{}".format(result)

            return result, status

        elif 'url' in request.form:

            url = request.form['url']

            result, status = worker.shortenURL(url, ip, userid, id, retention)

            result = "https://xygt.cc/{}".format(result)

            return result, status

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tos')
def tos():
    return render_template('tos.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/transparency')
def transparency():
    return render_template('transparency.html')

@app.route('/transparency/public')
def public():
    return "Nothing here yet."

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

@app.route('/teapot')
def teapot():
    return 'I\'m a teapot. 418.', 418

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "GET":
            return render_template("register.html", form=RegistrationForm())
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
            return render_template("login.html", form=LoginForm())
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            userid = Config.users.find_one({"user": username})["userid"]
            user = User.get(userid)

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                print(current_user.is_authenticated)
                flash("Successfully logged in!", "success")
                return redirect("/")
            else:
                flash("Incorrect username or password.", "danger")
                return redirect("/login")
            
@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")