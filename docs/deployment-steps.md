# Deployment Steps

## Complete Deployment Guide

This guide walks through deploying the cloud-container-portfolio application from scratch.

## Prerequisites

### Required Tools

- **Docker**: Version 20.10 or higher
- **kubectl**: Version 1.24 or higher
- **Git**: Version 2.30 or higher
- **AWS CLI**: Version 2.x (optional, for AWS setup)

### Required Accounts

- Docker Hub account (free tier is sufficient)
- GitHub account
- AWS account (free tier can be used)
- Kubernetes cluster (options below)

### Kubernetes Cluster Options

**Local Development:**
- Minikube
- Kind (Kubernetes in Docker)
- Docker Desktop (built-in Kubernetes)
- k3s

**Cloud Providers:**
- Amazon EKS
- Google GKE
- Azure AKS
- DigitalOcean Kubernetes

## Phase 1: Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/cloud-container-portfolio.git
cd cloud-container-portfolio
```

### Step 2: Create Environment File

Create `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials:
```
AWS_ACCESS_KEY_ID=your-actual-access-key
AWS_SECRET_ACCESS_KEY=your-actual-secret-key
AWS_BUCKET_NAME=cloud-portfolio-storage
AWS_REGION=us-east-1
```

**Important**: Never commit `.env` file!

### Step 3: Test Application Locally

**Without Docker:**
```bash
cd app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Access: http://localhost:5000

**With Docker:**
```bash
docker build -t cloud-portfolio-test ./app
docker run -p 5000:5000 --env-file .env cloud-portfolio-test
```

Access: http://localhost:5000

### Step 4: Verify Endpoints

Test all endpoints:
```bash
# Health check
curl http://localhost:5000/health

# Readiness check
curl http://localhost:5000/ready

# Application info
curl http://localhost:5000/info

# List files (requires AWS credentials)
curl http://localhost:5000/files
```

## Phase 2: Docker Image Build and Push

### Step 5: Build Production Image
```bash
cd app
docker build -t yourusername/cloud-container-portfolio:v1.0.0 .
docker tag yourusername/cloud-container-portfolio:v1.0.0 yourusername/cloud-container-portfolio:latest
```

**Tips:**
- Use semantic versioning (v1.0.0, v1.1.0, etc.)
- Always tag with version AND latest
- Build from app directory (where Dockerfile is)

### Step 6: Test Built Image
```bash
docker run -d -p 5000:5000 --name test-container \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e AWS_BUCKET_NAME=your-bucket \
  -e AWS_REGION=us-east-1 \
  yourusername/cloud-container-portfolio:latest

# Check logs
docker logs test-container

# Test endpoint
curl http://localhost:5000/health

# Stop and remove
docker stop test-container
docker rm test-container
```

### Step 7: Login to Docker Hub
```bash
docker login
# Enter your Docker Hub username and password/token
```

**Security Tip**: Use access tokens instead of passwords:
- Go to Docker Hub → Account Settings → Security → Access Tokens
- Generate new token
- Use token as password when logging in

### Step 8: Push Image to Docker Hub
```bash
docker push yourusername/cloud-container-portfolio:v1.0.0
docker push yourusername/cloud-container-portfolio:latest
```

**Verify**: Visit https://hub.docker.com/r/yourusername/cloud-container-portfolio

## Phase 3: AWS Configuration

### Step 9: Create S3 Bucket

**Via AWS Console:**
1. Navigate to S3
2. Click "Create bucket"
3. Name: `cloud-portfolio-storage-[unique-id]`
4. Region: `us-east-1`
5. Block all public access: ✅ Enabled
6. Versioning: ✅ Enabled
7. Encryption: ✅ SSE-S3
8. Click "Create bucket"

**Via AWS CLI:**
```bash
aws s3api create-bucket \
  --bucket cloud-portfolio-storage-unique123 \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket cloud-portfolio-storage-unique123 \
  --versioning-configuration Status=Enabled
```

### Step 10: Create IAM Policy

**Via AWS Console:**
1. Navigate to IAM → Policies
2. Click "Create policy"
3. Click JSON tab
4. Paste content from `aws/s3-policy.json`
5. Update bucket name to match yours
6. Name: `CloudPortfolioS3Policy`
7. Click "Create policy"

### Step 11: Create IAM User

**Via AWS Console:**
1. Navigate to IAM → Users
2. Click "Add users"
3. Username: `cloud-portfolio-app`
4. Access type: ✅ Access key - Programmatic access
5. Click "Next: Permissions"
6. Attach policies: `CloudPortfolioS3Policy`
7. Click through to "Create user"
8. **Download CSV** or copy Access Key ID and Secret Access Key
9. Store securely!

## Phase 4: Kubernetes Deployment

### Step 12: Verify Kubernetes Cluster
```bash
# Check connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Verify you have admin access
kubectl auth can-i create deployments
```

### Step 13: Create Namespace
```bash
kubectl apply -f kubernetes/namespace.yaml

