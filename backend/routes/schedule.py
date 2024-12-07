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
    data = request.get_json()
    if not all(k in data for k in ['courses', 'reserved']):
        return jsonify({'message': 'Missing required fields'}), 400

    # Get all sections for requested courses
    all_sections = []
    for course in data['courses']:
        sections = CourseSection.query.filter_by(
            department_id=course['department_id'],
            course_number=course['course_number']
        ).all()
        if sections:
            all_sections.append(sections)

    # Convert reserved times to section-like objects
    reserved_sections = []
    for r in data['reserved']:
        reserved = CourseSection(
            department_id='RESV',
            course_number='000',
            section_id='0',
            instructor='Reserved',
            days=''.join(r['days']),
            start_time=r['start_time'],
            end_time=r['end_time']
        )
        reserved_sections.append([reserved])
    
    if reserved_sections:
        all_sections.append(reserved_sections[0])

    # Generate all possible combinations
    def cartesian_product(arrays):
        if not arrays:
            return [[]]
        result = [[]]
        for array in arrays:
            result = [x + [y] for x in result for y in array]
        return result

    possible_schedules = cartesian_product(all_sections)

    # Filter out schedules with time conflicts
    def has_time_conflict(schedule):
        days_order = {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4}
        
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                section1, section2 = schedule[i], schedule[j]
                
                # Check for overlapping days
                common_days = set(section1.days) & set(section2.days)
                if not common_days:
                    continue
                    
                # Check for time overlap on common days
                if (section1.start_time <= section2.end_time and 
                    section2.start_time <= section1.end_time):
                    return True
        return False

    valid_schedules = [schedule for schedule in possible_schedules 
                      if not has_time_conflict(schedule)]

    # Convert to JSON response format
    response = [{
        'sections': [{
            'department_id': section.department_id,
            'course_number': section.course_number,
            'section_id': section.section_id,
            'instructor': section.instructor,
            'days': list(section.days),
            'start_time': section.start_time,
            'end_time': section.end_time
        } for section in schedule]
    } for schedule in valid_schedules]

    return jsonify(response)

