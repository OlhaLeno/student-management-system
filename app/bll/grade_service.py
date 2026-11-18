
from app.dal.database import db
from app.dal.models import Grade, ExamGrade, CreditGrade
from app.bll.result_creators import ExamCreator, CreditCreator


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

        grade = self._exam_creator.create(
            student_id,
            subject_id,
            score
        )

        try:
            db.session.add(grade)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return grade

    def add_credit(
        self,
        student_id: int,
        subject_id: int,
        passed: bool
    ) -> CreditGrade:

        grade = self._credit_creator.create(
            student_id,
            subject_id,
            passed
        )

        try:
            db.session.add(grade)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return grade

    def for_student(self, student_id: int) -> list[Grade]:
        return db.session.query(Grade).filter_by(
            student_id=student_id
        ).all()

    def all_grades(self) -> list[Grade]:
        return db.session.query(Grade).all()
