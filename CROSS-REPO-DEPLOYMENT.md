# Cross-Repository Deployment Setup

## Overview

When you push code to **red9inja-GPT** repo, it automatically triggers deployment in **red9inja-GPT-INFRA** repo.

## Setup Required

### Step 1: Create GitHub Personal Access Token (PAT)

1. Go to GitHub: Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click: Generate new token (classic)
3. Name: `INFRA_TRIGGER_TOKEN`
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
5. Click: Generate token
6. Copy the token (you won't see it again!)

### Step 2: Add Token to red9inja-GPT Repo

1. Go to: https://github.com/red9inja/red9inja-GPT
2. Settings → Secrets and variables → Actions
3. New repository secret:
   - Name: `INFRA_TRIGGER_TOKEN`
   - Value: Paste the PAT token
   - Add secret

### Step 3: Add AWS Credentials to red9inja-GPT-INFRA Repo

1. Go to: https://github.com/red9inja/red9inja-GPT-INFRA
2. Settings → Secrets and variables → Actions
3. Add two secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

## How It Works

### Workflow 1: red9inja-GPT (Application Code)

```
Push to GPT repo (dev/test/staging/prod branch)
         ↓
trigger-infra.yml runs
         ↓
Sends trigger to INFRA repo
```

### Workflow 2: red9inja-GPT-INFRA (Infrastructure)

```
Receives trigger from GPT repo
         ↓
terraform-cicd.yml runs
         ↓
Creates/updates EKS cluster
         ↓
Builds Docker image from GPT code
         ↓
Deploys to Kubernetes
```

## Deployment Triggers

### Automatic Triggers

**From GPT Repo:**
- Push to dev/test/staging/prod branches
- Changes in: model/, api/, data/, training/, utils/, *.py, requirements.txt

**From INFRA Repo:**
- Push to dev/test/staging/prod branches
- Changes in: terraform/, k8s/, docker/

### Manual Trigger

**From INFRA Repo:**
- Go to Actions tab
- Select "Terraform CI/CD" workflow
- Click "Run workflow"
- Select environment
- Click "Run workflow"

## Complete Flow

```
1. Developer pushes code to red9inja-GPT (dev branch)
2. trigger-infra.yml detects push
3. Sends repository_dispatch to red9inja-GPT-INFRA
4. terraform-cicd.yml in INFRA repo starts
5. Terraform creates/updates infrastructure
6. Docker image built from GPT code
7. Image pushed to ECR
8. Deployed to EKS cluster
9. Service available via Load Balancer
```

## Example Usage

### Deploy to Dev Environment

```bash
cd red9inja-GPT
git checkout dev
# Make changes to model code
git add .
git commit -m "Update model architecture"
git push origin dev
```

This will:
1. Trigger workflow in GPT repo
2. Trigger deployment in INFRA repo
3. Update infrastructure and redeploy

### Deploy to Production

```bash
cd red9inja-GPT
git checkout prod
git merge dev
git push origin prod
```

This will deploy to production environment.

## Monitoring

### Check GPT Repo Workflow
https://github.com/red9inja/red9inja-GPT/actions

### Check INFRA Repo Workflow
https://github.com/red9inja/red9inja-GPT-INFRA/actions

## Troubleshooting

### Workflow not triggering

Check:
- INFRA_TRIGGER_TOKEN is added to GPT repo secrets
- Token has correct permissions (repo, workflow)
- Branch names match (dev/test/staging/prod)

### Deployment fails

Check:
- AWS credentials in INFRA repo
- S3 bucket exists for Terraform state
- ECR repository exists

## Security Notes

- PAT token has full repo access - keep it secure
- Use separate AWS accounts for different environments
- Rotate tokens regularly
- Use AWS IAM roles instead of access keys (recommended)

## Summary

**One-time Setup:**
1. Create PAT token
2. Add to GPT repo as INFRA_TRIGGER_TOKEN
3. Add AWS credentials to INFRA repo

**Daily Usage:**
- Push code to GPT repo
- Automatic deployment happens
- Check Actions tab for status
