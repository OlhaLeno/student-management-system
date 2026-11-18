from app.dal.database import db
from sqlalchemy.orm import validates

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
    grades = db.relationship(
        "Grade", back_populates="student"
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
    grades = db.relationship(
        "Grade", back_populates="subject"
    )

class ScheduleEntry(db.Model):
    __tablename__ = "schedule_entries"
    
    __table_args__ = (
        db.CheckConstraint(
            "day IN (1, 2, 3, 4, 5)",
            name="check_schedule_day"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer, db.ForeignKey("academic_groups.id"), nullable=False
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=False
    )
    day = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    classroom = db.Column(db.String(50), nullable=False)

    group = db.relationship(
        "AcademicGroup", back_populates="schedule_entries"
    )
    subject = db.relationship(
        "Subject", back_populates="schedule_entries"
    )
    @property
    def day_name(self):
        days = {
            1: "Понеділок",
            2: "Вівторок",
            3: "Середа",
            4: "Четвер",
            5: "П'ятниця",
        }

        return days.get(self.day, "Невідомий день")

    @validates("day")
    def validate_day(self, key, value):
        if type(value) is not int or value not in range(1, 6):
            raise ValueError("Заняття можуть проводитись лише з понеділка до п'ятниці.")
        return value


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id"), nullable=False
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=False
    )
    kind = db.Column(db.String(10), nullable=False)

    student = db.relationship("Student", back_populates="grades")
    subject = db.relationship("Subject", back_populates="grades")

    __mapper_args__ = {
        "polymorphic_on": kind,
        "polymorphic_abstract": True
    }

    def is_debt(self):
        raise NotImplementedError


class ExamGrade(Grade):
    score = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "exam"
    }

    @validates("score")
    def validate_score(self, key, value):
        if type(value) is not int or not 0 <= value <= 100:
            raise ValueError("Оцінка повинна бути від 0 до 100.")
        return value

    def is_debt(self):
        return self.score <= 50


class CreditGrade(Grade):
    passed = db.Column(db.Boolean, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "credit"
    }

    @validates("passed")
    def validate_passed(self, key, value):
        if type(value) is not bool:
            raise ValueError("Результат заліку має бути True або False.")
        return value

    def is_debt(self):
        return not self.passed
