# SonarQube Integration

## Overview

SonarQube integration for continuous code quality and security analysis.

## Features

- Code quality analysis
- Security vulnerability detection
- Code coverage tracking
- Technical debt measurement
- Quality gate enforcement

## Setup Options

### Option 1: SonarCloud (Free for Public Repos)

1. Go to https://sonarcloud.io
2. Sign in with GitHub
3. Add organization: red9inja
4. Import repository: red9inja-GPT
5. Get token from Account → Security

### Option 2: Self-Hosted SonarQube

Deploy on EKS:

```bash
# Create secrets
kubectl create secret generic sonarqube-secrets \
  --from-literal=db-username=sonarqube \
  --from-literal=db-password=YOUR_PASSWORD \
  -n monitoring

# Deploy SonarQube
kubectl apply -f k8s/sonarqube.yaml

# Get URL
kubectl get service sonarqube -n monitoring
```

## GitHub Secrets Required

Add to repository secrets:

1. **SONAR_TOKEN**
   - Get from SonarQube: Administration → Security → Users → Tokens
   - Or SonarCloud: Account → Security → Generate Token

2. **SONAR_HOST_URL**
   - SonarCloud: https://sonarcloud.io
   - Self-hosted: http://SONARQUBE_LB_URL

## Configuration

### sonar-project.properties

```properties
sonar.projectKey=red9inja-gpt
sonar.projectName=Red9inja GPT
sonar.sources=model,api,auth,database,utils
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
```

## Workflow

Automatic scan on:
- Push to any branch
- Pull requests

```yaml
name: SonarQube Code Analysis
on:
  push:
    branches: [main, dev, test, staging, prod]
  pull_request:
    types: [opened, synchronize, reopened]
```

## Quality Metrics

### Reliability
- Bugs: 0 target
- Rating: A

### Security
- Vulnerabilities: 0 target
- Security Hotspots: Review all
- Rating: A

### Maintainability
- Code Smells: < 50
- Technical Debt: < 5%
- Rating: A

### Coverage
- Line Coverage: > 80%
- Branch Coverage: > 70%

### Duplications
- Duplication: < 3%

## Quality Gate

Default conditions:
- Coverage on New Code: > 80%
- Duplicated Lines on New Code: < 3%
- Maintainability Rating on New Code: A
- Reliability Rating on New Code: A
- Security Rating on New Code: A

## Dashboard

### SonarCloud
https://sonarcloud.io/dashboard?id=red9inja-gpt

### Self-Hosted
http://SONARQUBE_URL/dashboard?id=red9inja-gpt

## Metrics Tracked

### Code Quality
- Lines of Code
- Complexity
- Cognitive Complexity
- Duplications

### Reliability
- Bugs
- Code Smells
- Technical Debt

### Security
- Vulnerabilities
- Security Hotspots
- Security Review Rating

### Coverage
- Line Coverage
- Branch Coverage
- Uncovered Lines

## Integration with CI/CD

```
Code Push
    ↓
Run Tests with Coverage
    ↓
SonarQube Scan
    ↓
Quality Gate Check
    ↓
Pass: Continue Deployment
Fail: Block Deployment
```

## Local Analysis

Run locally before pushing:

```bash
# Install SonarScanner
brew install sonar-scanner  # macOS
# or download from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

# Run analysis
sonar-scanner \
  -Dsonar.projectKey=red9inja-gpt \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN
```

## Common Issues

### Issue: Coverage not showing
**Solution:** Ensure coverage.xml is generated:
```bash
pytest tests/ --cov=. --cov-report=xml
```

### Issue: Quality gate failing
**Solution:** Check specific conditions:
```bash
# View issues
sonar-scanner -Dsonar.verbose=true
```

### Issue: Authentication failed
**Solution:** Verify SONAR_TOKEN is correct and has permissions

## Best Practices

1. **Fix issues before merging**
   - Review all new issues
   - Prioritize security vulnerabilities
   - Address code smells

2. **Maintain coverage**
   - Write tests for new code
   - Aim for > 80% coverage
   - Test edge cases

3. **Reduce technical debt**
   - Refactor complex code
   - Remove duplications
   - Follow coding standards

4. **Security first**
   - Fix all vulnerabilities
   - Review security hotspots
   - Use secure coding practices

## Reports

### Available Reports
- Issues Report
- Security Report
- Coverage Report
- Duplications Report
- Complexity Report

### Export Reports
```bash
# From SonarQube UI
Project → More → Export
```

## Cost

### SonarCloud
- Public repos: Free
- Private repos: $10/month per 100K LOC

### Self-Hosted
- Community Edition: Free
- Developer Edition: $150/year
- Enterprise Edition: $15,000/year

## Monitoring

### Alerts
- Quality gate failed
- New vulnerabilities
- Coverage decreased
- Technical debt increased

### Notifications
- Email notifications
- Slack integration
- Webhook support

## Documentation

- SonarQube Docs: https://docs.sonarqube.org
- SonarCloud Docs: https://sonarcloud.io/documentation
- Python Analysis: https://docs.sonarqube.org/latest/analysis/languages/python/

## Support

For issues:
- Check SonarQube logs
- Review workflow logs
- Verify configuration
- Check GitHub Actions status
