from flask import Blueprint, request, jsonify
from backend.models import Course, CourseSection
from backend.extensions import db

bp = Blueprint('catalog', __name__)

@bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all courses."""
    pass

@bp.route('/courses', methods=['POST'])
def save_courses():
    """Save courses to catalog (admin/root functionality)."""
    pass

@bp.route('/courses/<int:course_id>/sections', methods=['GET'])
def get_course_sections():
    """Get all sections for a specific course."""
    pass
