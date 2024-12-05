from flask import Blueprint, request, jsonify
from backend.models import CourseSection
from backend.extensions import db

bp = Blueprint('schedule', __name__)

@bp.route('', methods=['GET'])
def get_schedule():
    """Get all course sections."""
    sections = CourseSection.query.all()
    return jsonify([{
        'department_id': s.department_id,
        'course_number': s.course_number,
        'section_id': s.section_id,
        'instructor': s.instructor,
        'days': s.days,
        'start_time': s.start_time,
        'end_time': s.end_time
    } for s in sections])

@bp.route('', methods=['POST'])
def save_schedule():
    """Save course sections (admin/root functionality)."""
    data = request.get_json()
    
    # Clear existing sections if this is a full update
    if request.args.get('clear', 'false').lower() == 'true':
        CourseSection.query.delete()
    
    # Add new sections
    for section_data in data:
        section = CourseSection(
            department_id=section_data['departmentId'],
            course_number=section_data['courseNumber'],
            section_id=section_data['sectionId'],
            instructor=section_data['instructor'],
            days=''.join(section_data['days']),
            start_time=section_data['startTime'],
            end_time=section_data['endTime']
        )
        db.session.add(section)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Sections saved successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/generate', methods=['POST'])
def generate_schedules():
    """Generate possible schedules based on selected courses and reserved times."""
    pass

@bp.route('/sections/<int:section_id>', methods=['POST'])
def add_section():
    """Add a section to student's schedule."""
    pass

@bp.route('/sections/<int:section_id>', methods=['DELETE'])
def remove_section():
    """Remove a section from student's schedule."""
    pass
