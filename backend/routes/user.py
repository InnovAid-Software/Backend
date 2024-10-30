from flask import Blueprint, request, jsonify, current_app, redirect
from backend.models.user import User, UserType, RegistrationQueue, RequestType
from backend.extensions import db, mail, bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

bp = Blueprint('user', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']) and user.is_verified():
        token, expires_on = user.generate_token()
        return jsonify({'token': token, 'expires_on': str(expires_on), 'role': user.get_role().value}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        email=data['email'], 
        password=data['password'], 
        user_type=UserType(data['user_type'].upper())
    )
    db.session.add(user)
    db.session.commit()

    if user.user_type in [UserType.ADMIN, UserType.ROOT]:
        request_type = RequestType[user.user_type.name]
        queue = RegistrationQueue(user=user, request_type=request_type)
        db.session.add(queue)
        db.session.commit()
        return jsonify({'message': 'User added to verification queue'}), 201
    else:
        verification_token = user.generate_verification_token()
        try:
            send_verification_email(user.email, verification_token)
            return jsonify({'message': 'Verification email sent'}), 201
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            return jsonify({'message': 'User registered but failed to send verification email'}), 500

@bp.route('/verify/<token>', methods=['GET'])
def verify(token):
    user = User.verify_token(token)
    if user:
        user.verified = True
        db.session.commit()
        return redirect('https://innovaid.dev')
    return jsonify({'message': 'Invalid or expired token'}), 400


def send_verification_email(email, token):
    """
    Send a verification email to the user.
    
    :param email: The recipient's email address
    :param token: The verification token
    """
    verification_url = f'http://innovaid.dev/api/user/verify/{token}'
    msg = Message(
        'Please click the below link to verify your email.',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f'Click the link to verify your email: {verification_url}'
    mail.send(msg)
    print(f"Verification email sent to {email}")
