
from app.dal.database import db
from app.dal.models import Grade, ExamGrade, CreditGrade, Student, Subject
from app.bll.result_creators import ExamCreator, CreditCreator
from app.bll.service_utils import get_required, commit


class GradeService:

    def __init__(self):
        self._exam_creator = ExamCreator()
        self._credit_creator = CreditCreator()

    def add_exam(
        self,
        student_id: int,
        subject_id: int,
        score: int
    ) -> ExamGrade:

        self._validate_grade(student_id, subject_id)

        grade = self._exam_creator.create(
            student_id,
            subject_id,
            score
        )

        db.session.add(grade)
        commit()

        return grade

    def add_credit(
        self,
        student_id: int,
        subject_id: int,
        passed: bool
    ) -> CreditGrade:

        self._validate_grade(student_id, subject_id)

        grade = self._credit_creator.create(
            student_id,
            subject_id,
            passed
        )

        db.session.add(grade)
        commit()

        return grade

    def for_student(self, student_id: int) -> list[Grade]:
        return db.session.query(Grade).filter_by(
            student_id=student_id
        ).all()

    def all_grades(self) -> list[Grade]:
        return db.session.query(Grade).all()

    def _validate_grade(self, student_id: int, subject_id: int):

        if type(student_id) is not int or student_id < 1:
            raise ValueError("Некоректний ID студента.")

        if type(subject_id) is not int or subject_id < 1:
            raise ValueError("Некоректний ID дисципліни.")

        student = get_required(
            Student, student_id,
            "Студента не знайдено."
        )

        subject = get_required(
            Subject, subject_id,
            "Дисципліну не знайдено."
        )

        if subject not in student.group.subjects:
            raise ValueError(
                "Академічна група студента не вивчає цю дисципліну."
            )

        existing = Grade.query.filter_by(
            student_id=student_id,
            subject_id=subject_id
        ).first()

        if existing is not None:
            raise ValueError(
                "Студент уже має результат з цієї дисципліни."
            )
