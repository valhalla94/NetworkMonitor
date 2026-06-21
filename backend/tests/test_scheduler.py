import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import socket
import ssl

from scheduler import check_ssl_expiry

@patch("scheduler.datetime")
@patch("scheduler.socket.create_connection")
@patch("scheduler.ssl.create_default_context")
def test_check_ssl_expiry_valid_cert(mock_ssl_context, mock_create_connection, mock_datetime):
    # Setup mock current time
    mock_now = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.utcnow.return_value = mock_now
    # We also need to let strptime pass through to the real datetime
    mock_datetime.strptime.side_effect = datetime.strptime

    # Setup mock cert with expiry in 10 days
    expiry_date = mock_now + timedelta(days=10)
    mock_cert = {
        "notAfter": expiry_date.strftime("%b %d %H:%M:%S %Y GMT")
    }

    mock_context_instance = MagicMock()
    mock_ssl_context.return_value = mock_context_instance

    mock_sock = MagicMock()
    mock_create_connection.return_value.__enter__.return_value = mock_sock

    mock_ssock = MagicMock()
    mock_context_instance.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_ssock.getpeercert.return_value = mock_cert

    # Call function
    days = check_ssl_expiry("example.com", 443)

    # Verify
    assert days == 10
    mock_create_connection.assert_called_once_with(("example.com", 443), timeout=5)
    mock_context_instance.wrap_socket.assert_called_once_with(mock_sock, server_hostname="example.com")


@patch("scheduler.datetime")
@patch("scheduler.socket.create_connection")
@patch("scheduler.ssl.create_default_context")
def test_check_ssl_expiry_expired_cert(mock_ssl_context, mock_create_connection, mock_datetime):
    # Setup mock current time
    mock_now = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.utcnow.return_value = mock_now
    mock_datetime.strptime.side_effect = datetime.strptime

    # Setup mock cert with expiry 5 days ago
    expiry_date = mock_now - timedelta(days=5)
    mock_cert = {
        "notAfter": expiry_date.strftime("%b %d %H:%M:%S %Y GMT")
    }

    mock_context_instance = MagicMock()
    mock_ssl_context.return_value = mock_context_instance

    mock_sock = MagicMock()
    mock_create_connection.return_value.__enter__.return_value = mock_sock

    mock_ssock = MagicMock()
    mock_context_instance.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_ssock.getpeercert.return_value = mock_cert

    # Call function
    days = check_ssl_expiry("example.com", 443)

    # Verify
    assert days == -5


@patch("scheduler.socket.create_connection")
def test_check_ssl_expiry_connection_error(mock_create_connection):
    mock_create_connection.side_effect = socket.timeout("Connection timed out")

    # Call function
    days = check_ssl_expiry("example.com", 443)

    # Verify
    assert days is None


@patch("scheduler.socket.create_connection")
@patch("scheduler.ssl.create_default_context")
def test_check_ssl_expiry_cert_parse_error(mock_ssl_context, mock_create_connection):
    mock_context_instance = MagicMock()
    mock_ssl_context.return_value = mock_context_instance

    mock_sock = MagicMock()
    mock_create_connection.return_value.__enter__.return_value = mock_sock

    mock_ssock = MagicMock()
    mock_context_instance.wrap_socket.return_value.__enter__.return_value = mock_ssock
    # Invalid date format to trigger exception
    mock_ssock.getpeercert.return_value = {"notAfter": "invalid-date"}

    # Call function
    days = check_ssl_expiry("example.com", 443)

    # Verify
    assert days is None
