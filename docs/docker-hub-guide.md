# Docker Hub Publication Guide

## Overview

This guide documents how the cloud-container-portfolio Docker image is built, tagged, and published to Docker Hub for public distribution.

## Docker Hub Repository

**Repository URL**: https://hub.docker.com/r/yourusername/cloud-container-portfolio

**Repository Type**: Public (freely accessible)

**Automated Builds**: Enabled via GitHub Actions

## Image Information

### Current Tags

| Tag | Description | Size | Architectures |
|-----|-------------|------|---------------|
| `latest` | Most recent stable build | ~150MB | linux/amd64, linux/arm64 |
| `v1.0.0` | Initial release | ~150MB | linux/amd64 |
| `v1.1.0` | Added monitoring features | ~155MB | linux/amd64, linux/arm64 |

### Image Specifications

**Base Image**: `python:3.11-slim`
- Minimal Debian-based image
- Python 3.11 runtime
- Reduced attack surface

**Optimization Techniques**:
- Multi-stage build to reduce final image size
- Only production dependencies included
- Build artifacts removed
- Layers optimized for caching

**Exposed Ports**: 5000 (HTTP)

**Health Check**: Built-in health check on `/health` endpoint

**Default Command**: Gunicorn WSGI server with optimized worker configuration

## Manual Build and Push Process

### Prerequisites

- Docker installed and running
- Docker Hub account created
- Repository created on Docker Hub
- Logged into Docker CLI

### Step 1: Login to Docker Hub
````bash
docker login
````

**Security Best Practice**: Use access tokens instead of passwords
1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Give it a name (e.g., "local-development")
4. Copy the token
5. Use token as password when prompted

### Step 2: Build the Image

Navigate to the app directory (where Dockerfile is located):
````bash
cd app
````

Build with version tag:
````bash
docker build -t yourusername/cloud-container-portfolio:v1.0.0 .
````

**Build Arguments** (optional):
````bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg APP_VERSION=1.0.0 \
  -t yourusername/cloud-container-portfolio:v1.0.0 .
````

**Multi-platform Build** (for ARM support):
````bash
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t yourusername/cloud-container-portfolio:v1.0.0 \
  --push .
````

### Step 3: Tag the Image

Create additional tags:
````bash
# Tag as latest
docker tag yourusername/cloud-container-portfolio:v1.0.0 \
           yourusername/cloud-container-portfolio:latest

# Tag as stable
docker tag yourusername/cloud-container-portfolio:v1.0.0 \
           yourusername/cloud-container-portfolio:stable
````

**Tagging Best Practices**:
- Use semantic versioning (major.minor.patch)
- Always maintain a `latest` tag
- Consider environment tags (dev, staging, prod)
- Use git commit SHA for traceability

### Step 4: Test the Image Locally

Before pushing, always test:
````bash
# Run container
docker run -d -p 5000:5000 \
  --name test-app \
  -e AWS_ACCESS_KEY_ID=test \
  -e AWS_SECRET_ACCESS_KEY=test \
  -e AWS_BUCKET_NAME=test-bucket \
  -e AWS_REGION=us-east-1 \
  yourusername/cloud-container-portfolio:v1.0.0

# Test health endpoint
curl http://localhost:5000/health

# Check logs
docker logs test-app

# Inspect image
docker inspect yourusername/cloud-container-portfolio:v1.0.0

# Check image size
docker images | grep cloud-container-portfolio

# Cleanup
docker stop test-app
docker rm test-app
````

### Step 5: Push to Docker Hub

Push specific version:
````bash
docker push yourusername/cloud-container-portfolio:v1.0.0
````

Push latest tag:
````bash
docker push yourusername/cloud-container-portfolio:latest
````

Push all tags:
````bash
docker push --all-tags yourusername/cloud-container-portfolio
````

**Monitor upload progress:**
- Shows layer upload status
- Indicates which layers are already cached
- Displays final manifest digest

