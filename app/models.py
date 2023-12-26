from flask_login import UserMixin
from config import Config

class User(UserMixin):
    def __init__(self, user, userid, password, idpass, level):
        self.user = user
        self.password = password
        self.userid = userid
        self.idpass = idpass
        self.level = level

    def __repr__(self):
        return f"User('{self.user}', '{self.userid}', '{self.password}', '{self.idpass}', '{self.level}')"

    def get_id(self):
        return str(self.userid)
    
    def get(userid):
        userData = Config.users.find_one({"userid": userid})
        if not userData:
            return None
        else:
            return User(userData["user"], userData["userid"], userData["password"], userData["idpass"], userData["level"])