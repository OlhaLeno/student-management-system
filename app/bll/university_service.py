
from app.dal.database import db
from app.dal.models import Institute


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

        if institute.specialties:
            raise ValueError(
                "Неможливо видалити інститут, "
                "до якого належать спеціальності."
            )

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
