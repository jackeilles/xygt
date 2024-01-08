#!/usr/bin/env python

"""
xygt.cc cleanup script

This script will run once hourly to remove expired files and URL's from the database as well as local storage.
"""

import datetime
import os
from pymongo import MongoClient
from config import Config
import time

class Config:
    # MongoDB init stuff
    client = MongoClient("mongodb://localhost:27017/")
    db = client["xygt"]
    files = db["file"]
    url = db["url"]
    users = db["users"]
    fileDir = "./data"

def main():
    while True:
        print("Starting cleanup script...")

        # Get current time in unix timestamp
        now = datetime.datetime.now()
        now = now.timestamp()

        # Get all expired files
        expiredFiles = Config.files.find({"expiry": {"$lt": now}})
        expiredURLs = Config.url.find({"expiry": {"$lt": now}})

        # Delete all expired files
        for file in expiredFiles:
            print(f"Deleting file {file['id']}")
            Config.files.delete_one({"id": file["id"]})
            os.remove(os.path.join(Config.fileDir, file["filename"]))

        # Delete all expired URL's
        for urls in expiredURLs:
            print(f"Deleting URL {urls['id']}")
            Config.url.delete_one({"id": urls["id"]})

        print("Cleanup complete.")
        time.sleep(60)


if __name__ == "__main__":
    main()