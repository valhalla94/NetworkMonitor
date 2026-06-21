import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, RequestException
import time

from scheduler import check_http

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
