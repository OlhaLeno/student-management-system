from flask import request

from app.bll.university_service import (
    InstituteService, SpecialtyService, AcademicGroupService
)
from app.pl.api_utils import make_api, get_data, positive_int, query_int


university_api = make_api("university_api", __name__)


def institute_to_dict(institute):
    return {"id": institute.id, "name": institute.name}


def specialty_to_dict(specialty):
    return {
        "id": specialty.id,
        "name": specialty.name,
        "institute_id": specialty.institute_id,
        "institute_name": specialty.institute.name
    }


def group_to_dict(group):
    return {
        "id": group.id,
        "name": group.name,
        "course": group.course,
        "specialty_id": group.specialty_id,
        "specialty_name": group.specialty.name,
        "institute_id": group.specialty.institute_id,
        "institute_name": group.specialty.institute.name,
        "subject_ids": sorted(subject.id for subject in group.subjects)
    }


# Інститути
@university_api.route("/institutes", methods=["GET", "POST"])
def institutes():
    service = InstituteService()
    if request.method == "POST":
        data = get_data()
        return institute_to_dict(service.create(data.get("name"))), 201
    return [institute_to_dict(item) for item in service.get_all()]


@university_api.route("/institutes/<int:institute_id>", methods=["GET", "PUT", "DELETE"])
def institute_detail(institute_id):
    service = InstituteService()
    if request.method == "PUT":
        data = get_data()
        return institute_to_dict(service.update(institute_id, data.get("name")))
    if request.method == "DELETE":
        service.delete(institute_id)
        return "", 204
    return institute_to_dict(service.get_by_id(institute_id))


@university_api.route("/specialties", methods=["GET", "POST"])
def specialties():
    service = SpecialtyService()
    if request.method == "POST":
        data = get_data()
        specialty = service.create(
            data.get("name"),
            positive_int(data.get("institute_id"), "institute_id")
        )
        return specialty_to_dict(specialty), 201
    return [specialty_to_dict(item) for item in service.get_all(query_int("institute_id"))]


@university_api.route("/specialties/<int:specialty_id>", methods=["GET", "PUT", "DELETE"])
def specialty_detail(specialty_id):
    service = SpecialtyService()
    if request.method == "PUT":
        data = get_data()
        specialty = service.update(
            specialty_id, data.get("name"),
            positive_int(data.get("institute_id"), "institute_id")
        )
        return specialty_to_dict(specialty)
    if request.method == "DELETE":
        service.delete(specialty_id)
        return "", 204
    return specialty_to_dict(service.get_by_id(specialty_id))


@university_api.route("/groups", methods=["GET", "POST"])
def groups():
    service = AcademicGroupService()
    if request.method == "POST":
        data = get_data()
        group = service.create(
            data.get("name"),
            positive_int(data.get("course"), "course"),
            positive_int(data.get("specialty_id"), "specialty_id")
        )
        return group_to_dict(group), 201
    return [group_to_dict(item) for item in service.get_all(
        specialty_id=query_int("specialty_id"), course=query_int("course")
    )]


@university_api.route("/groups/<int:group_id>", methods=["GET", "PUT", "DELETE"])
def group_detail(group_id):
    service = AcademicGroupService()
    if request.method == "PUT":
        data = get_data()
        group = service.update(
            group_id, data.get("name"),
            positive_int(data.get("course"), "course"),
            positive_int(data.get("specialty_id"), "specialty_id")
        )
        return group_to_dict(group)
    if request.method == "DELETE":
        service.delete(group_id)
        return "", 204
    return group_to_dict(service.get_by_id(group_id))


@university_api.route("/groups/<int:group_id>/subjects/<int:subject_id>", methods=["PUT", "DELETE"])
def group_subject(group_id, subject_id):
    service = AcademicGroupService()
    if request.method == "PUT":
        service.add_subject(group_id, subject_id)
    else:
        service.remove_subject(group_id, subject_id)
    return "", 204
