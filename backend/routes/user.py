from flask import Blueprint, request, jsonify
from backend.models.user import User, UserType
from backend.models.registrationqueue import RegistrationQueue
from backend.extensions import db
from flask_bcrypt import Bcrypt

bp = Blueprint('user', __name__)
bcrypt = Bcrypt()

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token, expires_on = user.generate_token()
        return jsonify({'token': token.decode('utf-8'), 'expires_on': expires_on}), 200
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
        send_verification_email(user.email, verification_token)
        return jsonify({'message': 'Verification email sent'}), 201

@bp.route('/verify/<token>', methods=['GET'])
def verify(token):
    user = User.verify_token(token)
    if user:
        user.verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    return jsonify({'message': 'Invalid or expired token'}), 400


def send_verification_email(email, token):
    # This is a dummy function for sending verification email
    print(f"Sending verification email to {email} with token: {token}")
