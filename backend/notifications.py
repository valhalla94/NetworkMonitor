from apprise import Apprise
import logging
from sqlalchemy.orm import Session
from models import SettingsDB

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.apobj = Apprise()
        self.config_id = None

    def load_config(self, db: Session):
        """
        Loads the notification URL from the database.
        """
        try:
            setting = db.query(SettingsDB).filter(SettingsDB.key == "notification_url").first()
            if setting and setting.value:
                # Clear existing configuration
                self.apobj.clear()
                # Add the new configuration
                self.apobj.add(setting.value)
                logger.info("Notification configuration loaded/updated.")
            else:
                logger.info("No notification URL configured.")
                self.apobj.clear()
        except Exception as e:
            logger.error(f"Failed to load notification config: {e}")

    def send_notification(self, title: str, body: str):
        """
        Sends a notification.
        """
        if not self.apobj:
             logger.warning("Notification Manager not configured. Skipping.")
             return

        try:
            status = self.apobj.notify(
                body=body,
                title=title,
            )
            if status:
                logger.info(f"Notification sent: {title}")
            else:
                logger.warning(f"Failed to send notification: {title}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

notification_manager = NotificationManager()
