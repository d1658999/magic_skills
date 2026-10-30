# Cloud & Infrastructure-as-Code (IaC) Security Reference

This reference covers security audits for cloud infrastructure, containerization, Kubernetes configurations, and CI/CD pipelines.

---

## 1. Terraform & Cloud Security Patterns

### 1.1 Overly Permissive IAM Policies (CWE-732)
- **Anti-Pattern**: Granting wildcard actions (`"Action": "*"`) or wildcard resources (`"Resource": "*"`) to services or user roles.
- **Vulnerable Snippet**:
  ```hcl
  # BAD: Admin privileges granted to application role
  data "aws_iam_policy_document" "app_policy" {
    statement {
      actions   = ["*"]
      resources = ["*"]
    }
  }
  ```
- **Hardened Drop-In Remediation**:
  ```hcl
  # GOOD: Principle of least privilege with explicit action and resource constraints
  data "aws_iam_policy_document" "app_policy" {
    statement {
      sid     = "AllowS3InvoiceReadWrite"
      actions = [
        "s3:GetObject",
        "s3:PutObject"
      ]
      resources = [
        "${aws_s3_bucket.invoices.arn}/tenant-${var.tenant_id}/*"
      ]
    }
  }
  ```

### 1.2 Open Security Groups (CWE-284)
- **Anti-Pattern**: Exposing internal database, cache, or management ports to the open internet (`0.0.0.0/0`).
- **Dangerous Ports**: 22 (SSH), 3389 (RDP), 5432 (Postgres), 3306 (MySQL), 6379 (Redis), 27017 (MongoDB).
- **Remediation**:
  ```hcl
  # GOOD: Ingress restricted strictly to application VPC CIDR
  resource "aws_security_group_rule" "db_ingress" {
    type              = "ingress"
    from_port         = 5432
    to_port           = 5432
    protocol          = "tcp"
    security_group_id = aws_security_group.db.id
    source_security_group_id = aws_security_group.app_service.id # SG-to-SG reference
  }
  ```

### 1.3 Unencrypted S3 Buckets & Public Access
- **Requirement**: All cloud buckets must enforce server-side encryption and block public access.
  ```hcl
  resource "aws_s3_bucket_server_side_encryption_configuration" "secure" {
    bucket = aws_s3_bucket.data.id
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.app_key.arn
      }
    }
  }

  resource "aws_s3_bucket_public_access_block" "block_public" {
    bucket                  = aws_s3_bucket.data.id
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
  ```

---

## 2. Dockerfile & Container Security

### Container Audit Checklist:
1. **Never Run as Root**: Always create and switch to an unprivileged user (`USER appuser`).
2. **Multi-Stage Builds**: Separate compiler tools (gcc, npm, cargo) from the final minimal runtime image.
3. **Pin Image Digests**: Avoid `:latest` tags; pin base images by tag and SHA-256 digest.
4. **No Secrets in Image**: Never bake secrets into `ENV`, `ARG`, or image layers.

### Hardened Dockerfile Template (Node.js):
```dockerfile
# Stage 1: Build & Dependencies
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build && npm prune --production

# Stage 2: Hardened Runtime
FROM node:20-alpine AS runner
WORKDIR /app

# Create unprivileged system user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy only production artifacts
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

# Switch to non-root user
USER appuser

# Expose internal unprivileged port
EXPOSE 3000
ENV NODE_ENV=production

CMD ["node", "dist/main.js"]
```

---

## 3. Kubernetes Pod Security Standards

Every pod and deployment manifest should define strict `securityContext` boundaries:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hardened-service
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: app
          image: registry.example.com/app:v1.2.3@sha256:abc...
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          resources:
            limits:
              cpu: "1"
              memory: "512Mi"
            requests:
              cpu: "100m"
              memory: "128Mi"
```

---

## 4. CI/CD & GitHub Actions Security

- **Vulnerability (`pull_request_target`)**: Using `pull_request_target` with an explicit checkout of the PR head commit (`ref: ${{ github.event.pull_request.head.sha }}`) allows fork submitters to execute arbitrary code with repository secrets access.
- **Rule**: Use `pull_request` for untrusted fork builds. If `pull_request_target` is necessary, never checkout untrusted code.
- **Pin Action SHAs**: Always pin GitHub Actions to full 40-character commit hashes:
  ```yaml
  # GOOD: Pinned by commit SHA
  uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
  ```
- **Least Privilege Permissions**:
  ```yaml
  # Restrict default GITHUB_TOKEN permissions
  permissions:
    contents: read
    pull-requests: write
  ```
