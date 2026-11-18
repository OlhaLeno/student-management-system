from flask import request

from app.bll.schedule_service import ScheduleService
from app.pl.api_utils import make_api, get_data, positive_int, query_int, parse_time


schedule_api = make_api("schedule_api", __name__)


def schedule_to_dict(entry):
    return {
        "id": entry.id,
        "group_id": entry.group_id,
        "group_name": entry.group.name,
        "subject_id": entry.subject_id,
        "subject_name": entry.subject.name,
        "teacher_id": entry.subject.teacher_id,
        "teacher_name": entry.subject.teacher.full_name,
        "day": entry.day,
        "day_name": entry.day_name,
        "start_time": entry.start_time.isoformat(timespec="seconds"),
        "end_time": entry.end_time.isoformat(timespec="seconds"),
        "classroom": entry.classroom
    }


def schedule_data():
    data = get_data()
    return {
        "group_id": positive_int(data.get("group_id"), "group_id"),
        "subject_id": positive_int(data.get("subject_id"), "subject_id"),
        "day": positive_int(data.get("day"), "day"),
        "start_time": parse_time(data.get("start_time"), "Час початку"),
        "end_time": parse_time(data.get("end_time"), "Час завершення"),
        "classroom": data.get("classroom")
    }


@schedule_api.route("/schedule", methods=["GET", "POST"])
def schedule():
    service = ScheduleService()
    if request.method == "POST":
        return schedule_to_dict(service.create(**schedule_data())), 201
    day = query_int("day")
    if day is not None and day > 5:
        raise ValueError("Заняття можливі лише з понеділка до п'ятниці.")
    entries = service.get_all(
        group_id=query_int("group_id"), day=day,
        teacher_id=query_int("teacher_id")
    )
    return [schedule_to_dict(item) for item in entries]


@schedule_api.route("/schedule/<int:entry_id>", methods=["GET", "PUT", "DELETE"])
def schedule_detail(entry_id):
    service = ScheduleService()
    if request.method == "PUT":
        return schedule_to_dict(service.update(entry_id, **schedule_data()))
    if request.method == "DELETE":
        service.delete(entry_id)
        return "", 204
    return schedule_to_dict(service.get_by_id(entry_id))
