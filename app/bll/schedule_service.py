from datetime import time

from app.dal.database import db
from app.dal.models import ScheduleEntry, AcademicGroup, Subject
from app.bll.service_utils import validate_text, get_required, commit


class ScheduleService:

    def get_all(
        self,
        group_id: int | None = None,
        day: int | None = None,
        teacher_id: int | None = None
    ) -> list[ScheduleEntry]:

        query = db.session.query(ScheduleEntry)

        if group_id is not None:
            query = query.filter(ScheduleEntry.group_id == group_id)

        if day is not None:
            query = query.filter(ScheduleEntry.day == day)

        if teacher_id is not None:
            query = query.join(ScheduleEntry.subject).filter(
                Subject.teacher_id == teacher_id
            )

        return query.order_by(
            ScheduleEntry.day,
            ScheduleEntry.start_time
        ).all()

    def get_by_id(self, entry_id: int) -> ScheduleEntry:
        return get_required(
            ScheduleEntry, entry_id,
            "Запис розкладу не знайдено."
        )

    def create(
        self,
        group_id: int,
        subject_id: int,
        day: int,
        start_time: time,
        end_time: time,
        classroom: str
    ) -> ScheduleEntry:

        classroom = self._validate(
            group_id, subject_id, day,
            start_time, end_time, classroom
        )

        entry = ScheduleEntry(
            group_id=group_id,
            subject_id=subject_id,
            day=day,
            start_time=start_time,
            end_time=end_time,
            classroom=classroom
        )

        db.session.add(entry)
        commit()

        return entry

    def update(
        self,
        entry_id: int,
        group_id: int,
        subject_id: int,
        day: int,
        start_time: time,
        end_time: time,
        classroom: str
    ) -> ScheduleEntry:

        entry = self.get_by_id(entry_id)

        classroom = self._validate(
            group_id, subject_id, day,
            start_time, end_time, classroom, entry_id
        )

        entry.group_id = group_id
        entry.subject_id = subject_id
        entry.day = day
        entry.start_time = start_time
        entry.end_time = end_time
        entry.classroom = classroom

        commit()

        return entry

    def delete(self, entry_id: int) -> None:
        entry = self.get_by_id(entry_id)

        db.session.delete(entry)
        commit()

    def _validate(
        self, group_id, subject_id, day,
        start_time, end_time, classroom,
        entry_id=None
    ):
        group = get_required(
            AcademicGroup, group_id,
            "Академічну групу не знайдено."
        )

        subject = get_required(
            Subject, subject_id,
            "Дисципліну не знайдено."
        )

        if subject not in group.subjects:
            raise ValueError(
                "Ця академічна група не вивчає дисципліну."
            )

        if type(day) is not int or day not in range(1, 6):
            raise ValueError(
                "Заняття можливі лише з понеділка до п'ятниці."
            )

        if not isinstance(start_time, time) or not isinstance(end_time, time):
            raise ValueError("Вкажіть коректний час заняття.")

        if start_time >= end_time:
            raise ValueError(
                "Час завершення має бути пізнішим за час початку."
            )

        classroom = validate_text(classroom, "Аудиторія", 50)

        query = db.session.query(ScheduleEntry).filter(
            ScheduleEntry.day == day,
            ScheduleEntry.start_time < end_time,
            ScheduleEntry.end_time > start_time
        )

        if entry_id is not None:
            query = query.filter(ScheduleEntry.id != entry_id)

        for entry in query.all():

            if entry.group_id == group_id:
                raise ValueError(
                    "Академічна група вже має заняття в цей час."
                )

            if entry.subject.teacher_id == subject.teacher_id:
                raise ValueError(
                    "Викладач уже проводить заняття в цей час."
                )

            if entry.classroom.casefold() == classroom.casefold():
                raise ValueError(
                    "Аудиторія вже зайнята в цей час."
                )

        return classroom
