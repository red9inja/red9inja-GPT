# OWASP Security Integration

## Overview
Integrated OWASP security scanning and protection into red9inja-GPT for comprehensive security coverage.

## Components

### 1. OWASP ZAP (Dynamic Application Security Testing)
- **Baseline Scan**: Automated security testing against live endpoints
- **Targets**: All environment URLs (dev, test, staging, prod)
- **Frequency**: On every push and PR
- **Reports**: HTML reports uploaded as artifacts

### 2. OWASP Dependency-Check
- **Purpose**: Identify known vulnerabilities in dependencies
- **Scan**: Python packages in requirements.txt
- **Frequency**: Weekly scheduled scan + on-demand
- **Reports**: HTML vulnerability reports

### 3. OWASP Security Middleware
- **Injection Prevention**: SQL injection and XSS pattern detection
- **Security Headers**: 
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security: max-age=31536000
  - Content-Security-Policy: default-src 'self'
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy: geolocation=(), microphone=(), camera=()

## OWASP Top 10 Coverage

### A01:2021 - Broken Access Control
 Cognito JWT authentication
 Role-based access control (admin, premium, users)
 Rate limiting per user

### A02:2021 - Cryptographic Failures
 AWS Secrets Manager for credentials
 TLS/SSL via Cloudflare
 Encryption at rest (DynamoDB, S3)

### A03:2021 - Injection
 Input validation middleware
 SQL injection pattern detection
 XSS pattern detection
 Parameterized queries (DynamoDB)

### A04:2021 - Insecure Design
 Security by design architecture
 Threat modeling with AWS WAF
 Defense in depth strategy

### A05:2021 - Security Misconfiguration
 Security headers middleware
 Automated security scanning
 Infrastructure as Code with security defaults

### A06:2021 - Vulnerable Components
 OWASP Dependency-Check
 SonarQube vulnerability scanning
 Automated dependency updates

### A07:2021 - Authentication Failures
 AWS Cognito with MFA support
 JWT token validation
 Session management

### A08:2021 - Software and Data Integrity
 Code signing in CI/CD
 Integrity checks for model files
 Immutable infrastructure

### A09:2021 - Security Logging Failures
 CloudWatch logging
 Prometheus metrics
 Audit trails in DynamoDB

### A10:2021 - Server-Side Request Forgery
 Input validation
 URL allowlisting
 Network segmentation (VPC)

## GitHub Actions Workflow

```yaml
# .github/workflows/owasp-security.yml
- Dependency Check: Scans Python dependencies
- ZAP Scan: Tests live endpoints
- Security Summary: Aggregates results
```

## Usage

### Manual Scan
```bash
# Trigger workflow manually
gh workflow run owasp-security.yml
```

### View Reports
1. Go to GitHub Actions
2. Select "OWASP Security Scan" workflow
3. Download artifacts (dependency-check-report, zap-scan-report)

### CI/CD Integration
- Runs automatically on push to dev/test/staging/prod
- Weekly scheduled scans on Sunday 2 AM
- Blocks deployment on critical vulnerabilities (optional)

## Configuration

### ZAP Rules
Edit `.zap/rules.tsv` to customize scanning rules:
- WARN: Log warning but don't fail
- IGNORE: Skip the rule
- FAIL: Fail the build (add custom rules)

### Dependency Check
Modify workflow to adjust:
- `--failOnCVSS`: Fail on CVSS score threshold
- `--enableRetired`: Check retired dependencies
- `--enableExperimental`: Use experimental analyzers

## Security Headers Verification

```bash
# Test security headers
curl -I https://gpt.vmind.online

# Expected headers:
# x-content-type-options: nosniff
# x-frame-options: DENY
# strict-transport-security: max-age=31536000
# content-security-policy: default-src 'self'
```

## Cost Impact
- **OWASP ZAP**: Free (GitHub Actions)
- **Dependency-Check**: Free (GitHub Actions)
- **Middleware**: No additional cost
- **Total**: $0/month

## Best Practices
1. Review security reports weekly
2. Update dependencies regularly
3. Fix high/critical vulnerabilities immediately
4. Customize ZAP rules for your API
5. Enable MFA for all users
6. Monitor security metrics in Grafana

## Integration with Existing Security

### AWS WAF
- OWASP ZAP complements WAF rules
- WAF blocks attacks, ZAP finds vulnerabilities

### SonarQube
- SonarQube: Static analysis
- OWASP: Dynamic + dependency analysis
- Combined coverage for complete security

### Cloudflare
- Cloudflare: DDoS protection
- OWASP: Application-level security
- Layered defense strategy

## Compliance
- **PCI DSS**: Requirement 6.5 (secure coding)
- **HIPAA**: Security rule compliance
- **SOC 2**: Security controls
- **ISO 27001**: Information security management
