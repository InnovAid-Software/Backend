from backend.database import Model, SurrogatePK, Column
from backend.extensions import db


class Course(Model, SurrogatePK):
    """Course model."""
    __tablename__ = 'courses'

    department_id = Column(db.String(4), nullable=False)
    course_number = Column(db.String(4), nullable=False)
    course_title = Column(db.String(100), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('department_id', 'course_number', name='unique_course'),
    )

    def __init__(self, department_id, course_number, course_title, **kwargs):
        """Create instance."""
        db.Model.__init__(self, department_id=department_id, 
                         course_number=course_number, 
                         course_title=course_title, **kwargs)

    @staticmethod
    def validate_department_id(department_id):
        """Validate department ID format."""
        return bool(department_id and len(department_id) == 4 and department_id.isalpha())

    @staticmethod
    def validate_course_number(course_number):
        """Validate course number format."""
        return bool(course_number and len(course_number) == 4 and course_number.isdigit())
