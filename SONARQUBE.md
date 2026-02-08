# SonarQube Integration - Complete Guide

## Overview

Automated code quality and security analysis using self-hosted SonarQube on AWS EKS with complete CI/CD integration.

## Architecture

```
CODE PUSH
    |
    v
GITHUB ACTIONS (SonarQube Workflow)
    |
    v
RUN TESTS WITH COVERAGE
    |
    v
SONARQUBE SCANNER
    |
    v
SEND RESULTS TO SONARQUBE SERVER (EKS)
    |
    v
SONARQUBE ANALYSIS
    |
    +-- Code Quality Check
    +-- Security Scan
    +-- Coverage Analysis
    +-- Duplicate Detection
    |
    v
QUALITY GATE CHECK
    |
    +-- Pass: Continue
    +-- Fail: Block (optional)
    |
    v
PR COMMENT WITH RESULTS
```

## Infrastructure Components

### 1. RDS Database (PostgreSQL)
- Instance: db.t3.small
- Storage: 20GB (auto-scales to 100GB)
- Engine: PostgreSQL 13
- Encrypted: Yes
- Backups: 7 days retention
- Multi-AZ: Optional

### 2. EKS Deployment
- Namespace: sonarqube
- Image: sonarqube:10-community
- Resources: 2-4GB RAM, 1-2 CPU
- Storage: 10GB data + 5GB extensions
- Service: Load Balancer

### 3. GitHub Actions
- Deploy workflow (one-time)
- Analysis workflow (automatic)
- PR comment integration

## Complete Setup Flow

```
STEP 1: INFRASTRUCTURE PROVISIONING
Terraform → Create RDS PostgreSQL
         → Configure security groups
         → Store credentials in Secrets Manager

STEP 2: SONARQUBE DEPLOYMENT
GitHub Actions → Get RDS credentials
              → Create Kubernetes namespace
              → Create database secret
              → Deploy SonarQube pod
              → Wait for ready
              → Get Load Balancer URL
              → Generate admin token
              → Create project

STEP 3: GITHUB CONFIGURATION
Add Secrets → SONAR_HOST_URL
           → SONAR_TOKEN

STEP 4: AUTOMATIC ANALYSIS
Code Push → Run tests
         → Generate coverage
         → SonarQube scan
         → Quality gate check
         → PR comment
```

## Deployment Instructions

### Step 1: Deploy Infrastructure

```bash
# Navigate to terraform directory
cd red9inja-GPT-INFRA/terraform

# Initialize and apply
terraform init
terraform apply

# Verify RDS created
terraform output sonarqube_db_endpoint
```

### Step 2: Deploy SonarQube to EKS

**Option A: Automated (GitHub Actions)**

1. Go to: https://github.com/red9inja/red9inja-GPT-INFRA/actions
2. Select: "Deploy SonarQube" workflow
3. Click: "Run workflow"
4. Select environment: dev/test/staging/prod
5. Click: "Run workflow"
6. Wait 5-10 minutes
7. Check workflow output for URL and token

**Option B: Manual Script**

```bash
cd red9inja-GPT-INFRA
./scripts/deploy-sonarqube.sh
```

### Step 3: Configure GitHub Secrets

Add to red9inja-GPT repository:

1. Go to: Settings → Secrets → Actions
2. Add: `SONAR_HOST_URL`
   - Value: http://LOAD_BALANCER_URL (from deployment output)
3. Add: `SONAR_TOKEN`
   - Value: Generated token (from deployment output)

### Step 4: First Login

```
URL: http://LOAD_BALANCER_URL
Username: admin
Password: admin

IMPORTANT: Change password immediately!
```

### Step 5: Verify Setup

```bash
# Check deployment
kubectl get pods -n sonarqube
kubectl get service -n sonarqube

# Check logs
kubectl logs -f deployment/sonarqube -n sonarqube

# Test API
curl http://LOAD_BALANCER_URL/api/system/status
```

## Automatic Code Analysis

### Triggers

**Runs automatically on:**
- Push to: dev, test, staging, prod branches
- Pull requests to: dev, test, staging, prod branches
- Does NOT run on: main branch

### Workflow Steps

```
1. Checkout code
2. Setup Python 3.10
3. Install dependencies
4. Run pytest with coverage
5. Generate coverage.xml
6. SonarQube scan
7. Quality gate check
8. Comment on PR (if applicable)
```