### Step 6: Verify on Docker Hub

1. Visit https://hub.docker.com/r/yourusername/cloud-container-portfolio
2. Check that tags appear correctly
3. Verify image size
4. Check last updated timestamp
5. Ensure repository is public

## Automated Build with GitHub Actions

### Workflow Configuration

The repository includes a GitHub Actions workflow (`.github/workflows/ci-cd.yaml`) that automatically builds and pushes images.

**Trigger Events**:
- Push to `main` branch
- New Git tags (e.g., `v1.0.0`)
- Manual workflow dispatch

**Workflow Steps**:
1. Checkout code from repository
2. Set up Docker Buildx (for multi-platform builds)
3. Login to Docker Hub using secrets
4. Extract metadata (tags, labels)
5. Build Docker image
6. Push to Docker Hub
7. Update deployment (optional)

### Required GitHub Secrets

Configure these in GitHub repository settings → Secrets and variables → Actions:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Your account name |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Generate in Docker Hub settings |

**Creating Secrets**:
1. Go to repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add `DOCKERHUB_USERNAME` with your username
5. Add `DOCKERHUB_TOKEN` with access token from Docker Hub

### Automatic Versioning

**Git Tag Based Versioning**:
````bash
# Create and push tag
git tag v1.0.0
git push origin v1.0.0
````

This automatically triggers build with tags:
- `yourusername/cloud-container-portfolio:v1.0.0`
- `yourusername/cloud-container-portfolio:latest`
- `yourusername/cloud-container-portfolio:1`
- `yourusername/cloud-container-portfolio:1.0`

**Branch Based Versioning**:
- Push to `main` → `latest` tag
- Push to `develop` → `develop` tag
- Pull requests → `pr-123` tag (not pushed)

## Docker Hub Repository Configuration

### Repository Settings

**General Settings**:
- Visibility: Public ✅
- Description: "Cloud-native portfolio application demonstrating Docker, Kubernetes, and AWS integration"
- Categories: Developer Tools, Cloud Infrastructure

**Collaborators**:
- Add team members if needed
- Set appropriate permissions (Read, Write, Admin)

### Repository README

Docker Hub displays a README on the repository page. Create it with:

**Title**: Cloud Container Portfolio

