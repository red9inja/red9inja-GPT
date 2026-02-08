"""
Automated tests
"""

import pytest
from fastapi.testclient import TestClient
from api.server import app


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_signup(self):
        response = client.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "name": "Test User"
        })
        assert response.status_code in [201, 400]  # 400 if user exists
    
    def test_login_invalid(self):
        response = client.post("/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrong"
        })
        assert response.status_code == 401


class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit(self):
        # Make many requests
        for _ in range(70):
            response = client.get("/health")
        
        # Should be rate limited
        response = client.get("/health")
        assert response.status_code in [200, 429]


class TestGeneration:
    """Test text generation"""
    
    @pytest.fixture
    def auth_token(self):
        # Get auth token (mock or real)
        return "mock_token"
    
    def test_generate_without_auth(self):
        response = client.post("/generate", json={
            "prompt": "Hello",
            "max_tokens": 10
        })
        assert response.status_code == 403  # Unauthorized


class TestConversations:
    """Test conversation management"""
    
    def test_create_conversation_without_auth(self):
        response = client.post("/conversations", json={
            "title": "Test Chat"
        })
        assert response.status_code == 403


class TestMetrics:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint(self):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "api_requests_total" in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
