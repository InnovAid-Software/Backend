from backend.database import Model, Column
from backend.extensions import db

class ScheduleSection(Model):
    """Association table between Schedule and CourseSection."""
    __tablename__ = 'schedule_sections'

    schedule_id = Column(db.Integer, db.ForeignKey('schedules.id'), primary_key=True)
    section_id = Column(db.Integer, db.ForeignKey('course_sections.id'), primary_key=True) 