### Example PR Comment

```markdown
## SonarQube Analysis Complete

View detailed report: http://sonarqube-url/dashboard?id=red9inja-gpt

Quality Gate: PASSED

Metrics:
- Bugs: 0
- Vulnerabilities: 0  
- Code Smells: 5
- Coverage: 85.3%
- Duplications: 2.1%
- Technical Debt: 1h 30min
```

## Configuration Files

### sonar-project.properties

```properties
sonar.projectKey=red9inja-gpt
sonar.projectName=Red9inja GPT
sonar.projectVersion=1.0

# Source code
sonar.sources=model,api,auth,database,utils
sonar.tests=tests

# Python specific
sonar.python.version=3.10
sonar.python.coverage.reportPaths=coverage.xml

# Exclusions
sonar.exclusions=**/*_test.py,**/tests/**,**/__pycache__/**

# Quality Gate
sonar.qualitygate.wait=true
```

## Quality Metrics

### Reliability (Bugs)
- **A Rating**: 0 bugs
- **B Rating**: < 1% bug density
- **C Rating**: < 3% bug density
- Target: A Rating

### Security (Vulnerabilities)
- **A Rating**: 0 vulnerabilities
- **B Rating**: < 1% vulnerability density
- **C Rating**: < 3% vulnerability density
- Target: A Rating

### Maintainability (Code Smells)
- **A Rating**: < 5% technical debt ratio
- **B Rating**: < 10% technical debt ratio
- **C Rating**: < 20% technical debt ratio
- Target: A Rating

### Coverage
- **Target**: > 80% line coverage
- **Minimum**: > 70% line coverage
- **New Code**: > 80% coverage

### Duplications
- **Target**: < 3% duplicated lines
- **Maximum**: < 5% duplicated lines

## Quality Gate Configuration

Default conditions for new code:

```
Coverage: > 80%
Duplicated Lines: < 3%
Maintainability Rating: A
Reliability Rating: A
Security Rating: A
Security Hotspots Reviewed: 100%
```

## Dashboard Access

### Main Dashboard
```
http://SONARQUBE_URL/dashboard?id=red9inja-gpt
```

### Key Pages
- **Overview**: http://SONARQUBE_URL/dashboard?id=red9inja-gpt
- **Issues**: http://SONARQUBE_URL/project/issues?id=red9inja-gpt
- **Security**: http://SONARQUBE_URL/security_hotspots?id=red9inja-gpt
- **Measures**: http://SONARQUBE_URL/component_measures?id=red9inja-gpt
- **Code**: http://SONARQUBE_URL/code?id=red9inja-gpt

## Local Analysis

Run SonarQube analysis locally:

```bash
# Install SonarScanner
brew install sonar-scanner  # macOS
# or download from sonarqube.org

# Run analysis
sonar-scanner \
  -Dsonar.projectKey=red9inja-gpt \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://SONARQUBE_URL \
  -Dsonar.login=YOUR_TOKEN

# With coverage
pytest tests/ --cov=. --cov-report=xml
sonar-scanner \
  -Dsonar.projectKey=red9inja-gpt \
  -Dsonar.sources=. \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.host.url=http://SONARQUBE_URL \
  -Dsonar.login=YOUR_TOKEN
```

## Troubleshooting

### Issue: SonarQube pod not starting

```bash
# Check pod status
kubectl describe pod -n sonarqube -l app=sonarqube

# Check logs
kubectl logs -n sonarqube -l app=sonarqube

# Common fix: Increase memory
kubectl edit deployment sonarqube -n sonarqube
# Increase memory limits
```

### Issue: Database connection failed

```bash
# Verify RDS endpoint
terraform output sonarqube_db_endpoint

# Check secret
kubectl get secret sonarqube-db -n sonarqube -o yaml

# Test connection
kubectl run -it --rm debug --image=postgres:13 --restart=Never -- \
  psql -h RDS_ENDPOINT -U sonarqube -d sonarqube
```

### Issue: Quality gate failing

```bash
# View detailed issues
curl -u admin:admin \
  "http://SONARQUBE_URL/api/issues/search?componentKeys=red9inja-gpt"

# Check quality gate status
curl -u admin:admin \
  "http://SONARQUBE_URL/api/qualitygates/project_status?projectKey=red9inja-gpt"
```

### Issue: Coverage not showing

