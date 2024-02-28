from config import disallowedMimeTypes, Errors, Config
from app.models import User
from app import bcrypt
import secrets
import datetime
import random
import magic
import os

def uploadFile(file, ip, userid, filename, id, retention):

    # Is the MIME and file size good? 
    file_content = file.read()
    if magic.from_buffer(file_content, mime=True) not in disallowedMimeTypes:
        if file.content_length <= Config.maxFileSize:
            # We're going to check whether the id variable has been filled

            while True:                 # Loop to find an available file ID
                id = randomHex()        # Prevent conflicts if 2 of the same get made
                if Config.files.find_one({'id': id}) is None:
                    filename=id
                    break

            if userid == None:
                userid = 0
            elif Config.users.find_one({'userid': userid}) == None:
                userid = 0

            # Calculate retention before the file is written, we'll grab the filesize here as it's needed for the equation.
            file.seek(0, os.SEEK_END)
            fileSize = round(float(file.tell()) / (1024 * 1024), 2)
            
            # Set the position back to 0
            file.seek(0)

            if retention == None:
                retention = (Config.minretention+(-Config.maxretention + Config.minretention)*pow((fileSize / Config.maxFileSize -1), 3))
            elif retention > (Config.minretention+(-Config.maxretention + Config.minretention)*pow((fileSize / Config.maxFileSize -1), 3)):
                retention = (Config.minretention+(-Config.maxretention + Config.minretention)*pow((fileSize / Config.maxFileSize -1), 3))
            else:
                retention = retention
        
            
            # Create the file
            with open(f"{os.path.abspath(Config.fileDir)}/{filename}", "wb") as f:
                f.write(file.read())

            timestamp = datetime.datetime.now()
            timestamp = timestamp.timestamp()

            # Create the dictionary that we'll insert into the db
            data = {
                'id': id,
                'filename': filename,
                'filesize': fileSize,
                'mimetype': magic.from_buffer(file_content, mime=True) if magic.from_buffer(file_content, mime=True) != None else "text/plain",
                'retention': retention,
                'userid': userid,
                'ip': ip,
                'date': timestamp,
                'expiry': timestamp + retention
            }

            # Add the data and verify its there.
            Config.files.insert_one(data)
            print(Config.files.find_one({"id": id}))

            return f"https://xygt.cc/{id}", 200
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
        retention = 604800
    elif retention > 31540000:
        retention = 31540000

    timestamp = datetime.datetime.now()
    timestamp = timestamp.timestamp()    

    data = {
        'id': id,
        'url': url,
        'retention': retention,
        'userid': userid,
        'ip': ip,
        'date': timestamp,
        'expiry': timestamp + retention
    }

    Config.url.insert_one(data)
    print(Config.url.find_one({"id": data["id"]}))

    return f"https://xygt.cc/{id}", 200

def idInfo(id, cred):
    # Check if cred is true
    if cred:
        # Check files and url for the ID
        if Config.files.find_one({"id": id}) is not None:
            check = Config.files.find_one({"id": id}, {'_id': False})

        # If it's not there then check url
        elif Config.url.find_one({"id": id}) is not None:
            check = Config.url.find_one({"id": id}, {'_id': False}) 

        # Return the mongodb info about the file
        return check
    else:
        # Check files and url for the ID
        if Config.files.find_one({"id": id}) is not None:
            check = Config.files.find_one({"id": id}, {'_id': False, "ip": False, "userid": False})
        # If it's not there then check url
        elif Config.url.find_one({"id": id}) is not None:
            check = Config.url.find_one({"id": id}, {'_id': False, "ip": False, "userid": False}) 

        # Return the mongodb info about the file
        return check

def userInfo(id):
    # Grab user entry from userID
    user = Config.users.find_one({"userid": id})
    print(user)

    username = user['user']
    userid = id

    # Search for all files from that userID
    files = Config.files.find({"userid": userid}, {"_id": False, "ip": False})
    print(files)
    list = {}

    # Create file listing
    for file in files:
        list.update({
            file["id"]: {
                "filename": file["filename"],
                "mimetype": file["mimetype"],
                "filesize": file["filesize"],
                "retention": file["retention"],
                "creation": file["date"],
                "expiry": file["expiry"]
            }
        })

    # Search for all URL's from that userID
    url = Config.url.find({"userid": userid})

    # Format all into one JSON
    return {
        "user": {
            "username": username,
            "userid": userid 
        },
        "files": {
            "count": len(files),
            "list": list
            }
        }

def randomHex():
    hexRand = ''.join(secrets.choice('0123456789abcdef') for _ in range(6))
    return hexRand

def genIDPass():
    idpass = ''.join(secrets.choice('0123456789abcdef') for _ in range(16))
    return idpass

def registerUser(username, password):
    # Initialise some values
    try:
        level = 1
        while True:
            userid = randomHex()
            if Config.users.find_one({"userid": userid}) is None:
                break
        idpass = bcrypt.generate_password_hash(randomHex()).decode("utf-8") # The user will not know this, they'll need to generate a new one.
        password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username, userid, password, idpass, level)
        Config.users.insert_one(user.__dict__)

        return True
    except:
        return False
    
def resetIDPass(userid):
    try:
        idpass = genIDPass()
        hashedPass = bcrypt.generate_password_hash(idpass).decode("utf-8")
        Config.users.update_one({"userid": userid}, {"$set": {"idpass": hashedPass}})
        return idpass
    except:
        return False 
