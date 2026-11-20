
from app.dal.database import db
from app.dal.models import Student, AcademicGroup
from app.bll.service_utils import validate_text, get_required, commit


class StudentService:

    def get_all(
        self, group_id: int | None = None
    ) -> list[Student]:

        query = db.session.query(Student)

        if group_id is not None:
            query = query.filter_by(group_id=group_id)

        return query.order_by(Student.full_name).all()

    def get_by_id(self, student_id: int) -> Student:
        return get_required(
            Student, student_id, "Студента не знайдено."
        )

    def create(self, full_name: str, group_id: int) -> Student:
        full_name = validate_text(full_name, "ПІБ студента", 150)

        get_required(
            AcademicGroup, group_id,
            "Академічну групу не знайдено."
        )

        student = Student(
            full_name=full_name,
            group_id=group_id
        )

        db.session.add(student)
        commit()

        return student

    def update(
        self, student_id: int, full_name: str, group_id: int
    ) -> Student:

        student = self.get_by_id(student_id)

        full_name = validate_text(full_name, "ПІБ студента", 150)

        get_required(
            AcademicGroup, group_id,
            "Академічну групу не знайдено."
        )

        student.full_name = full_name
        student.group_id = group_id

        commit()

        return student

    def delete(self, student_id: int) -> None:
        student = self.get_by_id(student_id)

        if student.grades:
            raise ValueError(
                "Неможливо видалити студента, який має оцінки."
            )

        db.session.delete(student)
        commit()
