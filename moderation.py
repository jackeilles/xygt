from pymongo import MongoClient
import datetime

class Config:
    # MongoDB init stuff
    client = MongoClient("mongodb://localhost:27017/")
    db = client["xygt"]
    files = db["file"]
    url = db["url"]
    users = db["users"]

    fileDir = "./data"

def main():
    # Grab everything from the past day
    now = datetime.datetime.now()
    now = now.timestamp()
    yesterday = now - 86400
    files = Config.files.find({'date': {'$gt': yesterday}}).sort('date', -1)
    urls = Config.url.find({'date': {'$gt': yesterday}}).sort('date', -1)

    print("Files:")
    for file in files:
        print(f"File ID: {file['id']}, UserID: {file['userid']}, File Name: {file['filename']}, File Size: {file['filesize']}, File Type: {file['mimetype']}")

    print("URLs:")
    for url in urls:
        print(f"URL ID: {url['id']}, UserID: {url['userid']}, URL: {url['url']}")

if __name__ == "__main__":
    main()