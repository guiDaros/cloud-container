# Architecture Documentation

## System Overview

The cloud-container-portfolio is a cloud-native application demonstrating modern DevOps practices and container orchestration. The system integrates Docker containerization, Kubernetes orchestration, and AWS cloud services.

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes LoadBalancer Service                 │
│                    (Port 80 → 5000)                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Namespace: cloud-portfolio                    │  │
│  │                                                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  Pod 1   │  │  Pod 2   │  │  Pod 3   │           │  │
│  │  │          │  │          │  │          │           │  │
│  │  │ Flask    │  │ Flask    │  │ Flask    │           │  │
│  │  │ App      │  │ App      │  │ App      │           │  │
│  │  │ :5000    │  │ :5000    │  │ :5000    │           │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘           │  │
│  │       │             │             │                   │  │
│  │       └─────────────┴─────────────┘                   │  │
│  │                     │                                  │  │
│  │       ┌─────────────┴─────────────┐                   │  │
│  │       │                           │                   │  │
│  │       ▼                           ▼                   │  │
│  │  ┌─────────┐              ┌─────────────┐            │  │
│  │  │ConfigMap│              │   Secret    │            │  │
│  │  │         │              │             │            │  │
│  │  │AWS_REGION│             │AWS_ACCESS_  │            │  │
│  │  │BUCKET_NAME│            │KEY_ID       │            │  │
│  │  └─────────┘              │AWS_SECRET_  │            │  │
│  │                           │ACCESS_KEY   │            │  │
│  │                           └─────────────┘            │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS (boto3 SDK)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud                               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                IAM Service                          │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ IAM User: cloud-portfolio-app            │     │    │
│  │  │ Policy: CloudPortfolioS3Policy           │     │    │
│  │  │ Permissions: s3:Get*, s3:Put*, s3:List*  │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          │ Authorizes                        │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Amazon S3 Service                         │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ Bucket: cloud-portfolio-storage          │     │    │
│  │  │ Region: us-east-1                        │     │    │
│  │  │ Versioning: Enabled                      │     │    │
│  │  │ Encryption: SSE-S3                       │     │    │
│  │  │                                          │     │    │
│  │  │ Objects:                                 │     │    │
│  │  │  - file1.txt                             │     │    │
│  │  │  - file2.pdf                             │     │    │
│  │  │  - image.png                             │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Component Layers

### 1. Presentation Layer

**LoadBalancer Service**
- Type: LoadBalancer (or NodePort for local clusters)
- External port: 80
- Internal port: 5000
- Protocol: HTTP
- Session affinity: ClientIP

**Purpose:** Exposes the application to external traffic and distributes requests across pod replicas.

### 2. Application Layer

**Container Specification**
- Base image: Python 3.11-slim
- Application: Flask web framework
- Port: 5000
- Runtime: Gunicorn with 2 workers, 4 threads

**Pod Configuration**
- Replicas: 3 (high availability)
- Resource requests: 250m CPU, 256Mi memory
- Resource limits: 500m CPU, 512Mi memory
- Update strategy: RollingUpdate (maxSurge: 1, maxUnavailable: 1)

**Health Checks**
- Liveness probe: /health endpoint (checks if container is running)
- Readiness probe: /ready endpoint (checks if container can serve traffic)
- Initial delay: 10-30 seconds
- Period: 5-10 seconds

### 3. Configuration Layer

**ConfigMap**
- Non-sensitive configuration
- AWS region
- Bucket name
- Application settings
- Environment variables

**Secret**
- Sensitive credentials
- AWS Access Key ID
- AWS Secret Access Key
- Base64 encoded
- Mounted as environment variables

### 4. Storage Layer

**Amazon S3**
- Object storage for files
- Bucket: cloud-portfolio-storage
- Region: us-east-1
- Access: Private (IAM authenticated only)
- Features: Versioning, encryption, lifecycle policies

**IAM Security**
- User: cloud-portfolio-app
- Policy: Least privilege (only necessary S3 operations)
- Authentication: Access keys (stored in Kubernetes Secret)

## Data Flow

### File Upload Flow

1. User submits file via web interface
2. Request hits LoadBalancer (port 80)
3. LoadBalancer routes to healthy pod (port 5000)
4. Flask app receives POST request at /upload
5. App authenticates with AWS using credentials from Secret
6. boto3 SDK uploads file to S3 bucket
7. S3 confirms upload and returns object metadata
8. App returns success response to user
9. User interface displays confirmation

### File List Flow

1. User clicks "Load Files" button
2. JavaScript makes GET request to /files
3. Request routes through LoadBalancer to pod
4. Flask app calls s3_client.list_objects_v2()
5. AWS IAM validates credentials and permissions
6. S3 returns list of objects in bucket
7. App formats response as JSON
8. User interface displays file list

## Security Architecture

### Network Security

**Ingress:**
- LoadBalancer accepts traffic on port 80
- Only specified ports exposed to external traffic
- Service selector ensures traffic only reaches correct pods

**Egress:**
- Pods can reach AWS S3 endpoints (HTTPS port 443)
- DNS resolution for AWS service discovery
- All AWS communication encrypted with TLS

### Authentication & Authorization

**Kubernetes Level:**
- RBAC for kubectl access
- ServiceAccount permissions
- Namespace isolation

**AWS Level:**
- IAM user with programmatic access only
- Policy restricts to specific bucket
- No wildcard permissions
- Actions limited to: ListBucket, GetObject, PutObject, DeleteObject

