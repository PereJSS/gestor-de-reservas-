from notifications.apps import Config as NotificationsConfig
from schedule.apps import ScheduleConfig


class ScheduleFriendlyConfig(ScheduleConfig):
    verbose_name = "Agenda"


class NotificationsFriendlyConfig(NotificationsConfig):
    verbose_name = "Notificaciones"
