from itertools import product
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
    section_options = []
    for course in data['courses']:
        sections = CourseSection.query.filter_by(
            department_id=course['department_id'],
            course_number=course['course_number']
        ).all()
        
        # Add error handling for when no sections are found
        if not sections:
            return jsonify({
                'message': f'No sections found for {course["department_id"]} {course["course_number"]}'
            }), 404
            
        section_options.append(sections)

    # Add reserved times as sections if list exists and is not empty
    if 'reserved' in data and data['reserved'] and isinstance(data['reserved'], list):
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
        section_options.append(reserved_sections)

    # Add logging for debugging
    possible_schedules = list(product(*section_options))
    if not possible_schedules:
        return jsonify({
            'message': 'No possible schedule combinations could be generated'
        }), 404

    def check_overlap(schedule):
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                # Check for common days
                common_days = set(schedule[i].days) & set(schedule[j].days)
                if not common_days:
                    continue
                    
                # Convert times to integers for comparison
                s1_start = int(schedule[i].start_time)
                s1_end = int(schedule[i].end_time)
                s2_start = int(schedule[j].start_time)
                s2_end = int(schedule[j].end_time)
                
                # Check for time overlap
                if s1_start < s2_end and s1_end > s2_start:
                    return True
        return False

    # Filter out schedules with conflicts
    valid_schedules = [schedule for schedule in possible_schedules if not check_overlap(schedule)]
    if not valid_schedules:
        return jsonify({
            'message': 'No valid schedules found - all possible combinations have time conflicts'
        }), 404

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

