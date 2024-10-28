from flask import Blueprint, request, jsonify
from backend.models.user import User, UserType, RegistrationQueue
from backend.extensions import db

bp = Blueprint('queue', __name__)

@bp.route('', methods=['GET'])
def get_queue():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'message': 'Missing token'}), 401
    
    user = User.check_token(data['token'])
    if not user or user.user_type not in [UserType.ADMIN, UserType.ROOT]:
        return jsonify({'message': 'Unauthorized access'}), 403

    pending_requests = RegistrationQueue.query.filter_by(approved=False).all()
    queue_data = [{
        'id': req.id,
        'user_email': req.user.email,
        'request_type': req.request_type.value,
        'user_id': req.user_id
    } for req in pending_requests]
    
    return jsonify(queue_data), 200

@bp.route('', methods=['POST'])
def process_queue_request():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'message': 'Missing token'}), 401
    
    admin_user = User.check_token(data['token'])
    if not admin_user or admin_user.user_type not in [UserType.ADMIN, UserType.ROOT]:
        return jsonify({'message': 'Unauthorized access'}), 403

    if not all(k in data for k in ['email', 'approval_status']):
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    queue_request = RegistrationQueue.query.filter_by(user_id=user.id, approved=False).first()
    if not queue_request:
        return jsonify({'message': 'No pending request found for this user'}), 404

    if data['approval_status']:
        queue_request.approve()
        user.verified = True
        db.session.commit()
        return jsonify({'message': 'Request approved successfully'}), 200
    else:
        queue_request.reject()
        return jsonify({'message': 'Request rejected successfully'}), 200
