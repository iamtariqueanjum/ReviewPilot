"""Unit tests for API Client."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from requests.exceptions import HTTPError
from app.core.api.client import APIClient


class TestAPIClient:
    """Test suite for APIClient."""

    def test_init_default_retries(self):
        """Test APIClient initialization with default retries."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants:
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            
            client = APIClient()
            
            assert client.base_url == "http://localhost:8000"
            assert client.timeout == 60
            assert client.session is not None
            assert client.adapter is not None

    def test_init_custom_retries(self):
        """Test APIClient initialization with custom retries."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants:
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            
            client = APIClient(retries=5, timeout=30)
            
            assert client.timeout == 30

    def test_request_success(self):
        """Test successful API request."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "success"}
            mock_session.request.return_value = mock_response
            
            client = APIClient()
            client.session = mock_session
            
            response = client.request("GET", "/api/test")
            
            assert response.status_code == 200
            mock_session.request.assert_called_once()

    def test_call_api_success(self):
        """Test successful API call with response parsing."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "success"}
            mock_session.request.return_value = mock_response
            
            client = APIClient()
            client.session = mock_session
            
            result = client.call_api("GET", "/api/test")
            
            assert result["status_code"] == 200
            assert result["body"]["result"] == "success"

    def test_call_api_with_text_response(self):
        """Test API call with text response."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError()
            mock_response.text = "Plain text response"
            mock_session.request.return_value = mock_response
            
            client = APIClient()
            client.session = mock_session
            
            result = client.call_api("GET", "/api/test")
            
            assert result["status_code"] == 200
            assert result["body"] == "Plain text response"

    def test_call_api_http_error(self):
        """Test API call handling of HTTP errors."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
            
            error = HTTPError("404 Not Found")
            error.response = mock_response
            mock_session.request.side_effect = error
            
            client = APIClient()
            client.session = mock_session
            
            result = client.call_api("GET", "/api/test")
            
            assert result["status_code"] == 404

    def test_call_api_with_kwargs(self):
        """Test API call with additional kwargs."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "success"}
            mock_session.request.return_value = mock_response
            
            client = APIClient()
            client.session = mock_session
            
            result = client.call_api(
                "POST",
                "/api/test",
                json={"key": "value"},
                params={"filter": "active"}
            )
            
            assert result["status_code"] == 200

    def test_request_with_timeout(self):
        """Test request with custom timeout."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response
            
            client = APIClient()
            client.session = mock_session
            
            response = client.request("GET", "/api/test", timeout=5)
            
            # Verify timeout was passed
            call_kwargs = mock_session.request.call_args[1]
            assert call_kwargs["timeout"] == 5

    def test_request_with_custom_headers(self):
        """Test request with custom headers."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants, \
             patch('app.core.api.client.requests.Session') as mock_session_class:
            
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response
            
            client = APIClient()
            client.session = mock_session
            
            custom_headers = {"Authorization": "Bearer token123"}
            response = client.request("GET", "/api/test", headers=custom_headers)
            
            # Verify custom headers were used
            call_kwargs = mock_session.request.call_args[1]
            assert call_kwargs["headers"] == custom_headers

    def test_retry_strategy_configuration(self):
        """Test retry strategy is configured correctly."""
        with patch('app.core.api.client.ConfigConstants') as mock_constants:
            mock_constants.INTERNAL_API.value = "http://localhost:8000"
            
            client = APIClient(retries=3)
            
            assert client.retry_strategy.total == 3
            assert client.retry_strategy.backoff_factor == 0.3
            assert 429 in client.retry_strategy.status_forcelist
            assert 500 in client.retry_strategy.status_forcelist