```bash
# Verify coverage.xml exists
ls -la coverage.xml

# Check coverage format
head coverage.xml

# Regenerate coverage
pytest tests/ --cov=. --cov-report=xml --cov-report=html
```

## Cost Breakdown

### AWS Resources
- RDS db.t3.small: $25/month
- EBS volumes (15GB): $2/month
- Load Balancer: $20/month
- Data transfer: $5/month
- **Total**: ~$52/month

### Optimization
- Use Spot instances for non-prod: Save 70%
- Single NAT gateway: Save $45/month
- Reserved instances: Save 30-40%

## Maintenance

### Backup Database

```bash
# Manual backup
kubectl exec -n sonarqube deployment/sonarqube -- \
  pg_dump -h RDS_ENDPOINT -U sonarqube sonarqube > backup.sql

# Restore
kubectl exec -i -n sonarqube deployment/sonarqube -- \
  psql -h RDS_ENDPOINT -U sonarqube sonarqube < backup.sql
```

### Update SonarQube

```bash
# Update image version in k8s/sonarqube.yaml
image: sonarqube:10.3-community

# Apply update
kubectl apply -f k8s/sonarqube.yaml

# Monitor rollout
kubectl rollout status deployment/sonarqube -n sonarqube
```

### Clean Old Data

```bash
# Login to SonarQube
# Go to: Administration → Projects → Management
# Delete old projects or branches
```

## Security Best Practices

1. **Change default password immediately**
2. **Enable force authentication**: Administration → Security
3. **Create separate user accounts** for team members
4. **Use tokens** instead of passwords for CI/CD
5. **Enable HTTPS** (add SSL certificate to Load Balancer)
6. **Restrict access** via security groups
7. **Regular backups** of database
8. **Update regularly** to latest version

## Integration with CI/CD

### Block Deployment on Quality Gate Failure

```yaml
# In .github/workflows/sonarqube.yml
- name: SonarQube Quality Gate
  uses: sonarsource/sonarqube-quality-gate-action@master
  timeout-minutes: 5
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
  # Remove continue-on-error to block on failure
```

### Slack Notifications

Configure in SonarQube:
1. Administration → Configuration → Webhooks
2. Add webhook: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
3. Select events: Quality Gate status changed

## Monitoring

### Health Check

```bash
# API health
curl http://SONARQUBE_URL/api/system/health

# System status
curl http://SONARQUBE_URL/api/system/status
```

### Metrics

```bash
# Project metrics
curl -u admin:admin \
  "http://SONARQUBE_URL/api/measures/component?component=red9inja-gpt&metricKeys=bugs,vulnerabilities,code_smells,coverage"
```

### Logs

```bash
# Application logs
kubectl logs -f deployment/sonarqube -n sonarqube

# Database logs
aws rds describe-db-log-files --db-instance-identifier INSTANCE_ID
```

## Advanced Configuration

### Custom Quality Gate

1. Go to: Quality Gates
2. Create new gate
3. Add conditions:
   - Coverage on New Code > 80%
   - Duplicated Lines on New Code < 3%
   - Maintainability Rating = A
4. Set as default

### Branch Analysis

Enable branch analysis:
1. Administration → General Settings → Branches
2. Enable "Branch analysis"
3. Configure branch patterns

### Security Hotspots

Review security hotspots:
1. Go to: Security Hotspots
2. Review each hotspot
3. Mark as: Safe, To Review, or Fixed

## Documentation Links

- SonarQube Docs: https://docs.sonarqube.org/latest/
- Python Analysis: https://docs.sonarqube.org/latest/analysis/languages/python/
- Quality Gates: https://docs.sonarqube.org/latest/user-guide/quality-gates/
- GitHub Integration: https://docs.sonarqube.org/latest/analysis/github-integration/

## Support

For issues:
1. Check SonarQube logs: `kubectl logs -n sonarqube -l app=sonarqube`
2. Check GitHub Actions logs
3. Review SonarQube documentation
4. Check AWS RDS status
5. Open GitHub issue with details

## Summary

Complete automated code quality system:
- Self-hosted on AWS EKS
- Automated deployment via GitHub Actions
- Automatic code analysis on every push/PR
- Quality gate enforcement
- PR comments with results
- Production-ready with RDS database
- Cost: ~$52/month

**Enterprise-grade code quality monitoring!**


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
