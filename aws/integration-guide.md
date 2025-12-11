# AWS Integration Guide

## Overview

This guide demonstrates how the cloud-container-portfolio application integrates with AWS services, specifically S3 for object storage and IAM for secure authentication.

## Architecture

The application uses the following AWS integration pattern:

1. **Application Layer**: Python Flask app with boto3 SDK
2. **Authentication**: IAM user with programmatic access keys
3. **Storage**: S3 bucket for file storage
4. **Security**: Least privilege IAM policies

## Prerequisites

- AWS Account
- AWS CLI installed and configured
- Kubectl configured for your Kubernetes cluster
- Basic understanding of IAM and S3

## Step-by-Step Configuration

### 1. Create S3 Bucket

**Via AWS Console:**
- Navigate to S3 service
- Click "Create bucket"
- Bucket name: `cloud-portfolio-storage-[unique-id]` (must be globally unique)
- Region: `us-east-1` (or your preferred region)
- Block all public access: **Enabled**
- Versioning: **Enabled** (optional, recommended)
- Encryption: **Enable** with SSE-S3
- Tags: Add `Project=cloud-container-portfolio`

**Conceptual AWS CLI command:**
```
aws s3api create-bucket --bucket cloud-portfolio-storage-[unique-id] --region us-east-1
aws s3api put-bucket-versioning --bucket cloud-portfolio-storage-[unique-id] --versioning-configuration Status=Enabled
```

### 2. Create IAM Policy

**Via AWS Console:**
- Navigate to IAM → Policies
- Click "Create policy"
- Use JSON editor
- Paste content from `s3-policy.json` (update bucket name)
- Name: `CloudPortfolioS3Policy`
- Description: "Allows access to cloud-portfolio S3 bucket"
- Create policy

**Key Points:**
- Policy grants minimum necessary permissions
- Only allows access to specific bucket
- Separate permissions for bucket listing vs object operations

### 3. Create IAM User

**Via AWS Console:**
- Navigate to IAM → Users
- Click "Add user"
- Username: `cloud-portfolio-app`
- Access type: **Programmatic access** (not Console access)
- Attach policy: `CloudPortfolioS3Policy`
- Add tags: `Project=cloud-container-portfolio`
- Create user

**Important:** Save the Access Key ID and Secret Access Key securely. You won't see them again!

### 4. Configure Kubernetes Secret

**Create Secret manifest:**

The AWS credentials must be stored in a Kubernetes Secret. Create a file `aws-secret.yaml` (DO NOT commit this):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-credentials
  namespace: cloud-portfolio
type: Opaque
stringData:
  access-key-id: "YOUR_AWS_ACCESS_KEY_ID"
  secret-access-key: "YOUR_AWS_SECRET_ACCESS_KEY"
```

**Apply the secret:**
```
kubectl apply -f aws-secret.yaml
```

**Security Note:** Never commit this file to Git! Add it to `.gitignore`.

### 5. Update ConfigMap

Ensure the ConfigMap has the correct bucket name and region:
```yaml
data:
  AWS_BUCKET_NAME: "cloud-portfolio-storage-[your-unique-id]"
  AWS_REGION: "us-east-1"
```

Apply changes:
```
kubectl apply -f kubernetes/configmap.yaml
```

### 6. Deploy Application

Deploy the application which will automatically use the credentials:
```
kubectl apply -f kubernetes/deployment.yaml
```

### 7. Verify Integration

**Check pod logs:**
```
kubectl logs -n cloud-portfolio -l app=cloud-portfolio
```

Look for: `S3 client initialized for bucket: cloud-portfolio-storage-[id]`

**Test endpoints:**
```
kubectl port-forward -n cloud-portfolio svc/cloud-portfolio-service 8080:80
curl http://localhost:8080/info
curl http://localhost:8080/files
```

**Check S3 in AWS Console:**
- Navigate to your bucket
- Upload a test file via the application
- Verify it appears in the bucket

## Security Best Practices

### 1. Credential Management
- ✅ Store credentials in Kubernetes Secrets
- ✅ Use IAM roles instead of access keys when possible (EKS IRSA)
- ✅ Rotate credentials every 90 days
- ❌ Never commit credentials to Git
- ❌ Never hardcode credentials in application code

### 2. IAM Policies
- ✅ Apply principle of least privilege
- ✅ Use resource-specific ARNs
- ✅ Regularly audit and review permissions
- ✅ Use conditions to restrict access (IP, time, MFA)

### 3. S3 Bucket Security
- ✅ Block public access unless explicitly needed
- ✅ Enable versioning for data recovery
- ✅ Enable server-side encryption
- ✅ Configure lifecycle policies for cost optimization
- ✅ Enable CloudTrail logging for audit

### 4. Network Security
- ✅ Use VPC endpoints for S3 (avoid internet gateway)
- ✅ Implement security groups and NACLs
- ✅ Use TLS/SSL for all data in transit

## Troubleshooting

### Error: "NoSuchBucket"
- Verify bucket name in ConfigMap matches actual bucket
- Check region configuration
- Ensure bucket exists in the specified region

### Error: "AccessDenied"
- Verify IAM policy is attached to user
- Check policy allows required actions
- Verify credentials in Secret are correct
- Check bucket policy doesn't block access

### Error: "InvalidAccessKeyId"
- Credentials in Secret are incorrect
- User may have been deleted
- Access key may have been deactivated

### Connection Timeouts
- Check VPC configuration and routing
- Verify security groups allow outbound HTTPS
- Consider using VPC endpoint for S3

## Monitoring

### CloudWatch Metrics
Monitor S3 usage:
- `NumberOfObjects`
- `BucketSizeBytes`
- `AllRequests`
- `4xxErrors` / `5xxErrors`

### Application Logs
Monitor application logs for:
- S3 operation success/failure
- Authentication errors
- Performance metrics

### Cost Monitoring
- Enable Cost Explorer
- Set up billing alerts
- Use S3 Intelligent-Tiering for cost optimization

## Alternative Approaches

### Using IAM Roles for Service Accounts (IRSA) - EKS
For EKS clusters, use IRSA instead of access keys:

1. Create IAM OIDC provider
2. Create IAM role with trust policy for service account
3. Annotate Kubernetes service account
4. Remove access key secrets

This is more secure as credentials are temporary and automatically rotated.

### Using AWS Secrets Manager
Store credentials in AWS Secrets Manager and retrieve them at runtime:

1. Store secrets in Secrets Manager
2. Use AWS SDK to retrieve at startup
3. Implement automatic rotation

## Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [EKS IRSA Guide](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

## Demo Mode

This application includes demo mode that works without real AWS credentials:
- Displays mock data when credentials unavailable
- Shows integration structure without requiring AWS account
- Useful for portfolio demonstration