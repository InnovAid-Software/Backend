from enum import Enum

class UserType(Enum):
    student = 1
    admin = 2
    root = 3

class SSPUser:

    def __init__(self, userid, email, password, usertype):
        self.email = email
        self.password = password
        self.usertype = usertype
        #the ID of the user might be able to be simplified as just the email for the key.
        self.userid = userid

    #methods
