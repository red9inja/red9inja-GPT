# Trivy Security Scanning

## Overview
Trivy provides comprehensive security scanning for containers, dependencies, IaC, and secrets.

## Scanning Coverage

### 1. Docker Image Scanning
- **What**: Scans built Docker images for vulnerabilities
- **When**: On every push and PR
- **Detects**: OS packages, application dependencies vulnerabilities
- **Output**: SARIF format uploaded to GitHub Security tab

### 2. Filesystem Scanning
- **What**: Scans entire repository for vulnerabilities
- **When**: Daily at 3 AM + on push/PR
- **Detects**: Python dependencies, config issues
- **Output**: GitHub Security alerts

### 3. IaC Scanning
- **What**: Scans Terraform and Kubernetes manifests
- **When**: On infrastructure changes
- **Detects**: Misconfigurations, security issues
- **Files**: `terraform/`, `k8s/`

### 4. Secret Scanning
- **What**: Detects hardcoded secrets and API keys
- **When**: On every commit
- **Detects**: AWS keys, passwords, tokens, private keys
- **Action**: Fails build if secrets found

### 5. Dependency Scanning
- **What**: Scans requirements.txt for vulnerable packages
- **When**: On every push
- **Detects**: Known CVEs in Python packages
- **Output**: JSON report with fix recommendations

### 6. SBOM Generation
- **What**: Creates Software Bill of Materials
- **Format**: CycloneDX JSON
- **Use**: Compliance, supply chain security
- **Storage**: GitHub artifacts

## Workflows

### red9inja-GPT Repository
```yaml
# .github/workflows/trivy-security.yml
- Docker image scan
- Dependency scan (requirements.txt)
- SBOM generation
```

### red9inja-GPT-INFRA Repository
```yaml
# .github/workflows/trivy-security.yml
- Filesystem scan
- Terraform scan
- Kubernetes manifest scan
- Secret scan
```

## Severity Levels
- **CRITICAL**: Immediate fix required
- **HIGH**: Fix within 7 days
- **MEDIUM**: Fix within 30 days
- **LOW**: Fix when possible

## GitHub Security Integration
Trivy results automatically appear in:
- **Security tab** → Code scanning alerts
- **Pull Requests** → Security annotations
- **Dependabot** → Automated fix PRs

## Local Scanning

### Install Trivy
```bash
# Linux
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# macOS
brew install trivy
```

### Scan Commands
```bash
# Scan Docker image
trivy image red9inja-gpt:latest

# Scan filesystem
trivy fs .

# Scan specific file
trivy fs requirements.txt

# Scan Terraform
trivy config terraform/

# Scan Kubernetes
trivy config k8s/

# Scan for secrets
trivy fs --scanners secret .

# Generate SBOM
trivy image --format cyclonedx red9inja-gpt:latest > sbom.json

# Scan with severity filter
trivy image --severity CRITICAL,HIGH red9inja-gpt:latest

# Output to JSON
trivy image --format json -o results.json red9inja-gpt:latest
```

## CI/CD Integration

### Fail Build on Critical Issues
```yaml
- name: Trivy Scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'image'
    image-ref: 'red9inja-gpt:latest'
    exit-code: '1'  # Fail if vulnerabilities found
    severity: 'CRITICAL,HIGH'
```

### Ignore Specific CVEs
Create `.trivyignore`:
```
# Ignore specific CVE
CVE-2023-12345

# Ignore with expiry
CVE-2023-67890 exp:2026-03-01

# Ignore with reason
CVE-2023-11111 # False positive, not exploitable
```

## Comparison with Other Tools

| Feature | Trivy | OWASP Dependency-Check | Snyk |
|---------|-------|------------------------|------|
| Container Scan |  |  |  |
| IaC Scan |  |  |  |
| Secret Detection |  |  |  |
| SBOM Generation |  |  |  |
| Speed | Fast | Slow | Fast |
| Cost | Free | Free | Paid |
| Offline Mode |  |  |  |

## Best Practices

1. **Scan Early**: Run Trivy in development before pushing
2. **Fix Critical First**: Prioritize CRITICAL and HIGH vulnerabilities
3. **Update Regularly**: Keep base images and dependencies updated
4. **Use .trivyignore**: Document false positives
5. **Monitor Trends**: Track vulnerability count over time
6. **Automate**: Let CI/CD catch issues automatically

## Integration with Existing Security

### Layered Security Approach
```
┌─────────────────────────────────────┐
│ Trivy (Container + IaC + Secrets)   │
├─────────────────────────────────────┤
│ OWASP ZAP (Dynamic Testing)         │
├─────────────────────────────────────┤
│ SonarQube (Code Quality)            │
├─────────────────────────────────────┤
│ AWS WAF (Runtime Protection)        │
└─────────────────────────────────────┘
```

### Coverage Matrix
- **Trivy**: Container vulnerabilities, IaC misconfigurations, secrets
- **OWASP**: Application vulnerabilities, dependency CVEs
- **SonarQube**: Code smells, bugs, security hotspots
- **AWS WAF**: Runtime attack prevention

## Cost Impact
**$0/month** - Completely free and open source

## Compliance
- **PCI DSS**: Requirement 6.2 (vulnerability management)
- **HIPAA**: Security rule (vulnerability scanning)
- **SOC 2**: CC7.1 (security monitoring)
- **ISO 27001**: A.12.6.1 (technical vulnerability management)

## Metrics
Track in Grafana:
- Total vulnerabilities by severity
- Vulnerabilities fixed per sprint
- Mean time to remediation (MTTR)
- Container image security score

## Alerts
Configure GitHub Actions to:
- Fail build on CRITICAL vulnerabilities
- Create GitHub issues for HIGH vulnerabilities
- Send Slack notifications for new CVEs
- Block deployment if secrets detected
