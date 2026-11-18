from flask import request

from app.bll.student_service import StudentService
from app.pl.api_utils import make_api, get_data, positive_int, query_int


student_api = make_api("student_api", __name__)


def student_to_dict(student):
    group = student.group
    specialty = group.specialty
    return {
        "id": student.id,
        "full_name": student.full_name,
        "group_id": group.id,
        "group_name": group.name,
        "course": group.course,
        "specialty_id": specialty.id,
        "specialty_name": specialty.name,
        "institute_id": specialty.institute_id,
        "institute_name": specialty.institute.name
    }


@student_api.route("/students", methods=["GET", "POST"])
def students():
    service = StudentService()
    if request.method == "POST":
        data = get_data()
        student = service.create(
            data.get("full_name"),
            positive_int(data.get("group_id"), "group_id")
        )
        return student_to_dict(student), 201
    return [student_to_dict(item) for item in service.get_all(query_int("group_id"))]


@student_api.route("/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
def student_detail(student_id):
    service = StudentService()
    if request.method == "PUT":
        data = get_data()
        student = service.update(
            student_id, data.get("full_name"),
            positive_int(data.get("group_id"), "group_id")
        )
        return student_to_dict(student)
    if request.method == "DELETE":
        service.delete(student_id)
        return "", 204
    return student_to_dict(service.get_by_id(student_id))
