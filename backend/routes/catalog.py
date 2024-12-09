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
    course_catalog = request.get_json()
    
    if not isinstance(course_catalog, list):
        return jsonify({'error': 'Invalid input format - expected a list of courses'}), 400

    try:
        # Delete all existing courses
        Course.query.delete()
        
        # Now add the new courses
        for course_entry in course_catalog:
            # Normalize the data
            normalized_entry = {
                'departmentId': course_entry['departmentId'].strip().upper(),
                'courseNumber': course_entry['courseNumber'].strip(),
                'courseTitle': course_entry['courseTitle'].strip()
            }
            
            course = Course.from_json(normalized_entry)
            try:
                course.validate()
            except ValueError as ve:
                return jsonify({
                    'error': f"Validation failed for course {normalized_entry['departmentId']} {normalized_entry['courseNumber']}: {str(ve)}"
                }), 400
                
            db.session.add(course)
        
        db.session.commit()
        return jsonify({'message': 'Courses saved successfully'}), 201
        
    except KeyError as e:
        db.session.rollback()
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/courses/sections/all', methods=['GET'])
def get_all_course_sections():
    """Get all course sections."""
    sections = CourseSection.query.all()
    return jsonify([{
        'department_id': cs.department_id,
        'course_number': cs.course_number,
        'course_title': cs.course_title,
        'section_id': cs.section_id,
        'instructor': cs.instructor,
        'days': cs.days,
        'start_time': cs.start_time,
        'end_time': cs.end_time
    } for cs in sections])

@bp.route('/courses/sections', methods=['GET'])
def get_course_sections():
    """Get all sections for a specific course, or all sections if no course specified."""
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
    CourseSection.query.delete()

    for sectionEntry in sectionCatalog:
        sectiondata = CourseSection(
            department_id=sectionEntry['departmentId'],
            course_number=sectionEntry['courseNumber'],
            course_title=sectionEntry['courseTitle'],
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