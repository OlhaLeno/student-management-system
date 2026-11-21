from app.dal.database import db
from app.dal.models import Institute, Specialty, AcademicGroup, Subject

from app.bll.service_utils import validate_text, get_required, commit

class InstituteService:

    def get_all(self) -> list[Institute]:
        return db.session.query(Institute).order_by(
            Institute.name
        ).all()

    def get_by_id(self, institute_id: int) -> Institute:
        institute = db.session.get(Institute, institute_id)

        if institute is None:
            raise LookupError("Інститут не знайдено.")

        return institute

    def create(self, name: str) -> Institute:
        name = self._validate_name(name)

        institute = Institute(name=name)

        db.session.add(institute)
        self._commit()

        return institute

    def update(self, institute_id: int, name: str) -> Institute:
        institute = self.get_by_id(institute_id)

        institute.name = self._validate_name(name, institute_id)

        self._commit()

        return institute

    def delete(self, institute_id: int) -> None:
        institute = self.get_by_id(institute_id)

        db.session.delete(institute)
        self._commit()

    def _validate_name(
        self,
        name: str,
        institute_id: int | None = None
    ) -> str:

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Введіть назву інституту.")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Назва не може перевищувати 100 символів.")

        existing = Institute.query.filter_by(name=name).first()

        if existing is not None and existing.id != institute_id:
            raise ValueError("Інститут із такою назвою вже існує.")

        return name

    def _commit(self) -> None:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


class SpecialtyService:

    def get_all(
        self,
        institute_id: int | None = None
    ) -> list[Specialty]:

        query = db.session.query(Specialty)

        if institute_id is not None:
            InstituteService().get_by_id(institute_id)
            query = query.filter_by(institute_id=institute_id)

        return query.order_by(Specialty.name).all()

    def get_by_id(self, specialty_id: int) -> Specialty:
        specialty = db.session.get(Specialty, specialty_id)

        if specialty is None:
            raise LookupError("Спеціальність не знайдено.")

        return specialty

    def create(self, name: str, institute_id: int) -> Specialty:
        InstituteService().get_by_id(institute_id)

        name = self._validate_name(name, institute_id)

        specialty = Specialty(
            name=name,
            institute_id=institute_id
        )

        db.session.add(specialty)
        self._commit()

        return specialty

    def update(
        self,
        specialty_id: int,
        name: str,
        institute_id: int
    ) -> Specialty:

        specialty = self.get_by_id(specialty_id)
        InstituteService().get_by_id(institute_id)

        name = self._validate_name(
            name, institute_id, specialty_id
        )

        specialty.name = name
        specialty.institute_id = institute_id

        self._commit()

        return specialty

    def delete(self, specialty_id: int) -> None:
        specialty = self.get_by_id(specialty_id)

        db.session.delete(specialty)
        self._commit()

    def _validate_name(
        self,
        name: str,
        institute_id: int,
        specialty_id: int | None = None
    ) -> str:

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Введіть назву спеціальності.")

        name = name.strip()

        if len(name) > 100:
            raise ValueError(
                "Назва не може перевищувати 100 символів."
            )

        existing = Specialty.query.filter_by(
            name=name,
            institute_id=institute_id
        ).first()

        if existing is not None and existing.id != specialty_id:
            raise ValueError(
                "Така спеціальність уже існує в цьому інституті."
            )

        return name

    def _commit(self) -> None:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


class AcademicGroupService:

    def get_all(
        self,
        specialty_id: int | None = None,
        course: int | None = None
    ) -> list[AcademicGroup]:

        query = db.session.query(AcademicGroup)

        if specialty_id is not None:
            query = query.filter_by(specialty_id=specialty_id)

        if course is not None:
            query = query.filter_by(course=course)

        return query.order_by(AcademicGroup.name).all()

    def get_by_id(self, group_id: int) -> AcademicGroup:
        return get_required(
            AcademicGroup, group_id,
            "Академічну групу не знайдено."
        )

    def create(
        self, name: str, course: int, specialty_id: int
    ) -> AcademicGroup:

        name = self._validate(name, course, specialty_id)

        group = AcademicGroup(
            name=name,
            course=course,
            specialty_id=specialty_id
        )

        db.session.add(group)
        commit()

        return group

    def update(
        self, group_id: int, name: str,
        course: int, specialty_id: int
    ) -> AcademicGroup:

        group = self.get_by_id(group_id)

        name = self._validate(
            name, course, specialty_id, group_id
        )

        group.name = name
        group.course = course
        group.specialty_id = specialty_id

        commit()

        return group

    def delete(self, group_id: int) -> None:
        group = self.get_by_id(group_id)

        db.session.delete(group)
        commit()

    def add_subject(self, group_id: int, subject_id: int):
        group = self.get_by_id(group_id)

        subject = get_required(
            Subject, subject_id, "Дисципліну не знайдено."
        )

        if subject not in group.subjects:
            group.subjects.append(subject)
            commit()

    def remove_subject(self, group_id: int, subject_id: int):
        group = self.get_by_id(group_id)

        subject = get_required(
            Subject, subject_id, "Дисципліну не знайдено."
        )

        if subject not in group.subjects:
            raise ValueError("Група не вивчає цю дисципліну.")

        for entry in list(group.schedule_entries):
            if entry.subject_id == subject_id:
                db.session.delete(entry)

        for student in list(group.students):
            for grade in list(student.grades):
                if grade.subject_id == subject_id:
                    db.session.delete(grade)

        group.subjects.remove(subject)
        commit()

    def _validate(
        self, name, course, specialty_id, group_id=None
    ):
        name = validate_text(name, "Назва групи", 50)

        SpecialtyService().get_by_id(specialty_id)

        if type(course) is not int or course < 1:
            raise ValueError("Курс має бути додатним цілим числом.")

        existing = AcademicGroup.query.filter_by(
            name=name,
            specialty_id=specialty_id
        ).first()

        if existing is not None and existing.id != group_id:
            raise ValueError("Така академічна група вже існує.")

        return name
