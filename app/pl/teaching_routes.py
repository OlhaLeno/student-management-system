from flask import request

from app.bll.teaching_service import TeacherService, SubjectService
from app.pl.api_utils import make_api, get_data, positive_int, query_int


teaching_api = make_api("teaching_api", __name__)


def teacher_to_dict(teacher):
    return {"id": teacher.id, "full_name": teacher.full_name}


def subject_to_dict(subject):
    return {
        "id": subject.id,
        "name": subject.name,
        "teacher_id": subject.teacher_id,
        "teacher_name": subject.teacher.full_name,
        "group_ids": sorted(group.id for group in subject.groups)
    }


@teaching_api.route("/teachers", methods=["GET", "POST"])
def teachers():
    service = TeacherService()
    if request.method == "POST":
        data = get_data()
        return teacher_to_dict(service.create(data.get("full_name"))), 201
    return [teacher_to_dict(item) for item in service.get_all()]


@teaching_api.route("/teachers/<int:teacher_id>", methods=["GET", "PUT", "DELETE"])
def teacher_detail(teacher_id):
    service = TeacherService()
    if request.method == "PUT":
        data = get_data()
        return teacher_to_dict(service.update(teacher_id, data.get("full_name")))
    if request.method == "DELETE":
        service.delete(teacher_id)
        return "", 204
    return teacher_to_dict(service.get_by_id(teacher_id))


@teaching_api.route("/subjects", methods=["GET", "POST"])
def subjects():
    service = SubjectService()
    if request.method == "POST":
        data = get_data()
        subject = service.create(
            data.get("name"),
            positive_int(data.get("teacher_id"), "teacher_id")
        )
        return subject_to_dict(subject), 201
    return [subject_to_dict(item) for item in service.get_all(query_int("teacher_id"))]


@teaching_api.route("/subjects/<int:subject_id>", methods=["GET", "PUT", "DELETE"])
def subject_detail(subject_id):
    service = SubjectService()
    if request.method == "PUT":
        data = get_data()
        subject = service.update(
            subject_id, data.get("name"),
            positive_int(data.get("teacher_id"), "teacher_id")
        )
        return subject_to_dict(subject)
    if request.method == "DELETE":
        service.delete(subject_id)
        return "", 204
    return subject_to_dict(service.get_by_id(subject_id))
