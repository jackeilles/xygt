#!/usr/bin/env python

"""
This is to only be used in the event of catastrophic failure where everything is basically fucked.
This wipes all files and DB entries for Files, URL's and users.
"""

import os
from pymongo import MongoClient

class Config:
    # MongoDB init stuff
    client = MongoClient("mongodb://localhost:27017/")
    db = client["xygt"]
    files = db["file"]
    url = db["url"]
    users = db["users"]
    fileDir = "./data"

def main():
    # Start
    conf1 = input("This will irrevocably remove ALL DATA from xygt.cc, are you sure you'd like to proceed. (Type this w.o quotes 'Yes I would like to proceed')")
    if conf1 == "Yes I would like to proceed":
        conf2 = input("Are you definitely sure? (y/n)").lower()
        if conf2 == "y":
            print("WIPING ALL DATA.\n\n")
            print("Clearing files db")
            Config.files.delete_many({})
            print("Clearing url db")
            Config.url.delete_many({})
            print("Clearing user db")
            Config.url.delete_many({})
            print("Deleting local files")
            os.remove(f"{Config.fileDir}/*")
            print("Done. xygt.cc is ready to start clean.")
            exit()

# UNCOMMENT TO RUN!!!
if __name__ == "__main__":
    main()
