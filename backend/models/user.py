from backend.database import Model, SurrogatePK, Column, relationship, reference_col
from backend.extensions import db, bcrypt

import enum
from flask import current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSS, SignatureExpired, BadSignature

import datetime as dt

class UserType(enum.Enum):
    STUDENT = "STUDENT"
    ROOT = "ROOT"
    ADMIN = "ADMIN"


class User(Model, SurrogatePK):

    email = Column(db.String(80), unique=True, nullable=False, isPrivate=True)
    password = Column(db.LargeBinary(128), nullable=True, isInternal=True)
    verified = Column(db.Boolean(), default=False)
    user_type = Column(db.Enum(UserType), nullable=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        super().__init__(username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def __repr__(self):
        return f"<User({self.email!r})>"

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def generate_token(self, expiration=900):

        expires_on = dt.datetime.now() + dt.timedelta(seconds=expiration)
        serializer = TJWSS(current_app.config['SECRET_KEY'], expires_in=expiration)
        token = serializer.dumps({
                'id': self.id,
                'email': self.email,
                'user_type': self.user_type
            })
        return token, expires_on

    def addUserToQueue(self, queue):
        queue = RegistrationQueue.query.get(queue)
        if queue:
            queue.addUser(self)

    @staticmethod
    def check_token(token):
        serializer = TJWSS(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None  # token has expired or is invalid

        # Since the token contains the user id, we can load the object and return it
        user = User.query.get(data['id'])
        return user