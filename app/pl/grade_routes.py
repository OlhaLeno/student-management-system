from flask import request

from app.bll.grade_service import GradeService
from app.dal.models import ExamGrade, CreditGrade
from app.bll.student_service import StudentService
from app.bll.performance_facade import PerformanceFacade
from app.pl.api_utils import make_api, get_data, positive_int, query_int


grade_api = make_api("grade_api", __name__)


def grade_to_dict(grade):
    debt = grade.is_debt()
    data = {
        "id": grade.id,
        "student_id": grade.student_id,
        "student_name": grade.student.full_name,
        "subject_id": grade.subject_id,
        "subject_name": grade.subject.name,
        "kind": grade.kind,
        "kind_name": "Іспит" if grade.kind == "exam" else "Залік",
        "has_debt": debt,
        "debt_status": "Є" if debt else "Немає"
    }
    if grade.kind == "exam":
        data["score"] = grade.score
        data["result"] = grade.score
    else:
        data["passed"] = grade.passed
        data["result"] = "Зараховано" if grade.passed else "Не зараховано"
    return data


@grade_api.route("/grades", methods=["GET", "POST"])
def grades():
    service = GradeService()
    if request.method == "POST":
        data = get_data()
        student_id = positive_int(data.get("student_id"), "student_id")
        subject_id = positive_int(data.get("subject_id"), "subject_id")
        kind = data.get("kind")
        if kind not in ("exam", "credit"):
            raise ValueError("Обрати можна лише іспит або залік.")

        if kind == "exam":
            grade = service.add_exam(student_id, subject_id, data.get("score"))
        else:
            grade = service.add_credit(student_id, subject_id, data.get("passed"))
        return grade_to_dict(grade), 201

    student_id = query_int("student_id")
    if student_id is not None:
        StudentService().get_by_id(student_id)
        items = service.for_student(student_id)
    else:
        items = service.all_grades()
    return [grade_to_dict(item) for item in items]


@grade_api.get("/students/<int:student_id>/grades")
def student_grades(student_id):
    StudentService().get_by_id(student_id)
    return [grade_to_dict(item) for item in GradeService().for_student(student_id)]


@grade_api.get("/students/<int:student_id>/performance")
def student_performance(student_id):
    student = StudentService().get_by_id(student_id)
    data = PerformanceFacade().summary(student_id)
    data["student_name"] = student.full_name
    data["debt_status"] = "Є" if data["has_debt"] else "Немає"
    return data


@grade_api.route("/grades/<int:grade_id>", methods=["GET", "PUT"])
def grade_detail(grade_id):
    service = GradeService()
    grade = service.get_by_id(grade_id)

    if request.method == "PUT":
        data = get_data()
        if isinstance(grade, ExamGrade):
            if set(data) != {"score"}:
                raise ValueError("Для іспиту потрібно передати лише поле score.")
            grade = service.update_exam(grade_id, data["score"])
        elif isinstance(grade, CreditGrade):
            if set(data) != {"passed"}:
                raise ValueError("Для заліку потрібно передати лише поле passed.")
            grade = service.update_credit(grade_id, data["passed"])
        else:
            raise ValueError("Невідомий вид оцінювання.")

    return grade_to_dict(grade)
