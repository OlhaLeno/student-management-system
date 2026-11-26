from app.bll.notification_service import NotificationService
from app.pl.api_utils import make_api


notifications_api = make_api("notifications_api", __name__)


def notification_to_dict(notification):
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "event_type": notification.event_type,
        "is_read": notification.is_read,
        "created_at": notification.created_at.strftime("%d.%m.%Y %H:%M"),
    }


@notifications_api.get("/notifications")
def notifications():
    service = NotificationService()
    return [notification_to_dict(item) for item in service.get_all(limit=50)]


@notifications_api.patch("/notifications/read-all")
def mark_all_notifications_as_read():
    NotificationService().mark_all_as_read()
    return {"message": "Усі сповіщення позначено прочитаними."}


@notifications_api.patch("/notifications/<int:notification_id>/read")
def mark_notification_as_read(notification_id):
    notification = NotificationService().mark_as_read(notification_id)
    return notification_to_dict(notification)
