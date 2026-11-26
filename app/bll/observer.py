from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.dal.database import db
from app.dal.models import Notification


@dataclass(frozen=True)
class Event:
    event_type: str
    data: dict[str, Any]


class Observer(ABC):
    @abstractmethod
    def update(self, event: Event) -> None:
        raise NotImplementedError


class EventManager:

    def __init__(self):
        self._observers = []

    def subscribe(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, **data) -> None:
        event = Event(event_type=event_type, data=data)
        for observer in list(self._observers):
            observer.update(event)


class NotificationObserver(Observer):

    def update(self, event: Event) -> None:
        handler = getattr(self, f"_on_{event.event_type}", None)
        if handler is not None:
            handler(**event.data)

    @staticmethod
    def _add(title: str, message: str, event_type: str) -> None:
        db.session.add(Notification(
            title=title,
            message=message,
            event_type=event_type,
        ))

    def _on_teacher_deleted(
        self, teacher_name: str, group_subjects: list, freed_slots: list
    ) -> None:
        for item in group_subjects:
            subjects = ", ".join(f"«{name}»" for name in item["subjects"])
            self._add(
                "Зміни в навчальному плані",
                (
                    f"Після видалення викладача «{teacher_name}» "
                    f"група «{item['group_name']}» втратила дисципліни: "
                    f"{subjects}. Створіть потрібні дисципліни з іншим "
                    "викладачем і призначте їх групі."
                ),
                "teacher_deleted",
            )

        for slot in freed_slots:
            self._add_freed_slot(
                slot,
                (
                    f"Після видалення викладача «{teacher_name}» "
                    "у розкладі звільнився час."
                ),
            )

    def _on_subject_removed(
        self, subject_name: str, groups: list, freed_slots: list
    ) -> None:
        for group_name in groups:
            self._add(
                "Зміни в навчальному плані",
                (
                    f"Група «{group_name}» більше не вивчає дисципліну "
                    f"«{subject_name}». Перевірте навчальний план і за "
                    "потреби призначте іншу дисципліну."
                ),
                "subject_removed",
            )

        for slot in freed_slots:
            self._add_freed_slot(
                slot,
                f"Після видалення дисципліни «{subject_name}» у розкладі звільнився час.",
            )

    def _on_subject_assigned(
        self, group_name: str, subject_name: str
    ) -> None:
        self._add(
            "Зміни в навчальному плані",
            (
                f"Групі «{group_name}» призначено дисципліну "
                f"«{subject_name}». Перевірте, чи потрібно додати "
                "відповідне заняття до розкладу."
            ),
            "subject_assigned",
        )

    def _on_schedule_slot_freed(
        self, slot: dict, reason: str
    ) -> None:
        self._add_freed_slot(slot, reason)

    def _add_freed_slot(self, slot: dict, reason: str) -> None:
        classroom = f", аудиторія {slot['classroom']}" if slot.get("classroom") else ""
        subject = f" — «{slot['subject_name']}»" if slot.get("subject_name") else ""
        self._add(
            "Вільний час у розкладі",
            (
                f"{reason} Група «{slot['group_name']}»: "
                f"{slot['day_name']}, {slot['start_time']}–{slot['end_time']}"
                f"{classroom}{subject}. Цей час можна використати для іншого заняття."
            ),
            "schedule_slot_freed",
        )


event_manager = EventManager()
event_manager.subscribe(NotificationObserver())


def publish_event(event_type: str, **data) -> None:
    event_manager.notify(event_type, **data)


def schedule_slot_data(entry) -> dict:
    return {
        "group_name": entry.group.name,
        "subject_name": entry.subject.name,
        "day_name": entry.day_name,
        "start_time": entry.start_time.strftime("%H:%M"),
        "end_time": entry.end_time.strftime("%H:%M"),
        "classroom": entry.classroom,
    }
