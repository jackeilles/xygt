from app import app, worker
from config import Config, Errors
from flask import render_template, request, send_file
import os
import io
import random
import magic

@app.route('/', methods=["GET", "POST"])
def index():
    
    # Check for a GET or POST request
    if request.method == "GET":
        return render_template('index.html')

    elif request.method == "POST":

        # Before anything else, we want to take the IP if the logging is enabled
        if Config.ipLogEnabled == True:
            ip = request.remote_addr
        else:
            # If not then return a 0
            ip = 0

        # Init variables before they're passed
        userid = request.form.get("userid") if request.form.get("userid") else None
        filename = request.form.get("filename") if request.form.get("filename") else None
        retention = request.form.get("retention") if request.form.get("retention") else None
        id = request.form.get("filename") if Config.files.find_one({"id": filename}) is None else None

        # We got a file or a url?
        if 'file' in request.files:

            # Grab the file and store it, this is a FileStorage object
            file = request.files['file']

            # Call the function to upload the file, this will return either HTTP Status codes or a 200 with a URL.
            result, status = worker.uploadFile(file, ip, userid, filename, id, retention)

            result = "https://xygt.cc/{}".format(result)

            return result, status

        elif 'url' in request.form:
            result, status = worker.shortURL(url, ip, userid, id, retention)

@app.route('/<id>')
def getData(id):

    # Does it exist in the files DB?
    if Config.files.find_one({"id": id}) is not None:
        data = Config.files.find_one({"id": id})

        with open(os.path.join(Config.fileDir, id), "rb") as f:
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