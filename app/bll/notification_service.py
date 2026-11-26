from app.dal.database import db
from app.dal.models import Notification
from app.bll.service_utils import get_required, commit


class NotificationService:

    def get_all(self, limit: int = 10) -> list[Notification]:
        return db.session.query(Notification).order_by(
            Notification.created_at.desc(),
            Notification.id.desc()
        ).limit(limit).all()

    def get_unread_count(self) -> int:
        return db.session.query(Notification).filter_by(
            is_read=False
        ).count()

    def mark_as_read(self, notification_id: int) -> Notification:
        notification = get_required(
            Notification, notification_id, "Сповіщення не знайдено."
        )

        if not notification.is_read:
            notification.is_read = True
            commit()

        return notification

    def mark_all_as_read(self) -> None:
        db.session.query(Notification).filter_by(
            is_read=False
        ).update(
            {"is_read": True},
            synchronize_session=False
        )
        commit()
