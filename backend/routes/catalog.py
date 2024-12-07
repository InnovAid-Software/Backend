from flask import Blueprint, request, jsonify
from backend.models import Course, CourseSection
from backend.extensions import db

bp = Blueprint('catalog', __name__)

@bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all courses."""
    courses = Course.query.all()
    return jsonify([{
        'department_id': c.department_id,
        'course_number': c.course_number,
        'course_title': c.course_title
    } for c in courses])


@bp.route('/courses', methods=['POST'])
def save_courses():
    """Save courses to catalog (admin/root functionality)."""
    courseCatalog = request.get_json()

    for catalogCourseEntry in courseCatalog:
        coursedata = Course(
            department_id = catalogCourseEntry['departmentId'],
            course_number = catalogCourseEntry['courseNumber'],
            course_title = catalogCourseEntry['courseTitle']
        )
        db.session.add(coursedata)  # Move inside loop to add each course

    try:
        db.session.commit()
        return jsonify({'message': 'Courses saved successfully'}), 201  # Fixed message
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/courses/sections', methods=['GET'])
def get_course_sections():
    """Get all sections for a specific course."""
    data = request.get_json()
    if not all(k in data for k in ['department_id', 'course_number']):
        return jsonify({'message': 'Missing required fields'}), 400

    sections = CourseSection.query.filter_by(
        department_id=data['department_id'],
        course_number=data['course_number']
    ).all()

    return jsonify([{
        'department_id': cs.department_id,
        'course_number': cs.course_number,
        'section_id': cs.section_id,
        'instructor': cs.instructor,
        'days': cs.days,
        'start_time': cs.start_time,
        'end_time': cs.end_time
    } for cs in sections])

@bp.route('/courses/sections', methods=['POST'])
def save_course_sections():
    """Save course sections to catalog (admin/root functionality)."""
    sectionCatalog = request.get_json()

    for sectionEntry in sectionCatalog:
        sectiondata = CourseSection(
            department_id=sectionEntry['departmentId'],
            course_number=sectionEntry['courseNumber'],
            section_id=sectionEntry['sectionId'],
            instructor=sectionEntry['instructor'],
            days=sectionEntry['days'],
            start_time=sectionEntry['startTime'],
            end_time=sectionEntry['endTime']
        )
        db.session.add(sectiondata)

    try:
        db.session.commit()
        return jsonify({'message': 'Course sections saved successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400