# Verify
kubectl get namespaces
```

### Step 14: Create ConfigMap
```bash
# Edit kubernetes/configmap.yaml to update bucket name if needed
kubectl apply -f kubernetes/configmap.yaml

# Verify
kubectl get configmap -n cloud-portfolio
kubectl describe configmap cloud-portfolio-config -n cloud-portfolio
```

### Step 15: Create Secret for AWS Credentials

**Create secret manifest** (temporary file):

Create file `aws-secret.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-credentials
  namespace: cloud-portfolio
type: Opaque
stringData:
  access-key-id: "YOUR_ACTUAL_ACCESS_KEY_ID"
  secret-access-key: "YOUR_ACTUAL_SECRET_ACCESS_KEY"
```

**Apply secret:**
```bash
kubectl apply -f aws-secret.yaml

# Verify (values will be base64 encoded)
kubectl get secret aws-credentials -n cloud-portfolio
kubectl describe secret aws-credentials -n cloud-portfolio
```

**Security: Delete the file immediately after applying!**
```bash
rm aws-secret.yaml
```

**Alternative: Create secret via command line (more secure):**
```bash
kubectl create secret generic aws-credentials \
  --from-literal=access-key-id='YOUR_ACCESS_KEY_ID' \
  --from-literal=secret-access-key='YOUR_SECRET_ACCESS_KEY' \
  --namespace=cloud-portfolio
```

### Step 16: Deploy Application
```bash
# Apply deployment
kubectl apply -f kubernetes/deployment.yaml

# Watch deployment progress
kubectl rollout status deployment/cloud-portfolio-app -n cloud-portfolio

# Verify pods are running
kubectl get pods -n cloud-portfolio

# Check pod details
kubectl describe pod -l app=cloud-portfolio -n cloud-portfolio
```

**Expected output:**
```
NAME                                    READY   STATUS    RESTARTS   AGE
cloud-portfolio-app-xxxxxxxxxx-xxxxx    1/1     Running   0          30s
cloud-portfolio-app-xxxxxxxxxx-xxxxx    1/1     Running   0          30s
cloud-portfolio-app-xxxxxxxxxx-xxxxx    1/1     Running   0          30s
```

### Step 17: Deploy Service
```bash
# Apply service
kubectl apply -f kubernetes/service.yaml

# Verify service
kubectl get service -n cloud-portfolio

# Get service details
kubectl describe service cloud-portfolio-service -n cloud-portfolio
```

**For LoadBalancer type:**
Wait for external IP to be assigned (can take 2-5 minutes):
```bash
kubectl get service cloud-portfolio-service -n cloud-portfolio --watch
```

**For NodePort type (local clusters):**
```bash
# Get NodePort
kubectl get service cloud-portfolio-service -n cloud-portfolio

# Access via node IP and NodePort
# Example: http://192.168.49.2:30080
```

### Step 18: Verify Deployment

**Check pod logs:**
```bash
kubectl logs -f -l app=cloud-portfolio -n cloud-portfolio
```

Look for:
- `S3 client initialized for bucket: cloud-portfolio-storage-xxx`
- No error messages

**Test health endpoints:**
```bash
# Port-forward to test locally
kubectl port-forward -n cloud-portfolio svc/cloud-portfolio-service 8080:80

# In another terminal
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl http://localhost:8080/info
curl http://localhost:8080/files
```

**Access via browser:**
- If LoadBalancer: Use external IP
- If NodePort: Use node IP + NodePort
- If port-forward: http://localhost:8080

## Phase 5: Validation and Testing

### Step 19: Test S3 Integration

**Via Web Interface:**
1. Access application URL
2. Click "Load Files from S3"
3. Should show list of files or empty list

**Via API:**
```bash
curl http://your-app-url/files
```

**Upload test file** (if you added upload functionality):
```bash
curl -X POST -F "file=@testfile.txt" http://your-app-url/upload
```

**Verify in AWS Console:**
- Navigate to S3 → your bucket
- File should appear in the bucket

### Step 20: Test Scalability

**Scale deployment:**
```bash
# Scale up
kubectl scale deployment cloud-portfolio-app --replicas=5 -n cloud-portfolio

# Watch scaling
kubectl get pods -n cloud-portfolio --watch

# Scale down
kubectl scale deployment cloud-portfolio-app --replicas=3 -n cloud-portfolio
```

### Step 21: Test Rolling Update

**Update image:**
```bash
kubectl set image deployment/cloud-portfolio-app \
  cloud-portfolio=yourusername/cloud-container-portfolio:v1.1.0 \
  -n cloud-portfolio

