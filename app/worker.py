from config import disallowedMimeTypes, Errors, Config
from app.models import User
from app import bcrypt
import secrets
import datetime
import random
import time
import os

def uploadFile(file, ip, userid, filename, id, retention):

    # Is the MIME and file size good? 
    if file.content_type not in disallowedMimeTypes:
        if file.content_length <= Config.maxFileSize:
            # We're going to check whether the id variable has been filled

            while True:                 # Loop to find an available file ID
                id = randomHex()        # Prevent conflicts if 2 of the same get made
                if Config.files.find_one({'id': id}) is None:
                    filename = id
                    break

            if userid == None:
                userid = 0
            elif Config.users.find_one({'userid': userid}) == None:
                userid = 0

            # Calculate retention before the file is written, we'll grab the filesize here as it's needed for the equation.
            fileSize = round(float(file.content_length) / 1024, 2)

            if retention == None:
                retention = (Config.minretention+(-Config.maxretention + Config.minretention)*pow((fileSize / Config.maxFileSize -1), 3))
            elif retention > (Config.minretention+(-Config.maxretention + Config.minretention)*pow((fileSize / Config.maxFileSize -1), 3)):
                retention = (Config.minretention+(-Config.maxretention + Config.minretention)*pow((fileSize / Config.maxFileSize -1), 3))
        
            
            # Create the file
            with open(f"{os.path.abspath(Config.fileDir)}/{filename}", "wb") as f:
                f.write(file.read())

            date = time.mktime(datetime.datetime.now().timetuple())

            # Create the dictionary that we'll insert into the db
            data = {
                'id': id,
                'filename': filename,
                'filesize': fileSize,
                'retention': round(retention * 86400), # Convert to seconds
                'userid': userid,
                'ip': ip,
                'date': date,
                'expiry': date + round(retention * 86400)
            }

            # Add the data and verify its there.
            Config.files.insert_one(data)
            print(Config.files.find_one({"id": id}))

            return id, 200
        else:
            return random.choice(Errors.fileTooLarge), 400
    else:
        return random.choice(Errors.fileTypeNotAllowed), 400

def shortenURL(url, ip, userid, id, retention):
    # We're going to check whether the id variable has been filled
    # If not then we'll generate one. (The ID variable will be the same as the filename if not rejected earlier.)
    if id == None:
        while True:                 # Loop to find an available file ID
            id = randomHex()        # Prevent conflicts if 2 of the same get made
            if Config.files.find_one({'id': id}) is None:
                break

    if userid == None:
        userid = 0
    elif Config.users.find_one({'userid': userid}) == None:
        userid = 0

    if retention == None:
        retention = 14
    elif retention > 365:
        retention = 365
        
    data = {
        "id": id,
        "url": url,
        "userid": userid,
        "retention": retention,
        "ip": ip
    }

    Config.url.insert_one(data)
    print(Config.url.find_one({"id": data["id"]}))

    return id

def idInfo(id):
    # Check files and url for the ID
    if Config.files.find_one({"id": id}) is not None:
        check = Config.files.find_one({"id": id}, {'_id': False, "ip": False})
                                            # "ip": False removes the IP from the returned data.
    # If it's not there then check url
    elif Config.url.find_one({"id": id}) is not None:
        check = Config.url.find_one({"id": id}, {'_id': False, "ip": False}) 

    # Return the mongodb info about the file, removing IP if its present
    return check

def randomHex():
    hexRand = ''.join(secrets.choice('0123456789abcdef') for _ in range(6))
    return hexRand

def registerUser(username, password):
    # Initialise some values
    try:
        level = 1
        userid = randomHex()
        idpass = bcrypt.generate_password_hash(randomHex()).decode("utf-8")
        password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username, userid, password, idpass, level)
        Config.users.insert_one(user.__dict__)

        return True
    except:
        return False