**Badges**:
````markdown
![Docker Pulls](https://img.shields.io/docker/pulls/yourusername/cloud-container-portfolio)
![Docker Image Size](https://img.shields.io/docker/image-size/yourusername/cloud-container-portfolio)
![Docker Image Version](https://img.shields.io/docker/v/yourusername/cloud-container-portfolio)
````

**Quick Start**:
````markdown
## Quick Start

Pull the image:
```bash
docker pull yourusername/cloud-container-portfolio:latest
```

Run the container:
```bash
docker run -d -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e AWS_BUCKET_NAME=your-bucket \
  -e AWS_REGION=us-east-1 \
  --name cloud-portfolio \
  yourusername/cloud-container-portfolio:latest
```

Access the application at http://localhost:5000
````

**Environment Variables**:
````markdown
## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | No | AWS access key | mock-access-key |
| `AWS_SECRET_ACCESS_KEY` | No | AWS secret key | mock-secret-key |
| `AWS_BUCKET_NAME` | No | S3 bucket name | cloud-portfolio-demo |
| `AWS_REGION` | No | AWS region | us-east-1 |
````

**Links**:
````markdown
## Links

- [GitHub Repository](https://github.com/yourusername/cloud-container-portfolio)
- [Documentation](https://github.com/yourusername/cloud-container-portfolio/tree/main/docs)
- [Issue Tracker](https://github.com/yourusername/cloud-container-portfolio/issues)
````

## Image Management Best Practices

### Version Control

**Semantic Versioning**:
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

**Tag Strategy**:
- Always tag with full version: `v1.2.3`
- Maintain floating tags: `1`, `1.2`, `latest`
- Use descriptive tags: `stable`, `beta`, `rc1`

### Image Lifecycle

**Development Flow**:
1. Develop feature locally
2. Build and test image locally
3. Push to Docker Hub with dev tag
4. Test in staging environment
5. Tag as release version
6. Push release tags
7. Update production

**Deprecation Process**:
1. Announce deprecation in README
2. Keep deprecated tags for 6 months minimum
3. Add deprecation labels
4. Provide migration guide
5. Remove after grace period

### Security Scanning

**Docker Hub Automated Scanning**:
- Enable vulnerability scanning in repository settings
- Reviews each pushed image
- Reports known CVEs
- Provides severity ratings

**Local Scanning**:
````bash
# Using Docker Scout
docker scout cves yourusername/cloud-container-portfolio:latest

# Using Trivy
trivy image yourusername/cloud-container-portfolio:latest
````

**Best Practices**:
- Scan before pushing to production
- Update base images regularly
- Monitor security advisories
- Fix critical vulnerabilities immediately

## Usage Examples

### Pull and Run

**Basic usage**:
````bash
docker pull yourusername/cloud-container-portfolio:latest
docker run -p 5000:5000 yourusername/cloud-container-portfolio:latest
````

**With environment variables**:
````bash
docker run -p 5000:5000 \
  -e AWS_REGION=us-west-2 \
  -e AWS_BUCKET_NAME=my-bucket \
  yourusername/cloud-container-portfolio:latest
````

**With Docker Compose**:
````yaml
version: '3.8'
services:
  app:
    image: yourusername/cloud-container-portfolio:latest
    ports:
      - "5000:5000"
    environment:
      AWS_REGION: us-east-1
      AWS_BUCKET_NAME: my-bucket
    env_file:
      - .env
````

### Kubernetes Deployment

**Direct from Docker Hub**:
````yaml
spec:
  containers:
  - name: app
    image: yourusername/cloud-container-portfolio:v1.0.0
    imagePullPolicy: Always
````

**With specific digest** (for immutability):
````yaml
spec:
  containers:
  - name: app
    image: yourusername/cloud-container-portfolio@sha256:abc123...
````

## Monitoring and Analytics

### Docker Hub Metrics

**Available Metrics**:
- Total pulls
- Pulls per day/week/month
- Unique users
- Geographic distribution
- Tag popularity

**Accessing Metrics**:
1. Login to Docker Hub
2. Navigate to repository
3. Click "Insights" tab
4. View analytics dashboard

### Usage Tracking

**GitHub Badge** (shows pull count):
````markdown
![Docker Pulls](https://img.shields.io/docker/pulls/yourusername/cloud-container-portfolio)
````

**Docker Hub API**:
````bash
curl https://hub.docker.com/v2/repositories/yourusername/cloud-container-portfolio/
````

## Troubleshooting

### Issue: Push Denied

**Cause**: Not logged in or incorrect credentials

**Solution**:
````bash
docker logout
docker login
# Enter correct credentials
````

### Issue: Image Too Large

**Cause**: Unnecessary files in image

**Solution**:
- Use `.dockerignore` file
- Multi-stage builds
- Remove build dependencies
- Clean package manager cache

### Issue: Failed to Push

**Cause**: Network issues or rate limiting

**Solution**:
- Check internet connection
- Retry after delay
- Check Docker Hub status
- Verify account is not rate-limited

### Issue: Tag Already Exists

**Cause**: Trying to push existing tag

**Solution**:
````bash
# Overwrite (use with caution)
docker push yourusername/cloud-container-portfolio:latest

# Or use new version
docker tag yourusername/cloud-container-portfolio:latest \
           yourusername/cloud-container-portfolio:v1.0.1
docker push yourusername/cloud-container-portfolio:v1.0.1
````

## Resources

- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Build Reference](https://docs.docker.com/engine/reference/builder/)
- [GitHub Actions Docker](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)