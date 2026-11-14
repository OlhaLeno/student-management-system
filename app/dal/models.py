
from app.dal.database import db


class Institute(db.Model):
    __tablename__ = "institutes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    specialties = db.relationship(
        "Specialty", back_populates="institute"
    )


class Specialty(db.Model):
    __tablename__ = "specialties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    institute_id = db.Column(
        db.Integer, db.ForeignKey("institutes.id"), nullable=False
    )

    institute = db.relationship(
        "Institute", back_populates="specialties"
    )
    groups = db.relationship(
        "AcademicGroup", back_populates="specialty"
    )


class AcademicGroup(db.Model):
    __tablename__ = "academic_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    specialty_id = db.Column(
        db.Integer, db.ForeignKey("specialties.id"), nullable=False
    )

    specialty = db.relationship(
        "Specialty", back_populates="groups"
    )
    students = db.relationship(
        "Student", back_populates="group"
    )


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    group_id = db.Column(
        db.Integer, db.ForeignKey("academic_groups.id"), nullable=False
    )

    group = db.relationship(
        "AcademicGroup", back_populates="students"
    )