### Secrets Management

**Current Implementation:**
- Kubernetes Secrets for AWS credentials
- Base64 encoding (not encryption)
- Mounted as environment variables
- Not committed to Git

**Production Recommendations:**
- Use AWS IAM Roles for Service Accounts (IRSA) in EKS
- Implement AWS Secrets Manager integration
- Enable automatic credential rotation
- Use encryption at rest for Secrets (etcd encryption)

## Scalability

### Horizontal Scaling

**Current Configuration:**
- 3 replica pods
- Can scale up/down manually: `kubectl scale deployment`

**Autoscaling (Future):**
- Horizontal Pod Autoscaler (HPA)
- Scale based on CPU/memory metrics
- Min replicas: 2, Max replicas: 10
- Target CPU utilization: 70%

### Vertical Scaling

**Resource Adjustment:**
- Increase pod resource requests/limits
- Requires deployment restart
- Balances cost vs performance

## High Availability

### Application Level

**Multiple Replicas:**
- 3 pods ensure service continuity
- LoadBalancer distributes traffic
- If one pod fails, traffic routes to healthy pods

**Rolling Updates:**
- Zero-downtime deployments
- One pod updated at a time
- Rollback capability if issues detected

### Health Monitoring

**Liveness Probe:**
- Kubernetes restarts unhealthy containers
- Checks /health endpoint every 10 seconds
- 3 failures trigger restart

**Readiness Probe:**
- Removes pod from service if not ready
- Prevents traffic to initializing pods
- Adds back when ready

### AWS S3 Availability

- S3 standard storage: 99.99% availability
- Automatic replication across multiple AZs
- Versioning enables recovery from accidental deletions

## Performance Optimization

### Application Level

**Gunicorn Configuration:**
- 2 worker processes (handles concurrent requests)
- 4 threads per worker (handles I/O operations)
- 60-second timeout for long-running requests

**Caching (Future):**
- Implement Redis for file list caching
- Cache S3 list operations (expensive)
- TTL-based invalidation

### Resource Management

**CPU & Memory:**
- Requests guarantee minimum resources
- Limits prevent resource exhaustion
- Optimized for typical workload

**Connection Pooling:**
- boto3 maintains connection pool to AWS
- Reduces SSL handshake overhead
- Improves throughput

## Monitoring & Observability

### Kubernetes Metrics

**Pod Metrics:**
- CPU usage
- Memory usage
- Network I/O
- Restart count

**Deployment Metrics:**
- Available replicas
- Desired vs current state
- Update progress

### Application Logs

**Log Structure:**
- Stdout/stderr captured by Kubernetes
- View with: `kubectl logs`
- Structured logging with timestamps

**Log Aggregation (Future):**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd for log collection
- Centralized logging dashboard

### AWS CloudWatch

**S3 Metrics:**
- Request count
- Error rates (4xx, 5xx)
- Bytes uploaded/downloaded
- Storage size

## Disaster Recovery

### Backup Strategy

**Application Code:**
- Versioned in Git
- Multiple copies (local, GitHub, clones)

**Configuration:**
- Kubernetes manifests in Git
- Infrastructure as Code approach

**Data (S3):**
- S3 versioning enabled
- Can recover previous versions
- Cross-region replication (future)

### Recovery Procedures

**Pod Failure:**
- Automatic: Kubernetes restarts pod
- RTO: < 1 minute
- RPO: None (stateless application)

**Node Failure:**
- Automatic: Pods rescheduled to healthy nodes
- RTO: 1-3 minutes
- RPO: None

**Cluster Failure:**
- Manual: Deploy to new cluster
- Apply all Kubernetes manifests
- Update DNS to new LoadBalancer
- RTO: 15-30 minutes
- RPO: None (data in S3, separate from cluster)

**S3 Data Loss:**
- Restore from versioned objects
- RTO: Minutes to hours (depends on data size)
- RPO: Time of last version

## Cost Optimization

### Kubernetes Resources

**Right-sizing:**
- Monitor actual CPU/memory usage
- Adjust requests/limits based on metrics
- Avoid over-provisioning

**Autoscaling:**
- Scale down during low traffic
- Scale up during peak hours
- Saves compute costs

### AWS S3 Costs

**Storage Classes:**
- Standard: Frequent access
- Intelligent-Tiering: Automatic optimization
- Glacier: Long-term archive

**Lifecycle Policies:**
- Transition old files to cheaper storage
- Delete temporary files after X days
- Incomplete multipart upload cleanup

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Container Runtime | Docker | Application containerization |
| Orchestration | Kubernetes | Container orchestration |
| Application | Python Flask | Web framework |
| AWS SDK | boto3 | AWS service integration |
| Web Server | Gunicorn | Production WSGI server |
| Cloud Storage | Amazon S3 | Object storage |
| Authentication | AWS IAM | Access control |
| CI/CD | GitHub Actions | Automated deployment |
| Registry | Docker Hub | Container image storage |

## Future Enhancements

1. **Service Mesh**: Implement Istio for advanced traffic management
2. **Monitoring**: Add Prometheus + Grafana
3. **Caching**: Implement Redis for performance
4. **CDN**: CloudFront for static assets
5. **Database**: Add RDS for metadata storage
6. **Message Queue**: SQS for async processing
7. **API Gateway**: AWS API Gateway for advanced routing
8. **Multi-region**: Deploy across multiple AWS regions