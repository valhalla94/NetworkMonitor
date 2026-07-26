import pytest
from unittest.mock import Mock, patch
from notifications import NotificationManager


def test_load_config_with_valid_setting():
    manager = NotificationManager()
    manager.apobj = Mock()

    db_session = Mock()
    mock_setting = Mock()
    mock_setting.value = "mailto://test:test@example.com"

    db_session.query.return_value.filter.return_value.first.return_value = mock_setting

    manager.load_config(db_session)

    manager.apobj.clear.assert_called_once()
    manager.apobj.add.assert_called_once_with("mailto://test:test@example.com")


def test_load_config_without_setting():
    manager = NotificationManager()
    manager.apobj = Mock()

    db_session = Mock()
    db_session.query.return_value.filter.return_value.first.return_value = None

    manager.load_config(db_session)

    manager.apobj.clear.assert_called_once()
    manager.apobj.add.assert_not_called()


def test_load_config_exception():
    manager = NotificationManager()
    manager.apobj = Mock()

    db_session = Mock()
    db_session.query.side_effect = Exception("DB error")

    # Should not raise exception
    manager.load_config(db_session)


def test_send_notification_not_configured():
    manager = NotificationManager()
    # Set apobj to None or False-y value to trigger the not configured check properly
    manager.apobj = None

    manager.send_notification("Test Title", "Test Body")
    # if it's None we don't have notify to check, but we know it returned early


def test_send_notification_success():
    manager = NotificationManager()
    manager.apobj = Mock()
    manager.apobj.notify.return_value = True

    manager.send_notification("Test Title", "Test Body")
    manager.apobj.notify.assert_called_once_with(title="Test Title", body="Test Body")


def test_send_notification_failure():
    manager = NotificationManager()
    manager.apobj = Mock()
    manager.apobj.notify.return_value = False

    manager.send_notification("Test Title", "Test Body")
    manager.apobj.notify.assert_called_once_with(title="Test Title", body="Test Body")


def test_send_notification_exception():
    manager = NotificationManager()
    manager.apobj = Mock()
    manager.apobj.notify.side_effect = Exception("Apprise error")

    # Should not raise
    manager.send_notification("Test Title", "Test Body")
    manager.apobj.notify.assert_called_once_with(title="Test Title", body="Test Body")
