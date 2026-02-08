"""
Load testing with Locust
"""

from locust import HttpUser, task, between
import random


class GPTUser(HttpUser):
    """Simulate GPT API user"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login on start"""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
        else:
            self.token = None
    
    @task(3)
    def generate_text(self):
        """Generate text (most common operation)"""
        if not self.token:
            return
        
        prompts = [
            "What is artificial intelligence?",
            "Explain quantum computing",
            "Write a poem about nature",
            "How does machine learning work?",
            "Tell me about space exploration"
        ]
        
        self.client.post(
            "/generate",
            json={
                "prompt": random.choice(prompts),
                "max_tokens": 100
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def list_conversations(self):
        """List conversations"""
        if not self.token:
            return
        
        self.client.get(
            "/conversations",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def health_check(self):
        """Health check"""
        self.client.get("/health")


class AdminUser(HttpUser):
    """Simulate admin user"""
    
    wait_time = between(5, 10)
    
    @task
    def list_users(self):
        """List all users (admin only)"""
        self.client.get(
            "/auth/users",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )


# Run with: locust -f tests/load_test.py --host=https://gpt.vmind.online
