from backend.database import Model, SurrogatePK, Column
from backend.extensions import db

class CourseSection(Model, SurrogatePK):
    """Course Section model."""
    __tablename__ = 'course_sections'

    department_id = Column(db.String(4), nullable=False)
    course_number = Column(db.String(4), nullable=False)
    course_title = Column(db.String(100), nullable=False)
    section_id = Column(db.String(10), nullable=False)
    instructor = Column(db.String(100), nullable=False)
    days = Column(db.String(5), nullable=False)  # e.g., "MWF"
    start_time = Column(db.String(10), nullable=False)  # Format: HHMM
    end_time = Column(db.String(10), nullable=False)    # Format: HHMM

    def __init__(self, department_id, course_number, section_id, instructor, 
                 days, start_time, end_time, **kwargs):
        db.Model.__init__(self, department_id=department_id, 
                         course_number=course_number,
                         section_id=section_id,
                         instructor=instructor,
                         days=days,
                         start_time=start_time,
                         end_time=end_time,
                         **kwargs)
