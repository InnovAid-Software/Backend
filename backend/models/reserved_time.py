from backend.database import Model, SurrogatePK, Column
from backend.extensions import db

class ReservedTime(Model, SurrogatePK):
    """Reserved time blocks in a student's schedule."""
    __tablename__ = 'reserved_times'

    schedule_id = Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    days = Column(db.String(5), nullable=False)  # e.g., "MWF"
    start_time = Column(db.String(10), nullable=False)  # Format: HHMM
    end_time = Column(db.String(10), nullable=False)    # Format: HHMM
    description = Column(db.String(100), nullable=True)

    # Relationship
    schedule = db.relationship('Schedule', backref=db.backref('reserved_times', lazy=True))

    def __init__(self, schedule_id, days, start_time, end_time, description=None, **kwargs):
        db.Model.__init__(self, schedule_id=schedule_id, days=days,
                         start_time=start_time, end_time=end_time,
                         description=description, **kwargs) 