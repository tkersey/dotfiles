# Cloud Provider Security — AWS, GCP, Azure, Vercel

Each cloud provider has specific security footguns. This file covers the top
issues per provider for SaaS.

---

## AWS Security

### IAM (Identity and Access Management)

**The #1 AWS risk:** overly permissive IAM roles.

**Principles:**
- Minimum necessary permissions
- Use IAM roles (not users) for services
- Separate roles per environment (dev, staging, prod)
- Rotate access keys (or better: don't use them)

**Common mistakes:**
```json
// BAD: wildcard permissions
{
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
  }]
}

// GOOD: specific actions on specific resources
{
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

### EC2 Metadata Service (IMDS)

**The Capital One pattern:** SSRF → IMDS → IAM credentials → data exfiltration.

**Fix:**
- Use IMDSv2 (session-based, token required)
- Hop limit = 1 (prevents container breakout)
- Block instance metadata in application firewall

```bash
# Enforce IMDSv2
aws ec2 modify-instance-metadata-options \
  --instance-id i-1234 \
  --http-tokens required \
  --http-put-response-hop-limit 1
```

### S3 Buckets

**Checklist:**
- [ ] Block Public Access enabled at account level
- [ ] Bucket policies don't allow `*` principal
- [ ] ACLs don't grant public read
- [ ] Object-level ACLs respect bucket defaults
- [ ] Versioning enabled
- [ ] Server-side encryption enabled (SSE-KMS preferred)
- [ ] Access logs enabled
- [ ] Lifecycle policies for retention
- [ ] Object Lock for backups (WORM)
- [ ] CloudTrail data events logged

### RDS

- [ ] Not publicly accessible (private subnet only)
- [ ] Encryption at rest enabled
- [ ] Automated backups enabled
- [ ] Multi-AZ for production
- [ ] IAM database authentication (where possible)
- [ ] Parameter group disables plaintext `rds_log_level=log_min_duration_statement` for SQL logging

### KMS (Key Management Service)

- [ ] Customer-managed keys for sensitive data
- [ ] Key rotation enabled
- [ ] Key policies limit who can decrypt
- [ ] CloudTrail logs KMS operations
- [ ] Separate keys per environment

### CloudTrail

- [ ] Enabled in all regions
- [ ] Multi-region trail
- [ ] Log file validation enabled
- [ ] Logs go to dedicated bucket with MFA delete
- [ ] SNS notification on bucket changes

---

## GCP Security

### IAM

Similar principles to AWS. Key differences:
- Resource hierarchy: Organization → Folder → Project → Resource
- Permissions inherit down the hierarchy
- Service accounts are the key identity for workloads

**Common mistakes:**
- Using `Owner` role instead of specific roles
- Service account keys in source code
- `allUsers` or `allAuthenticatedUsers` in IAM bindings

### Service Accounts

**Best practice:** workload identity (no long-lived keys).

```yaml
# GKE workload identity
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    iam.gke.io/gcp-service-account: my-app@project.iam.gserviceaccount.com
```

### Cloud Storage Buckets

- [ ] Uniform bucket-level access (no object-level ACLs)
- [ ] No `allUsers` bindings
- [ ] VPC Service Controls for sensitive data
- [ ] Object Versioning enabled
- [ ] Retention policies for compliance

### Cloud SQL

- [ ] Private IP only (no public)
- [ ] Automatic backups
- [ ] Point-in-time recovery
- [ ] SSL required
- [ ] IAM database authentication

### Secret Manager

- [ ] Secrets stored in Secret Manager, not env vars
- [ ] Access via IAM
- [ ] Versioning enabled
- [ ] Rotation configured

---

## Azure Security

### Azure AD

- [ ] Conditional Access policies
- [ ] MFA required for all users
- [ ] Privileged Identity Management (PIM) for admin roles
- [ ] Access reviews quarterly

### Storage Accounts

- [ ] Block public blob access
- [ ] Secure transfer required (HTTPS)
- [ ] TLS 1.2 minimum
- [ ] Private endpoints
- [ ] Firewall rules restrict source IPs
- [ ] Access keys rotated

### Key Vault

- [ ] Soft delete enabled
- [ ] Purge protection enabled
- [ ] Private endpoints
- [ ] Managed identities (not service principals where possible)
- [ ] Audit logging to Log Analytics

### Defender for Cloud

Enable for runtime protection:
- Defender for App Service
- Defender for Storage
- Defender for Key Vault
- Defender for Container Registries

---

## Vercel Security

### Environment Variables
- [ ] Secrets in Vercel env vars, not hard-coded
- [ ] Scoped per environment (development, preview, production)
- [ ] Preview deployments use staging secrets (not production)
- [ ] Rotation schedule

### Deployment Protection
- [ ] Password protection on preview deployments (paid plans)
- [ ] Only main branch auto-deploys to production
- [ ] Ignored PR protection (don't preview-deploy drafts)

### Edge Config / KV
- [ ] Access via Vercel SDK (not raw API)
- [ ] Minimum access scope
- [ ] Rotation schedule

### Custom Domains
- [ ] HTTPS enforced (Vercel default)
- [ ] HSTS header set
- [ ] Automatic cert renewal monitored

### Serverless Function Security
- [ ] `x-real-ip` is trusted (Vercel sets it correctly)
- [ ] Function timeout limits (prevent hung requests)
- [ ] Memory limits (prevent memory bombs)
- [ ] Environment variables scoped to deployments

---

## Cloudflare Security

### WAF (Web Application Firewall)
- [ ] Enabled for production domains
- [ ] OWASP Core Rule Set active
- [ ] Custom rules for known attack patterns
- [ ] Rate limiting rules

### DDoS Protection
- [ ] Bot fight mode enabled
- [ ] Under attack mode tested (but not left on)
- [ ] Captcha for suspicious traffic

### Access
- [ ] Origin IPs restricted to Cloudflare IP ranges
- [ ] Authenticated Origin Pulls enabled (mTLS to origin)
- [ ] Cloudflare Access JWT verified at origin (not just header presence!)

### Workers
- [ ] KV access scoped
- [ ] D1 queries parameterized
- [ ] Durable Objects access control
- [ ] Worker secrets via env bindings

---

## Multi-Cloud Considerations

### Secret synchronization
If you have secrets in multiple clouds, keep them synchronized:
- AWS Secrets Manager + GCP Secret Manager + Vault + Vercel env
- Use a single source of truth (e.g., Vault) and propagate

### Identity federation
Avoid cross-cloud static credentials. Use federation:
- AWS IAM Roles Anywhere
- GCP Workload Identity Federation
- Azure Managed Identity

### Consistent naming
Different clouds use different terms:
- AWS: IAM Role, Resource, Policy
- GCP: Service Account, Resource, IAM Binding
- Azure: Managed Identity, Resource, Role Assignment

Document the mapping.

---

## The Cloud Security Audit Checklist

### Identity
- [ ] No root/owner access keys
- [ ] MFA for all human accounts
- [ ] Workload identity for services
- [ ] No hardcoded credentials
- [ ] Service accounts have minimum permissions

### Storage
- [ ] No publicly accessible buckets (unless explicitly public content)
- [ ] Encryption at rest
- [ ] Versioning / lifecycle enabled
- [ ] Access logs enabled

### Compute
- [ ] IMDSv2 (AWS) / equivalent on other clouds
- [ ] Instances in private subnets
- [ ] Security groups restrict source IPs
- [ ] OS updates automated

### Database
- [ ] Not publicly accessible
- [ ] Encryption at rest
- [ ] Automated backups
- [ ] SSL required

### Network
- [ ] WAF in front of public endpoints
- [ ] DDoS protection
- [ ] Private subnets for backends
- [ ] NAT for egress (not public IPs on backends)

### Monitoring
- [ ] CloudTrail / audit logs enabled
- [ ] Logs centralized
- [ ] Alerts on security events
- [ ] Regular security posture review

### Incident response
- [ ] Runbooks for common incidents
- [ ] Playbooks for credential rotation
- [ ] Forensic queries ready
- [ ] Communication templates

---

## Cloud Security Tools

### Free / Open Source
- **CloudSploit** — AWS misconfiguration scanner
- **ScoutSuite** — multi-cloud auditing
- **Prowler** — AWS compliance scanning
- **kube-bench** — Kubernetes CIS benchmarks
- **tfsec / checkov** — Terraform security scanning

### Commercial
- **AWS Security Hub** — centralized AWS security findings
- **Wiz** — multi-cloud, very good
- **Lacework** — runtime protection
- **Orca** — agentless multi-cloud
- **Palo Alto Prisma Cloud**
- **CrowdStrike Cloud Security**

---

## See Also

- [INFRASTRUCTURE.md](INFRASTRUCTURE.md)
- [THIRD-PARTY.md](THIRD-PARTY.md)
- [KEY-MANAGEMENT.md](KEY-MANAGEMENT.md)
- [vercel skill](../../vercel/) for Vercel specifics
- [gcloud skill](../../gcloud/) for GCP CLI
