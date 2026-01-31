Write-Host "🚀 AWS Fargate Deployment Script" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan

# Step 1: Check prerequisites
Write-Host "`n🔍 Step 1: Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Install Docker Desktop first!" -ForegroundColor Red
    exit
}

# Check AWS CLI
try {
    aws --version | Out-Null
    Write-Host "✅ AWS CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ AWS CLI not found. Downloading installer..." -ForegroundColor Yellow
    $url = "https://awscli.amazonaws.com/AWSCLIV2.msi"
    $output = "$env:TEMP\AWSCLIV2.msi"
    Invoke-WebRequest -Uri $url -OutFile $output
    Write-Host "Downloaded. Please run the installer manually." -ForegroundColor Yellow
    Write-Host "File: $output" -ForegroundColor Cyan
    exit
}

# Step 2: Push to Docker Hub
Write-Host "`n🐳 Step 2: Pushing to Docker Hub..." -ForegroundColor Yellow

# Get current image
$images = docker images --format "{{.Repository}}:{{.Tag}}"
$image = $images | Select-String "genai-api"

if (-not $image) {
    Write-Host "❌ No genai-api image found. Build it first:" -ForegroundColor Red
    Write-Host "   docker build -t genai-api:latest ." -ForegroundColor Cyan
    exit
}

# Tag and push
Write-Host "Tagging image: $image" -ForegroundColor Cyan
docker tag genai-api:latest inescherif/genai-api:latest
docker push inescherif/genai-api:latest

Write-Host "✅ Image pushed to Docker Hub" -ForegroundColor Green
Write-Host "   View at: https://hub.docker.com/r/inescherif/genai-api" -ForegroundColor Cyan

# Step 3: AWS Configuration
Write-Host "`n☁️ Step 3: AWS Setup Instructions" -ForegroundColor Yellow
Write-Host @"

MANUAL STEPS TO COMPLETE:

1. LOGIN to AWS Console: https://aws.amazon.com/console/

2. SEARCH for 'ECS' and click it

3. CREATE CLUSTER:
   - Click 'Create Cluster'
   - Choose 'Networking only (Fargate)'
   - Name: genai-cluster
   - Click 'Create'

4. CREATE TASK DEFINITION:
   - Click 'Task Definitions' → 'Create new'
   - Launch type: FARGATE
   - Name: genai-task
   - Task size: 0.5 vCPU, 1 GB memory
   - Add container:
     * Name: genai-api
     * Image: inescherif/genai-api:latest
     * Port: 8000
   - Environment variable:
     * Key: OPENAI_API_KEY
     * Value: [YOUR_OPENAI_KEY]

5. CREATE SERVICE:
   - Go to your cluster → 'Create service'
   - Launch type: FARGATE
   - Service name: genai-service
   - Number of tasks: 1
   - VPC: Default VPC
   - Subnets: Select ALL
   - Security group: Create new (allow ports 80, 8000)
   - Load balancer: Create new ALB
   - Click 'Create'

6. WAIT 5 minutes, then get your URL from Load Balancer DNS!

"@ -ForegroundColor White

Write-Host "`n🎯 Deployment Guide Complete!" -ForegroundColor Green
Write-Host "Your API will be available at: http://[load-balancer-dns]/" -ForegroundColor Cyan