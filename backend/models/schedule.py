from backend.database import Model, SurrogatePK, Column
from backend.extensions import db
from datetime import datetime

class Schedule(Model, SurrogatePK):
    """Student Schedule model."""
    __tablename__ = 'schedules'

    student_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', backref=db.backref('schedule', uselist=False))
    sections = db.relationship('CourseSection', secondary='schedule_sections')
    
    def __init__(self, student_id, **kwargs):
        db.Model.__init__(self, student_id=student_id, **kwargs)
