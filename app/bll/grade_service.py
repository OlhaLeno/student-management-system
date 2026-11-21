from app.dal.database import db
from app.dal.models import Grade, ExamGrade, CreditGrade, Student, Subject
from app.bll.result_creators import ExamCreator, CreditCreator
from app.bll.service_utils import get_required, commit


class GradeService:

    def __init__(self):
        self._exam_creator = ExamCreator()
        self._credit_creator = CreditCreator()

    def add_exam(self, student_id: int, subject_id: int, score: int) -> ExamGrade:
        self._validate_grade(student_id, subject_id)
        grade = self._exam_creator.create(student_id, subject_id, score)
        db.session.add(grade)
        commit()
        return grade

    def add_credit(self, student_id: int, subject_id: int, passed: bool) -> CreditGrade:
        self._validate_grade(student_id, subject_id)
        grade = self._credit_creator.create(student_id, subject_id, passed)
        db.session.add(grade)
        commit()
        return grade

    def get_by_id(self, grade_id: int) -> Grade:
        if type(grade_id) is not int or grade_id < 1:
            raise ValueError("Некоректний ID оцінки.")
        return get_required(Grade, grade_id, "Результат оцінювання не знайдено.")

    def delete(self, grade_id: int) -> None:
        grade = self.get_by_id(grade_id)
        db.session.delete(grade)
        commit()

    def update_exam(self, grade_id: int, score: int) -> ExamGrade:
        grade = self.get_by_id(grade_id)
        if not isinstance(grade, ExamGrade):
            raise ValueError("Цей результат є заліком, а не іспитом.")
        if type(score) is not int or not 0 <= score <= 100:
            raise ValueError("Оцінка за іспит має бути цілим числом від 0 до 100.")
        grade.score = score
        commit()
        return grade

    def update_credit(self, grade_id: int, passed: bool) -> CreditGrade:
        grade = self.get_by_id(grade_id)
        if not isinstance(grade, CreditGrade):
            raise ValueError("Цей результат є іспитом, а не заліком.")
        if type(passed) is not bool:
            raise ValueError("Результат заліку має бути true або false.")
        grade.passed = passed
        commit()
        return grade

    def change_kind(self, grade_id: int, kind: str, value) -> Grade:
        grade = self.get_by_id(grade_id)
        if kind not in ("exam", "credit"):
            raise ValueError("Обрати можна лише іспит або залік.")

        if kind == grade.kind:
            if kind == "exam":
                return self.update_exam(grade_id, value)
            return self.update_credit(grade_id, value)

        if kind == "exam":
            if type(value) is not int or not 0 <= value <= 100:
                raise ValueError("Оцінка за іспит має бути цілим числом від 0 до 100.")
            replacement = self._exam_creator.create(
                grade.student_id, grade.subject_id, value
            )
        else:
            if type(value) is not bool:
                raise ValueError("Результат заліку має бути true або false.")
            replacement = self._credit_creator.create(
                grade.student_id, grade.subject_id, value
            )

        replacement.id = grade.id
        try:
            db.session.delete(grade)
            db.session.flush()
            db.session.add(replacement)
            commit()
        except Exception:
            db.session.rollback()
            raise
        return replacement

    def for_student(self, student_id: int) -> list[Grade]:
        return db.session.query(Grade).filter_by(student_id=student_id).all()

    def all_grades(self) -> list[Grade]:
        return db.session.query(Grade).all()

    def _validate_grade(self, student_id: int, subject_id: int):
        if type(student_id) is not int or student_id < 1:
            raise ValueError("Некоректний ID студента.")
        if type(subject_id) is not int or subject_id < 1:
            raise ValueError("Некоректний ID дисципліни.")

        student = get_required(Student, student_id, "Студента не знайдено.")
        subject = get_required(Subject, subject_id, "Дисципліну не знайдено.")

        if subject not in student.group.subjects:
            raise ValueError("Академічна група студента не вивчає цю дисципліну.")

        existing = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if existing is not None:
            raise ValueError("Студент уже має результат з цієї дисципліни.")
