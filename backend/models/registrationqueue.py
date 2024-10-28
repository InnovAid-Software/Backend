from backend.database import Model, SurrogatePK, Column, reference_col
from backend.extensions import db
import enum

class RequestType(enum.Enum):
    ADMIN = "ADMIN"
    ROOT = "ROOT"

class RegistrationQueue(Model, SurrogatePK):
    __tablename__ = 'registration_queue'

    approved = Column(db.Boolean(), default=False, nullable=False)
    request_type = Column(db.Enum(RequestType), nullable=False)
    user_id = reference_col('users', nullable=False)
    user = db.relationship('User', backref=db.backref('registration_requests', lazy='dynamic'))

    def __init__(self, user, request_type, **kwargs):
        """Create instance."""
        super().__init__(user_id=user.id, request_type=request_type, **kwargs)

    def __repr__(self):
        return f"<RegistrationQueue(user_id={self.user_id}, request_type={self.request_type}, approved={self.approved})>"

    def approve(self):
        """Approve the registration request"""
        self.approved = True
        self.user.verified = True
        db.session.add(self.user)
        return self.save()

    def reject(self):
        """Reject the registration request"""
        self.approved = False
        self.user.verified = False
        db.session.add(self.user)
        return self.save()
