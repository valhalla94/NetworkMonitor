import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import socket
import ssl
from requests.exceptions import Timeout, RequestException
import time

from scheduler import check_ssl_expiry, check_http

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


def test_check_http_success():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # simulate time taken to sleep
        with patch("time.time", side_effect=[0, 0.1]):
            is_up, latency, status_code = check_http("http://example.com", expected_status=200, timeout=5)

        assert is_up is True
        assert latency == 100.0
        assert status_code == 200
        mock_get.assert_called_once_with("http://example.com", timeout=5)

def test_check_http_timeout():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Timeout("Request timed out")

        is_up, latency, status_code = check_http("http://example.com", expected_status=200, timeout=5)

        assert is_up is False
        assert latency == -1.0
        assert status_code == 0
        mock_get.assert_called_once_with("http://example.com", timeout=5)

def test_check_http_unexpected_status_code():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with patch("time.time", side_effect=[0, 0.05]):
            is_up, latency, status_code = check_http("http://example.com", expected_status=200, timeout=5)

        assert is_up is False
        assert latency == 50.0
        assert status_code == 404
        mock_get.assert_called_once_with("http://example.com", timeout=5)

def test_check_http_exception():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = RequestException("Some error")

        is_up, latency, status_code = check_http("http://example.com", expected_status=200, timeout=5)

        assert is_up is False
        assert latency == -1.0
        assert status_code == 0
        mock_get.assert_called_once_with("http://example.com", timeout=5)

def test_check_http_url_formatting():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with patch("time.time", side_effect=[0, 0.1]):
            is_up, latency, status_code = check_http("example.com", expected_status=200, timeout=5)

        assert is_up is True
        assert latency == 100.0
        assert status_code == 200
        mock_get.assert_called_once_with("http://example.com", timeout=5)
