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
            course_number='0000',
            section_id='0',
            instructor='Reserved',
            days=''.join(r['days']),
            start_time=r['start_time'],
            end_time=r['end_time']
        )
        reserved_sections.append(reserved)
    
    if reserved_sections:
        all_sections.append(reserved_sections)

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
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                section1, section2 = schedule[i], schedule[j]
                
                # Check for overlapping days
                common_days = set(section1.days) & set(section2.days)
                if not common_days:
                    continue
                    
                # Convert times to integers for comparison
                s1_start = int(section1.start_time)
                s1_end = int(section1.end_time)
                s2_start = int(section2.start_time)
                s2_end = int(section2.end_time)
                
                # Check for time overlap on common days
                if (s1_start <= s2_end and s2_start <= s1_end):
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