# Watch rollout
kubectl rollout status deployment/cloud-portfolio-app -n cloud-portfolio

# Check rollout history
kubectl rollout history deployment/cloud-portfolio-app -n cloud-portfolio
```

**Rollback if needed:**
```bash
kubectl rollout undo deployment/cloud-portfolio-app -n cloud-portfolio
```

### Step 22: Test Pod Resilience

**Delete a pod (should auto-recreate):**
```bash
# Get pod name
kubectl get pods -n cloud-portfolio

# Delete one pod
kubectl delete pod cloud-portfolio-app-xxxxxxxxxx-xxxxx -n cloud-portfolio

# Watch new pod being created
kubectl get pods -n cloud-portfolio --watch
```

## Phase 6: Monitoring and Maintenance

### Step 23: Check Resource Usage
```bash
# Pod resource usage
kubectl top pods -n cloud-portfolio

# Node resource usage
kubectl top nodes
```

### Step 24: View Logs
```bash
# All pods
kubectl logs -l app=cloud-portfolio -n cloud-portfolio

# Specific pod
kubectl logs cloud-portfolio-app-xxxxxxxxxx-xxxxx -n cloud-portfolio

# Follow logs (real-time)
kubectl logs -f -l app=cloud-portfolio -n cloud-portfolio

# Previous pod logs (if crashed)
kubectl logs --previous cloud-portfolio-app-xxxxxxxxxx-xxxxx -n cloud-portfolio
```

### Step 25: Inspect Configuration
```bash
# View ConfigMap
kubectl get configmap cloud-portfolio-config -n cloud-portfolio -o yaml

# View Secret (base64 encoded)
kubectl get secret aws-credentials -n cloud-portfolio -o yaml

# Decode secret value
kubectl get secret aws-credentials -n cloud-portfolio -o jsonpath='{.data.access-key-id}' | base64 --decode
```

## Troubleshooting Guide

### Issue: Pods not starting

**Check pod status:**
```bash
kubectl get pods -n cloud-portfolio
kubectl describe pod <pod-name> -n cloud-portfolio
```

**Common causes:**
- Image pull errors: Check image name and Docker Hub permissions
- Resource constraints: Check node resources
- ConfigMap/Secret missing: Verify they exist

### Issue: ImagePullBackOff

**Solutions:**
- Verify image exists on Docker Hub
- Check image name in deployment.yaml
- Ensure image is public or provide imagePullSecrets

### Issue: CrashLoopBackOff

**Check logs:**
```bash
kubectl logs <pod-name> -n cloud-portfolio
kubectl logs --previous <pod-name> -n cloud-portfolio
```

**Common causes:**
- Application error on startup
- Missing environment variables
- Port binding issues

### Issue: Service not accessible

**Verify service:**
```bash
kubectl get svc -n cloud-portfolio
kubectl describe svc cloud-portfolio-service -n cloud-portfolio
```

**Check endpoints:**
```bash
kubectl get endpoints cloud-portfolio-service -n cloud-portfolio
```

**Common causes:**
- No pods in Ready state
- Selector mismatch
- LoadBalancer provisioning failed

### Issue: Cannot connect to S3

**Check logs for errors:**
```bash
kubectl logs -l app=cloud-portfolio -n cloud-portfolio | grep -i error
```

**Verify:**
- AWS credentials in Secret are correct
- Bucket name in ConfigMap matches actual bucket
- IAM policy allows required actions
- Network connectivity to AWS

## Cleanup

### Remove Application
```bash
kubectl delete -f kubernetes/service.yaml
kubectl delete -f kubernetes/deployment.yaml
kubectl delete -f kubernetes/configmap.yaml
kubectl delete secret aws-credentials -n cloud-portfolio
kubectl delete -f kubernetes/namespace.yaml
```

### Remove AWS Resources

**S3 Bucket:**
```bash
# Empty bucket first
aws s3 rm s3://your-bucket-name --recursive

# Delete bucket
aws s3api delete-bucket --bucket your-bucket-name --region us-east-1
```

**IAM User:**
1. Delete access keys
2. Detach policies
3. Delete user

## Best Practices Summary

✅ **Always use Secrets for sensitive data**
✅ **Use specific image tags, not just latest**
✅ **Set resource requests and limits**
✅ **Implement health checks**
✅ **Use namespaces for isolation**
✅ **Monitor logs regularly**
✅ **Test rollback procedures**
✅ **Document your deployment process**
✅ **Version your configurations**
✅ **Implement proper RBAC**

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions)
2. Implement monitoring (Prometheus/Grafana)
3. Add horizontal pod autoscaling
4. Configure ingress controller
5. Implement backup strategy
6. Set up alerting