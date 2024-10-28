from flask import Blueprint, request, jsonify, current_app
from backend.models.user import User, UserType
from backend.models.registrationqueue import RegistrationQueue
from backend.extensions import db, mail
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

bp = Blueprint('user', __name__)
bcrypt = Bcrypt()

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token, expires_on = user.generate_token()
        return jsonify({'token': token.decode('utf-8'), 'expires_on': expires_on, 'role': user.get_role()}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], email=data['email'], password=hashed_password, user_type=UserType(data['user_type']))
    db.session.add(user)
    db.session.commit()

    if user.user_type in [UserType.ADMIN, UserType.ROOT]:
        queue = RegistrationQueue(user=user, request_type=user.user_type)
        db.session.add(queue)
        db.session.commit()
        return jsonify({'message': 'User added to verification queue'}), 201
    else:
        verification_token = user.generate_verification_token()
        try:
            send_verification_email(user.email, verification_token)
            return jsonify({'message': 'Verification email sent'}), 201
        except Exception as e:
            # Log the error
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            return jsonify({'message': 'User registered but failed to send verification email'}), 500

@bp.route('/verify/<token>', methods=['GET'])
def verify(token):
    user = User.verify_token(token)
    if user:
        user.verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    return jsonify({'message': 'Invalid or expired token'}), 400


def send_verification_email(email, token):
    """
    Send a verification email to the user.
    
    :param email: The recipient's email address
    :param token: The verification token
    """
    verification_url = f'http://innovaid.dev/verify/{token}'
    msg = Message(
        'Please check your email for a verification link.',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f'Click the link to verify your email: {verification_url}'
    mail.send(msg)
    print(f"Verification email sent to {email}")
