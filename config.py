from pymongo import MongoClient
import random

class Config:
    # MongoDB init stuff
    client = MongoClient("mongodb://localhost:27017/")
    db = client["xygt"]
    files = db["file"]
    url = db["url"]
    users = db["users"]

    # Basic configs
    maxFileSize = 256
    premMaxFileSize = 512
    maxretention = 365
    minretention = 7
    fileDir = "./data"
    ipLogEnabled = False
    secretKey = "CHANGEINPRODUCTION"

quotes = {
    "Anon /g/": "Biometrics are shit, you lose a limb and you're fucked.",
    "Jack": "i named it xygt because it sounds cool lmao",
    "Cow": "Does this server run Gentoo? (no it doesn't)",
    "uname -a": "Linux xygt 6.1.0-12-arm64 #1 SMP Debian 6.1.52-1 (2023-09-07) aarch64 GNU/Linux",
    "Luna": "shit you moth",
    "Maze": "Mein Gott Leute, meine Mama hat mir einfach erlaubt dass ich Cola trinken darf! Wie cool ist das bitte? Jetzt zocke ich Fortnite und trinke Cola! YIPPEE!",
}

disallowedMimeTypes = [
    "application/x-dosexec",
    "application/java-archive",
    "application/java-vm"
]

class Errors:
    file404 = [
        "The file you seek does not exist...", 
        "Nope, can't find it.", 
        "AVE FOOKIN LOST IT", 
        "My shitty filehost can't find this, sorry lmao",
        "Your file could not be found.",
        "You fucked up somewhere, this link doesn't work.",
        "If someone gave you this link, go shout at them, it's broken.",
        "404.",
        "The file isn't in our db, so it's probably expired or just never existed in the first place."
    ]

    fileTooLarge = [
        "Too big, nah.",
        "File size goes over the limit, you're not uploading this"
        "Your file is too large, get it under 256mb first.",
        "I don't know what the hell you're trying to upload but it's over 256mb, so no.",
        "Your file is over 256mb, remember, we don't store your files forever!",
        "File is too big, 256mb is the limit.",
        "nuh uh, too big"
    ]

    fileTypeNotAllowed = [
        "Nice try idiot. You're not uploading that onto my server.",
        "No executables allowed, NO EXCEPTIONS.",
        "So bud... what you trying to do there? You can't upload executables you knob.",
        "Nah, not getting that on here today.",
        "Stop trying to upload executables, goddamnit.",
        "Executables can suck my dick, you're not uploading that"
        "nuh uh (executables not allowed)"
    ]

    def file404Error():
        return random.choice(self.file404.items())

    def fileTooLargeError():
        return random.choice(self.fileTooLarge.items())

    def fileTypeNotAllowedError():
        return random.choice(self.fileTypeNotAllowed.items())