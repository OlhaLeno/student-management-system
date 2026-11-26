from app.dal.database import db
from app.dal.models import Teacher, Subject
from app.bll.service_utils import validate_text, get_required, commit
from app.bll.observer import publish_event, schedule_slot_data


class TeacherService:

    def get_all(self) -> list[Teacher]:
        return db.session.query(Teacher).order_by(
            Teacher.full_name
        ).all()

    def get_by_id(self, teacher_id: int) -> Teacher:
        return get_required(
            Teacher, teacher_id, "Викладача не знайдено."
        )

    def create(self, full_name: str) -> Teacher:
        full_name = validate_text(full_name, "ПІБ викладача", 150)

        teacher = Teacher(full_name=full_name)

        db.session.add(teacher)
        commit()

        return teacher

    def update(self, teacher_id: int, full_name: str) -> Teacher:
        teacher = self.get_by_id(teacher_id)

        teacher.full_name = validate_text(
            full_name, "ПІБ викладача", 150
        )

        commit()

        return teacher

    def delete(self, teacher_id: int) -> None:
        teacher = self.get_by_id(teacher_id)

        group_subjects = {}
        freed_slots = []

        for subject in list(teacher.subjects):
            for group in list(subject.groups):
                item = group_subjects.setdefault(
                    group.id,
                    {"group_name": group.name, "subjects": []}
                )
                item["subjects"].append(subject.name)

            for entry in list(subject.schedule_entries):
                freed_slots.append(schedule_slot_data(entry))

        publish_event(
            "teacher_deleted",
            teacher_name=teacher.full_name,
            group_subjects=[
                {
                    **item,
                    "subjects": sorted(set(item["subjects"]), key=str.casefold)
                }
                for item in group_subjects.values()
            ],
            freed_slots=freed_slots,
        )

        db.session.delete(teacher)
        commit()


class SubjectService:

    def get_all(
        self, teacher_id: int | None = None
    ) -> list[Subject]:

        query = db.session.query(Subject)

        if teacher_id is not None:
            query = query.filter_by(teacher_id=teacher_id)

        return query.order_by(Subject.name).all()

    def get_by_id(self, subject_id: int) -> Subject:
        return get_required(
            Subject, subject_id, "Дисципліну не знайдено."
        )

    def create(self, name: str, teacher_id: int) -> Subject:
        name = self._validate(name, teacher_id)

        subject = Subject(
            name=name,
            teacher_id=teacher_id
        )

        db.session.add(subject)
        commit()

        return subject

    def update(
        self, subject_id: int, name: str, teacher_id: int
    ) -> Subject:

        subject = self.get_by_id(subject_id)

        name = self._validate(name, teacher_id, subject_id)

        if subject.teacher_id != teacher_id:
            if subject.grades or subject.schedule_entries:
                raise ValueError(
                    "Неможливо змінити викладача дисципліни, "
                    "яка вже має оцінки або заняття в розкладі."
                )

        subject.name = name
        subject.teacher_id = teacher_id

        commit()

        return subject

    def delete(self, subject_id: int) -> None:
        subject = self.get_by_id(subject_id)

        groups = [group.name for group in list(subject.groups)]
        freed_slots = [
            schedule_slot_data(entry)
            for entry in list(subject.schedule_entries)
        ]

        publish_event(
            "subject_removed",
            subject_name=subject.name,
            groups=groups,
            freed_slots=freed_slots,
        )

        db.session.delete(subject)
        commit()

    def _validate(self, name, teacher_id, subject_id=None):
        name = validate_text(name, "Назва дисципліни", 100)

        TeacherService().get_by_id(teacher_id)

        existing = Subject.query.filter_by(
            name=name,
            teacher_id=teacher_id
        ).first()

        if existing is not None and existing.id != subject_id:
            raise ValueError(
                "Така дисципліна вже закріплена за викладачем."
            )

        return name
