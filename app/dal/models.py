
from app.dal.database import db

group_subject = db.Table(
    "group_subjects",
    db.Column("group_id", db.Integer, db.ForeignKey("academic_groups.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id"), primary_key=True),
)

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
    subjects = db.relationship(
        "Subject", secondary=group_subject, back_populates="groups"
    )
    schedule_entries = db.relationship(
        "ScheduleEntry", back_populates="group", cascade="all, delete-orphan"
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

class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)

    subjects = db.relationship(
        "Subject", back_populates="teacher"
    )

class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teachers.id"), nullable=False
    )

    teacher = db.relationship(
        "Teacher", back_populates="subjects"
    )
    groups = db.relationship(
        "AcademicGroup", secondary=group_subject, back_populates="subjects"
    )
    schedule_entries = db.relationship(
        "ScheduleEntry", back_populates="subject", cascade="all, delete-orphan"
    )

class ScheduleEntry(db.Model):
    __tablename__ = "schedule_entries"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer, db.ForeignKey("academic_groups.id"), nullable=False
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=False
    )
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    classroom = db.Column(db.String(50), nullable=False)

    group = db.relationship(
        "AcademicGroup", back_populates="schedule_entries"
    )
    subject = db.relationship(
        "Subject", back_populates="schedule_entries"
    )