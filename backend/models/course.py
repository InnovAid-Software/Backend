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
        return True

    @staticmethod
    def validate_course_number(course_number):
        """Validate course number format."""
        return True

    @staticmethod
    def from_json(json_data):
        """Convert JSON data to Course model."""
        return Course(
            department_id=json_data['departmentId'],
            course_number=json_data['courseNumber'],
            course_title=json_data['courseTitle']
        )

    def validate(self):
        """Validate course data."""
        if not self.validate_department_id(self.department_id):
            raise ValueError("Department ID must be exactly 4 letters")
        if not self.validate_course_number(self.course_number):
            raise ValueError("Course number must be exactly 4 digits")
        return True
