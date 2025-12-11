# ☁️ Cloud Container Portfolio

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/yourusername/cloud-container-portfolio/ci-cd.yaml?branch=main)
![Docker Pulls](https://img.shields.io/docker/pulls/yourusername/cloud-container-portfolio)
![Docker Image Size](https://img.shields.io/docker/image-size/yourusername/cloud-container-portfolio)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)
![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)
![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20IAM-orange.svg)

A production-ready cloud-native application demonstrating practical expertise in containerization, orchestration, and cloud integration. This portfolio project showcases real-world DevOps practices with Docker, Kubernetes, and AWS services.

## 🎯 About This Project

This is a **portfolio demonstration project** built to showcase hands-on expertise in modern cloud technologies. The application is a fully functional file management system that integrates with Amazon S3 for cloud storage, deployed on Kubernetes with automated CI/CD pipelines.

**What This Project Demonstrates:**
- Complete containerization workflow with Docker
- Production-ready Kubernetes deployments with resource management
- Secure AWS cloud integration (S3 and IAM)
- Automated CI/CD pipelines with GitHub Actions
- Infrastructure as Code practices
- Security best practices for credentials and secrets
- Multi-architecture support (amd64/arm64)

The application provides a web interface for interacting with AWS S3, allowing users to list and manage files stored in the cloud while demonstrating the integration between containerized applications and cloud services.

## 🚀 Technologies Used

| Technology | Purpose | Implementation Details |
|------------|---------|------------------------|
| **Docker** | Containerization | Multi-stage builds, optimized images (~150MB), health checks |
| **Kubernetes** | Orchestration | Deployments, Services, ConfigMaps, Secrets, resource limits |
| **Amazon S3** | Object Storage | File upload/download, bucket management via boto3 SDK |
| **AWS IAM** | Access Control | Least-privilege policies, secure credential management |
| **Python 3.11** | Application | Flask web framework, async operations, type hints |
| **GitHub Actions** | CI/CD | Automated testing, building, and deployment pipeline |
| **Docker Hub** | Image Registry | Public image repository with automated builds |
| **Gunicorn** | WSGI Server | Production-grade server with worker management |

## 📐 Architecture

The application follows a three-tier architecture with clear separation of concerns:
```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Kubernetes LoadBalancer        │
│  (Port 80 → 5000)              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Kubernetes Cluster              │
│  ┌─────────────────────────┐   │
│  │ 3 Replica Pods          │   │
│  │ - Resource Limits       │   │
│  │ - Health Checks         │   │
│  │ - Auto-restart          │   │
│  └─────────────────────────┘   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  AWS Cloud                       │
│  ┌─────────────────────────┐   │
│  │ S3 Bucket               │   │
│  │ - Versioning enabled    │   │
│  │ - Encrypted storage     │   │
│  │ - IAM access control    │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

**Request Flow:**
1. User accesses web interface through LoadBalancer
2. Request is routed to a healthy pod (round-robin)
3. Flask application authenticates with AWS using IAM credentials
4. boto3 SDK communicates with S3 over HTTPS
5. Response is returned through the same path

## ✨ Features Implemented

### Container & Orchestration
- ✅ **Multi-stage Docker build** for optimized image size
- ✅ **Multi-architecture support** (linux/amd64, linux/arm64)
- ✅ **Kubernetes Deployment** with 3 replicas for high availability
- ✅ **Resource management** with requests (250m CPU, 256Mi memory) and limits (500m CPU, 512Mi memory)
- ✅ **Rolling updates** with zero downtime (maxSurge: 1, maxUnavailable: 1)
- ✅ **Health checks** with liveness and readiness probes
- ✅ **ConfigMaps** for non-sensitive configuration
- ✅ **Secrets** for secure credential management
- ✅ **Namespace isolation** for resource organization

### Cloud Integration
- ✅ **AWS S3 integration** using boto3 SDK
- ✅ **IAM policies** with least-privilege access
- ✅ **Secure credential management** via Kubernetes Secrets
- ✅ **Environment-based configuration** supporting multiple deployment scenarios

### Advanced Features
- ✅ **GPU deployment example** demonstrating ML workload configuration
- ✅ **Automated CI/CD pipeline** with GitHub Actions
- ✅ **Security scanning** with Trivy vulnerability detection
- ✅ **Automated Docker Hub publishing** with semantic versioning

## 🐳 Docker Image

**Public Repository**: [`yourusername/cloud-container-portfolio`](https://hub.docker.com/r/yourusername/cloud-container-portfolio)

The Docker image is publicly available on Docker Hub and automatically built via GitHub Actions on every push to the main branch.

**Pull the image:**
```bash
docker pull yourusername/cloud-container-portfolio:latest
```

**Image Details:**
- **Size**: ~150MB (optimized with multi-stage builds)
- **Architectures**: linux/amd64, linux/arm64
- **Base**: python:3.11-slim
- **Updated**: Automatically on every commit to main
- **Tags**: `latest`, `v1.0.0`, `stable`, SHA-based tags

**Run locally:**
```bash
docker run -d -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e AWS_BUCKET_NAME=your-bucket \
  -e AWS_REGION=us-east-1 \
  --name cloud-portfolio \
  yourusername/cloud-container-portfolio:latest
```

Access at: http://localhost:5000

## ☸️ Kubernetes Deployment

The project includes complete Kubernetes manifests demonstrating production-ready configurations.

### Key Components

**Deployment Configuration:**
- **Replicas**: 3 pods for high availability and load distribution
- **Strategy**: RollingUpdate for zero-downtime deployments
- **Resource Requests**: 250m CPU, 256Mi memory (guaranteed resources)
- **Resource Limits**: 500m CPU, 512Mi memory (maximum allowed)
- **Liveness Probe**: Checks `/health` endpoint every 10 seconds
- **Readiness Probe**: Checks `/ready` endpoint every 5 seconds
- **Image Pull Policy**: Always (ensures latest image)

**Service Configuration:**
- **Type**: LoadBalancer (exposes externally)
- **External Port**: 80 (HTTP)
- **Target Port**: 5000 (container port)
- **Session Affinity**: ClientIP (sticky sessions)

**ConfigMap:**
- AWS region configuration
- Bucket name
- Application settings
- Non-sensitive parameters

**Secret:**
- AWS Access Key ID
- AWS Secret Access Key
- Encrypted at rest in etcd

### GPU Deployment Example

The project includes `kubernetes/gpu-deployment.yaml` demonstrating how to configure pods with GPU access for machine learning workloads.

**GPU Configuration Highlights:**
- **Resource Request**: `nvidia.com/gpu: 1` (requests 1 GPU)
- **Resource Limit**: `nvidia.com/gpu: 1` (limits to 1 GPU)
- **Tolerations**: Allows scheduling on GPU-tainted nodes
- **Node Selector**: `accelerator: nvidia-gpu` (ensures GPU node)
- **Environment Variables**: `NVIDIA_VISIBLE_DEVICES`, `CUDA_VISIBLE_DEVICES`

**Prerequisites for GPU deployment:**
- Kubernetes cluster with GPU nodes
- NVIDIA device plugin installed
- Nodes labeled with `accelerator: nvidia-gpu`

This demonstrates understanding of specialized workload requirements and resource scheduling in Kubernetes.

## ☁️ AWS Integration

This project demonstrates secure integration with AWS services without exposing credentials in the codebase.

### Architecture

The application connects to AWS S3 for object storage using the boto3 SDK. Authentication is handled through IAM credentials stored securely in Kubernetes Secrets.

**IAM Configuration:**
- **User**: Dedicated IAM user (`cloud-portfolio-app`) with programmatic access only
- **Policy**: Custom policy with minimum required permissions
- **Permissions**: `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`
- **Scope**: Limited to specific S3 bucket only (principle of least privilege)

**S3 Bucket Configuration:**
- **Access**: Private (no public access)
- **Versioning**: Enabled for data recovery
- **Encryption**: Server-side encryption (SSE-S3)
- **Region**: us-east-1 (configurable)

### Security Best Practices

✅ **Never commit credentials** - All sensitive data in Secrets or environment variables  
✅ **Least privilege principle** - IAM policy grants only necessary permissions  
✅ **Kubernetes Secrets** - Credentials stored encrypted in etcd  
✅ **No hardcoded values** - All configuration via environment variables  
✅ **Audit trail** - CloudTrail enabled for S3 access logging  

### Configuration Guide

Complete setup instructions are available in [`aws/integration-guide.md`](aws/integration-guide.md), including:
- S3 bucket creation steps
- IAM policy and user setup
- Kubernetes Secret configuration
- Security recommendations
- Troubleshooting guide

**Note**: The application includes a "demo mode" that works without real AWS credentials, allowing the portfolio to be reviewed without requiring AWS account setup.

## 🚀 Quick Start

### Prerequisites

- Docker installed
- kubectl configured (for Kubernetes deployment)
- AWS account (optional - works in demo mode)

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/cloud-container-portfolio.git
cd cloud-container-portfolio
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your AWS credentials (or leave as mock for demo)
```

3. **Run with Docker:**
```bash
docker build -t cloud-portfolio ./app
docker run -p 5000:5000 --env-file .env cloud-portfolio
```

4. **Access application:**
```
http://localhost:5000
```

### Kubernetes Deployment

1. **Apply namespace:**
```bash
kubectl apply -f kubernetes/namespace.yaml
```

2. **Create ConfigMap:**
```bash
kubectl apply -f kubernetes/configmap.yaml
```

3. **Create Secret (replace with your credentials):**
```bash
kubectl create secret generic aws-credentials \
  --from-literal=access-key-id='YOUR_ACCESS_KEY_ID' \
  --from-literal=secret-access-key='YOUR_SECRET_ACCESS_KEY' \
  --namespace=cloud-portfolio
```

4. **Deploy application:**
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

5. **Get service URL:**
```bash
kubectl get service cloud-portfolio-service -n cloud-portfolio
```

Wait for EXTERNAL-IP to be assigned (for LoadBalancer) or use NodePort.

6. **Verify deployment:**
```bash
kubectl get pods -n cloud-portfolio
kubectl logs -f -l app=cloud-portfolio -n cloud-portfolio
```

## 🔄 CI/CD Pipeline

Automated pipeline using GitHub Actions that runs on every push to main:

**Pipeline Stages:**

1. **Test**: Linting and unit tests
2. **Build**: Multi-architecture Docker image build
3. **Push**: Automatic push to Docker Hub with multiple tags
4. **Security Scan**: Trivy vulnerability scanning
5. **Notify**: Success notification

**Automatic Tagging:**
- `latest` - Most recent build from main
- `v1.0.0` - Semantic version from Git tags
- `main-abc1234` - Branch name + short SHA
- `1`, `1.0` - Major and major.minor versions

### Setting Up CI/CD

**Required GitHub Secrets:**

Navigate to: Repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Your Docker Hub account name |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker Hub → Account Settings → Security → New Access Token |

**To generate Docker Hub token:**
1. Login to Docker Hub
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Give it a name (e.g., "github-actions")
5. Copy the token (you won't see it again!)
6. Add as `DOCKERHUB_TOKEN` secret in GitHub

The pipeline will automatically run on every push to main and on Git tags.

## 📁 Project Structure
```
cloud-container-portfolio/
│
├── README.md                      # This file
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
├── CONTRIBUTING.md                # Contribution guidelines
├── .env.example                   # Environment template
│
├── app/                           # Application code
│   ├── Dockerfile                 # Multi-stage Docker build
│   ├── requirements.txt           # Python dependencies
│   ├── app.py                     # Flask application
│   └── templates/
│       └── index.html             # Web interface
│
├── kubernetes/                    # Kubernetes manifests
│   ├── namespace.yaml             # Namespace definition
│   ├── configmap.yaml             # Configuration
│   ├── deployment.yaml            # Main deployment
│   ├── service.yaml               # LoadBalancer service
│   └── gpu-deployment.yaml        # GPU workload example
│
├── aws/                           # AWS configuration
│   ├── s3-policy.json             # IAM policy example
│   ├── iam-role.json              # IAM role structure
│   └── integration-guide.md       # AWS setup guide
│
├── docs/                          # Documentation
│   ├── architecture.md            # System architecture
│   ├── deployment-steps.md        # Deployment guide
│   └── docker-hub-guide.md        # Docker Hub guide
│
└── .github/
    └── workflows/
        └── ci-cd.yaml             # CI/CD pipeline
```

## 📚 Documentation

Comprehensive documentation available in the `docs/` directory:

- **[Architecture](docs/architecture.md)**: System design, data flow, components
- **[Deployment Guide](docs/deployment-steps.md)**: Step-by-step deployment instructions
- **[Docker Hub Guide](docs/docker-hub-guide.md)**: Image management and publication
- **[AWS Integration](aws/integration-guide.md)**: AWS setup and security practices

## 🔐 Security Considerations

This project implements multiple security best practices:

**Credential Management:**
- ❌ No credentials committed to repository
- ✅ Kubernetes Secrets for sensitive data
- ✅ Environment variables for configuration
- ✅ `.env` in `.gitignore`

**Container Security:**
- ✅ Non-root user in containers
- ✅ Minimal base image (python:3.11-slim)
- ✅ No privilege escalation
- ✅ Dropped all capabilities
- ✅ Read-only root filesystem where possible

**Network Security:**
- ✅ TLS/HTTPS for AWS communication
- ✅ No exposed unnecessary ports
- ✅ Network policies (future enhancement)

**Access Control:**
- ✅ IAM least-privilege policies
- ✅ Private S3 bucket
- ✅ RBAC in Kubernetes
- ✅ Namespace isolation

## 🔮 Future Enhancements

Potential improvements demonstrating forward thinking:

- [ ] **Horizontal Pod Autoscaler** - Scale based on CPU/memory metrics
- [ ] **Monitoring Stack** - Prometheus + Grafana for observability
- [ ] **Service Mesh** - Istio for advanced traffic management
- [ ] **Caching Layer** - Redis for performance optimization
- [ ] **Database Integration** - RDS for metadata storage
- [ ] **Multi-region Deployment** - High availability across regions
- [ ] **API Gateway** - AWS API Gateway for advanced routing
- [ ] **Backup Automation** - Scheduled S3 backups
- [ ] **Load Testing** - Performance benchmarks with k6
- [ ] **Cost Optimization** - S3 Intelligent-Tiering

## 📊 Metrics & Monitoring

**Application Metrics:**
- Health endpoint: `/health`
- Readiness endpoint: `/ready`
- Info endpoint: `/info`

**Kubernetes Metrics:**
```bash
# Pod resource usage
kubectl top pods -n cloud-portfolio

# Deployment status
kubectl get deployment -n cloud-portfolio

# Service endpoints
kubectl get endpoints -n cloud-portfolio
```

**AWS CloudWatch:**
- S3 request metrics
- Bucket size monitoring
- Error rate tracking

## 🧪 Testing

**Local Testing:**
```bash
# Run Flask app locally
cd app
python app.py

# Test with curl
curl http://localhost:5000/health
curl http://localhost:5000/files
```

**Container Testing:**
```bash
# Build and run
docker build -t test-image ./app
docker run -p 5000:5000 test-image

# Check logs
docker logs <container-id>
```

**Kubernetes Testing:**
```bash
# Check pod health
kubectl get pods -n cloud-portfolio

# View logs
kubectl logs -f -l app=cloud-portfolio -n cloud-portfolio

# Port forward for testing
kubectl port-forward -n cloud-portfolio svc/cloud-portfolio-service 8080:80
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick contribution guide:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Contact

**Guilherme Vassoller Daros**
- GitHub: [@guiDaros](https://github.com/guiDaros/)
- LinkedIn: [Guilherme Vassoller Daros](https://www.linkedin.com/in/guilherme-vassoller-daros/)
- Email: guivdaros@gmail.com

## 🙏 Acknowledgments

- Flask framework and Python community
- Kubernetes and CNCF ecosystem
- AWS documentation and best practices
- Docker and containerization community
- Open source contributors

---

**⭐ If this project demonstrates skills relevant to your needs, please consider starring the repository!**

**🔗 Project Link**: https://github.com/yourusername/cloud-container-portfolio