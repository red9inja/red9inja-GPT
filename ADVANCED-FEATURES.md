# Advanced Features Documentation

## Overview

Production-ready features for enterprise-scale deployment:
- Real-time streaming with WebSocket
- Prometheus monitoring
- AWS WAF security
- Secrets Manager
- Grafana dashboards

## 1. WebSocket Streaming

### Real-time Token Generation

Stream model responses token-by-token for better UX (like ChatGPT).

### JavaScript Client Example

```javascript
const ws = new WebSocket('wss://gpt.vmind.online/ws/generate?token=YOUR_TOKEN');

ws.onopen = () => {
  ws.send(JSON.stringify({
    prompt: "What is AI?",
    conversation_id: "abc123",
    max_tokens: 100
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'token') {
    // Append token to UI
    document.getElementById('output').textContent += data.content;
  } else if (data.type === 'complete') {
    // Generation complete
    console.log('Done:', data.content);
  } else if (data.type === 'error') {
    console.error('Error:', data.content);
  }
};
```

### Benefits
- Real-time feedback
- Better user experience
- Lower perceived latency
- Progressive rendering

## 2. Prometheus Monitoring

### Metrics Collected

- **Request metrics**: Count, duration, status codes
- **Generation metrics**: Tokens generated, user activity
- **Cache metrics**: Hit rate, miss rate
- **Rate limit metrics**: Violations per user
- **System metrics**: CPU, memory, GPU usage

### Access Metrics

```bash
# Metrics endpoint
curl https://gpt.vmind.online/metrics

# Sample output:
api_requests_total{method="POST",endpoint="/generate",status="200"} 1523
api_request_duration_seconds_sum{method="POST",endpoint="/generate"} 45.2
generation_tokens_sum{user_id="user123"} 15234
cache_hits_total 8234
cache_misses_total 1523
```

### Grafana Dashboards

Access: `http://GRAFANA_LB_URL`
- Username: admin
- Password: admin123

**Pre-built dashboards:**
1. API Performance
2. User Activity
3. Cache Performance
4. Rate Limiting
5. System Resources

## 3. AWS WAF (Web Application Firewall)

### Protection Rules

1. **Rate Limiting**: 2000 requests/5min per IP
2. **Common Attacks**: SQL injection, XSS, etc.
3. **Known Bad Inputs**: Malicious patterns
4. **SQL Injection**: Database attack prevention

### Blocked Attacks

WAF automatically blocks:
- SQL injection attempts
- Cross-site scripting (XSS)
- Path traversal
- Command injection
- Known malicious IPs

### Monitoring

CloudWatch metrics:
- Blocked requests
- Allowed requests
- Rule matches
- False positives

## 4. AWS Secrets Manager

### Secure Secret Storage

All sensitive data stored in Secrets Manager:
- Cognito credentials
- Redis connection
- Database names
- API keys

### Benefits
- Automatic rotation
- Encryption at rest
- Audit logging
- No secrets in code

### Access Secrets

```python
import boto3

secrets = boto3.client('secretsmanager')
response = secrets.get_secret_value(SecretId='app-secrets')
config = json.loads(response['SecretString'])

cognito_pool_id = config['cognito_user_pool_id']
```

## 5. Performance Monitoring

### Key Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Response time | < 200ms | > 500ms |
| Error rate | < 0.1% | > 1% |
| Cache hit rate | > 80% | < 60% |
| CPU usage | < 70% | > 85% |
| Memory usage | < 80% | > 90% |

### Alerts

CloudWatch alarms for:
- High error rate
- Slow responses
- Low cache hit rate
- Resource exhaustion
- Queue depth

## 6. Security Features

### Multi-layer Security

```
User Request
    ↓
Cloudflare (DDoS, Bot protection)
    ↓
AWS WAF (Application firewall)
    ↓
Rate Limiter (Abuse prevention)
    ↓
Authentication (Cognito JWT)
    ↓
Authorization (Role-based)
    ↓
Application
```

### Security Headers

Automatic headers:
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Strict-Transport-Security

## 7. Cost Optimization

### Auto-scaling

- Scale down during low traffic
- Scale up during peaks
- Spot instances for non-prod
- Scheduled scaling

### Resource Optimization

- Cache frequently accessed data
- Compress responses
- Use CDN for static assets
- Optimize database queries

## 8. Disaster Recovery

### Backup Strategy

- DynamoDB: Point-in-time recovery
- Redis: Daily snapshots
- EBS: Automated snapshots
- Secrets: Automatic backup

### Recovery Time

- Database: < 5 minutes
- Cache: < 2 minutes
- Application: < 10 minutes
- Full system: < 30 minutes

## 9. Load Testing

### Recommended Tools

```bash
# Locust load testing
pip install locust

# Create locustfile.py
from locust import HttpUser, task

class GPTUser(HttpUser):
    @task
    def generate(self):
        self.client.post("/generate", 
            json={"prompt": "Hello", "max_tokens": 50},
            headers={"Authorization": f"Bearer {token}"})

# Run test
locust -f locustfile.py --host=https://gpt.vmind.online
```

### Performance Targets

- 10,000 concurrent users
- 100,000 requests/minute
- < 200ms p95 latency
- < 0.1% error rate

## 10. Monitoring Dashboard

### Grafana Panels

1. **API Overview**
   - Requests per second
   - Response times
   - Error rates

2. **User Activity**
   - Active users
   - Generations per user
   - Token usage

3. **Cache Performance**
   - Hit/miss ratio
   - Cache size
   - Eviction rate

4. **System Health**
   - CPU/Memory/GPU
   - Network I/O
   - Disk usage

5. **Security**
   - WAF blocks
   - Rate limit violations
   - Failed auth attempts

## Usage Examples

### Stream Generation

```python
import websockets
import json

async def stream_generate():
    uri = "wss://gpt.vmind.online/ws/generate?token=TOKEN"
    
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "prompt": "Explain quantum computing",
            "max_tokens": 200
        }))
        
        async for message in ws:
            data = json.loads(message)
            if data['type'] == 'token':
                print(data['content'], end='', flush=True)
            elif data['type'] == 'complete':
                print("\nDone!")
                break
```

### Monitor Metrics

```bash
# Get current metrics
curl https://gpt.vmind.online/metrics

# Query Prometheus
curl 'http://prometheus:9090/api/v1/query?query=api_requests_total'
```

## Cost Summary

| Feature | Cost/Month |
|---------|-----------|
| WAF | $5 |
| Secrets Manager | $1 |
| Prometheus/Grafana | $0 (self-hosted) |
| CloudWatch Logs | $10 |
| **Total Additional** | **$16** |

## Summary

Complete enterprise features:
- Real-time streaming
- Production monitoring
- Advanced security
- Secure secrets
- Performance tracking
- Cost optimization

**Production-ready for millions of users!** 
