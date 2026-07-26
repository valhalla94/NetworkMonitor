import pytest
import models


# We need to import client fixture to ensure DB gets initialized before main
def test_audit_logs_created_successfully(client, db_session):
    from main import _audit

    user = "admin"
    action = "CREATE_HOST"
    target = "Host1"
    details = "Created host 10.0.0.1"

    # Call the function
    _audit(db_session, user=user, action=action, target=target, details=details)

    # Verify the log was added
    log = (
        db_session.query(models.AuditLogDB)
        .filter(models.AuditLogDB.user == user, models.AuditLogDB.action == action)
        .first()
    )

    assert log is not None
    assert log.user == user
    assert log.action == action
    assert log.target == target
    assert log.details == details


def test_audit_logs_default_details(client, db_session):
    from main import _audit

    user = "test_user"
    action = "DELETE_HOST"
    target = "Host2"

    # Call the function without details
    _audit(db_session, user=user, action=action, target=target)

    # Verify the log was added
    log = (
        db_session.query(models.AuditLogDB)
        .filter(models.AuditLogDB.user == user, models.AuditLogDB.action == action)
        .first()
    )

    assert log is not None
    assert log.user == user
    assert log.action == action
    assert log.target == target
    assert log.details == ""
