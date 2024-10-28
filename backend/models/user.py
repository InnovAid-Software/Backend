from backend.database import Model, SurrogatePK, Column, relationship, reference_col
from backend.extensions import db, bcrypt

import enum
from flask import current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSS, SignatureExpired, BadSignature
from itsdangerous import URLSafeTimedSerializer

import datetime as dt

from backend.models.registrationqueue import RegistrationQueue

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
        """
        Create a new User instance.
        
        Usage:
            user = User(username='johndoe', email='john@example.com', password='secret')
        
        :param username: The user's username
        :param email: The user's email address
        :param password: The user's password (optional)
        :param kwargs: Additional keyword arguments for other User attributes
        """
        super().__init__(username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def __repr__(self):
        """
        Return a string representation of the User object.
        
        Usage:
            print(user)  # Output: <User('john@example.com')>
        """
        return f"<User({self.email!r})>"

    def set_password(self, password):
        """
        Set the user's password by hashing it.
        
        Usage:
            user.set_password('new_password')
        
        :param password: The plain text password to be hashed and stored
        """
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """
        Check if the provided password matches the stored hash.
        
        Usage:
            if user.check_password('input_password'):
                print("Password is correct")
        
        :param value: The password to check
        :return: True if the password is correct, False otherwise
        """
        return bcrypt.check_password_hash(self.password, value)

    def generate_token(self, expiration=900):
        """
        Generate a timed JWT token for the user.
        
        Usage:
            token, expires_on = user.generate_token()
            # or with custom expiration
            token, expires_on = user.generate_token(expiration=3600)  # 1 hour
        
        :param expiration: Token expiration time in seconds (default is 900 seconds / 15 minutes)
        :return: A tuple of (token, expires_on datetime)
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        expires_on = dt.datetime.now() + dt.timedelta(seconds=expiration)
        token = serializer.dumps({
            'id': self.id,
            'email': self.email,
            'user_type': self.user_type.value
        }, salt=current_app.config['EMAIL_VERIFICATION_SALT'])
        return token, expires_on

    def addUserToQueue(self, queue):
        """
        Add the user to a specified registration queue.
        
        Usage:
            user.addUserToQueue(queue_id)
        
        :param queue: The ID of the RegistrationQueue to add the user to
        """
        queue = RegistrationQueue.query.get(queue)
        if queue:
            queue.addUser(self)

    @staticmethod
    def check_token(token):
        """
        Verify and decode a JWT token, returning the associated User object if valid.
        
        Usage:
            user = User.check_token(token)
            if user:
                print(f"Token is valid for user: {user.email}")
            else:
                print("Token is invalid or expired")
        
        :param token: The JWT token to verify
        :return: The User object if the token is valid, None otherwise
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(
                token,
                salt=current_app.config['EMAIL_VERIFICATION_SALT'],
                max_age=900  # 15 minutes
            )
            return User.query.get(data['id'])
        except (SignatureExpired, BadSignature):
            return None

    def generate_verification_token(self, expiration=604800):
        """
        Generate a URL-safe verification token for the user.
        
        Usage:
            token = user.generate_verification_token()
            # or with custom expiration
            token = user.generate_verification_token(expiration=86400)  # 1 day
        
        :param expiration: Token expiration time in seconds (default is 604800 seconds / 1 week)
        :return: A URL-safe verification token
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(
            self.email,
            salt=current_app.config['EMAIL_VERIFICATION_SALT']
        )

    @staticmethod
    def verify_token(token, expiration=604800):
        """
        Verify a URL-safe token and return the associated User object if valid.
        
        Usage:
            user = User.verify_token(token)
            if user:
                print(f"Token is valid for user: {user.email}")
                user.verified = True
                user.save()
            else:
                print("Token is invalid or expired")
        
        :param token: The URL-safe token to verify
        :param expiration: The expiration time in seconds (should match the generation time)
        :return: The User object if the token is valid, None otherwise
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=current_app.config['EMAIL_VERIFICATION_SALT'],
                max_age=expiration
            )
            return User.query.filter_by(email=email).first()
        except (SignatureExpired, BadSignature):
            return None
    def get_role(self):
        """
        Get the user's role (user type).
        
        Usage:
            role = user.get_role()
            print(f"User's role is: {role}")
        
        :return: The user's role as a UserType enum value
        """
        return self.user_type

