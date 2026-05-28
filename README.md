# Flask App on AWS ECS Fargate

A containerized Flask web application with MySQL, deployed to AWS ECS Fargate using CloudFormation and automated via GitHub Actions CI/CD.

---

## Architecture Overview

```
Internet
   │
   ▼
Application Load Balancer (port 80)
   │
   ▼
ECS Fargate Task (port 5000)
   │  ├── Flask App (python3 app.py via supervisord)
   │  └── MySQL Server (mysqld_safe via supervisord)
   │
   ▼
Amazon ECR (Docker image registry)
Amazon CloudWatch Logs (/ecs/secure-container-app)
```

**AWS Resources created by CloudFormation:**
- VPC with 2 public subnets across 2 availability zones
- Internet Gateway + Route Table
- Application Load Balancer (ALB) with Security Group
- ECS Cluster (Fargate) with Security Group
- ECR Repository
- ECS Task Definition + ECS Service
- IAM Task Execution Role
- CloudWatch Log Group

---

## Project Structure

```
flask-aws-project/
├── .aws/
│   └── cloudformation.yaml       # Full AWS infrastructure definition
├── .github/
│   └── workflows/
│       └── deploy.yml            # GitHub Actions CI/CD pipeline
├── templates/
│   └── index.html                # Flask HTML template
├── app.py                        # Flask application
├── Dockerfile                    # Container build instructions
├── requirements.txt              # Python dependencies
├── supervisord.conf              # Process manager (MySQL + Flask)
└── .env                          # Local environment variables (do not commit)
```

---

## Prerequisites

Make sure the following are installed on your local machine:

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.x | Run app locally | https://python.org |
| Docker Desktop | Build & run containers | https://docker.com |
| AWS CLI v2 | Deploy to AWS | https://aws.amazon.com/cli |
| Git | Version control | https://git-scm.com |

---

## Part 1 — Run the App Locally

### Step 1 — Clone the repository

```bash
git clone https://github.com/<your-username>/flask-aws-project.git
cd flask-aws-project
```

### Step 2 — Create a virtual environment and install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3 — Set up local environment variables

Create a `.env` file in the project root:

```env
DB_HOST=127.0.0.1
DB_USER=flask_user
DB_PASSWORD=VaultSecurePassword2026!
DB_NAME=production_db
APP_PORT=5000
```

### Step 4 — Start MySQL locally and create the database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE IF NOT EXISTS production_db;
CREATE USER IF NOT EXISTS 'flask_user'@'localhost' IDENTIFIED BY 'VaultSecurePassword2026!';
GRANT ALL PRIVILEGES ON production_db.* TO 'flask_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 5 — Run the Flask app

```bash
python app.py
```

Open your browser at `http://localhost:5000` — you should see the app with MySQL version info.

Health check endpoint: `http://localhost:5000/health` → returns `{"status": "ok"}`

---

## Part 2 — Build and Test with Docker Locally

### Step 6 — Build the Docker image

```bash
docker build -t dynamic-secure-app .
```

### Step 7 — Run the container locally

```bash
docker run -p 5000:5000 \
  -e DB_HOST=127.0.0.1 \
  -e DB_USER=flask_user \
  -e DB_PASSWORD=VaultSecurePassword2026! \
  -e DB_NAME=production_db \
  -e APP_PORT=5000 \
  dynamic-secure-app
```

Open `http://localhost:5000` to verify the container works before pushing to AWS.

---

## Part 3 — AWS Setup

### Step 8 — Create an IAM user for deployments

1. Go to **AWS Console → IAM → Users → Create user**
2. Username: `flask-deploy-user`
3. Attach policies:
   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AWSCloudFormationFullAccess`
   - `IAMFullAccess`
   - `ElasticLoadBalancingFullAccess`
   - `AmazonVPCFullAccess`
   - `CloudWatchLogsFullAccess`
4. Go to **Security credentials → Create access key** → choose CLI
5. Save the `Access Key ID` and `Secret Access Key` — you will need these next

> ⚠️ Never share or commit your credentials. If exposed, revoke them immediately from IAM.

### Step 9 — Configure AWS CLI

```bash
aws configure
```

Enter when prompted:
```
AWS Access Key ID:     <your-access-key-id>
AWS Secret Access Key: <your-secret-access-key>
Default region name:   ap-south-1
Default output format: json
```

Verify it works:
```bash
aws sts get-caller-identity
```

You should see your Account ID `135306227278` in the response.

---

## Part 4 — GitHub Repository Setup

### Step 10 — Push code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/flask-aws-project.git
git push -u origin main
```

### Step 11 — Add GitHub Secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these two secrets:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM access key ID |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret access key |

> These are encrypted by GitHub and injected securely into the workflow at runtime.

---

## Part 5 — Automated Deployment via GitHub Actions

Every push to the `main` branch triggers the full deployment pipeline automatically.

### Deployment sequence

| Step | Action | Waits? |
|------|--------|--------|
| 1 | Checkout source code | — |
| 2 | Configure AWS credentials from GitHub Secrets | — |
| 3 | Deploy base infrastructure via CloudFormation (VPC, ECR, ECS Cluster, ALB) using placeholder image | — |
| 4 | Wait for CloudFormation stack to reach stable state | ✅ |
| 5 | Authenticate Docker to Amazon ECR | — |
| 6 | Build Docker image from Dockerfile | — |
| 7 | Tag and push image to ECR (`:latest` + commit SHA) | — |
| 8 | Redeploy CloudFormation with real ECR image + ECS Service enabled | — |
| 9 | Wait for ECS Service tasks to reach RUNNING state | ✅ |
| 10 | Print live application URL from CloudFormation outputs | — |
| 11 | Fetch last 100 lines of container logs from CloudWatch (runs even on failure) | — |

### Trigger a deployment

```bash
git add .
git commit -m "Deploy to ECS"
git push origin main
```

Then go to your GitHub repo → **Actions** tab to watch the pipeline run.

---

## Part 6 — Manual Deployment (without GitHub Actions)

If you want to deploy manually from your local machine:

### Step 1 — Deploy base infrastructure

```bash
aws cloudformation deploy \
  --template-file .aws/cloudformation.yaml \
  --stack-name flask-secure-stack \
  --region ap-south-1 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides DeployService=false
```

### Step 2 — Authenticate Docker to ECR

```bash
aws ecr get-login-password --region ap-south-1 | docker login \
  --username AWS \
  --password-stdin 135306227278.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 3 — Build and push image to ECR

```bash
docker build -t dynamic-secure-app .

docker tag dynamic-secure-app:latest \
  135306227278.dkr.ecr.ap-south-1.amazonaws.com/dynamic-secure-app:latest

docker push \
  135306227278.dkr.ecr.ap-south-1.amazonaws.com/dynamic-secure-app:latest
```

### Step 4 — Deploy ECS Service

```bash
aws cloudformation deploy \
  --template-file .aws/cloudformation.yaml \
  --stack-name flask-secure-stack \
  --region ap-south-1 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DeployService=true \
    AppImage=135306227278.dkr.ecr.ap-south-1.amazonaws.com/dynamic-secure-app:latest
```

### Step 5 — Get the application URL

```bash
aws cloudformation describe-stacks \
  --stack-name flask-secure-stack \
  --region ap-south-1 \
  --query "Stacks[0].Outputs[?OutputKey=='ExternalUrl'].OutputValue" \
  --output text
```

---

## Part 7 — Test the Application on AWS

### Step 12 — Access the app

Open the ALB DNS URL printed in the deployment output:
```
http://<alb-dns-name>.ap-south-1.elb.amazonaws.com
```

### Step 13 — Test the health endpoint

```bash
curl http://<alb-dns-name>.ap-south-1.elb.amazonaws.com/health
```

Expected response:
```json
{"status": "ok"}
```

### Step 14 — Check ECS task status

```bash
aws ecs list-tasks \
  --cluster DynamicSecureCluster \
  --service-name flask-service \
  --region ap-south-1
```

### Step 15 — View container logs in CloudWatch

```bash
# List available log streams
aws logs describe-log-streams \
  --log-group-name /ecs/secure-container-app \
  --region ap-south-1

# Fetch logs from a specific stream
aws logs get-log-events \
  --log-group-name /ecs/secure-container-app \
  --log-stream-name secureapp/flask-container/<task-id> \
  --region ap-south-1 \
  --limit 50 \
  --query 'events[*].message' \
  --output text
```

Or go to **AWS Console → CloudWatch → Log groups → /ecs/secure-container-app**

---

## CloudFormation Parameters Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `AWSAccountId` | `135306227278` | Your AWS account ID |
| `AWSRegion` | `ap-south-1` | Deployment region |
| `DeployService` | `false` | Set to `true` after ECR image is pushed |
| `AppImage` | `public.ecr.aws/docker/library/python:3.11-slim` | Container image URI |
| `SecureDBUser` | `flask_user` | MySQL username |
| `SecureDBPassword` | `VaultSecurePassword2026!` | MySQL password |
| `SecureDBName` | `production_db` | MySQL database name |

---

## Cleanup — Delete All AWS Resources

To avoid ongoing charges, delete the stack when done:

```bash
aws cloudformation delete-stack \
  --stack-name flask-secure-stack \
  --region ap-south-1

aws cloudformation wait stack-delete-complete \
  --stack-name flask-secure-stack \
  --region ap-south-1

echo "Stack deleted successfully"
```

> Note: The ECR repository must be emptied before the stack can be deleted. Go to **AWS Console → ECR → dynamic-secure-app → Delete all images** first, or run:
> ```bash
> aws ecr batch-delete-image \
>   --repository-name dynamic-secure-app \
>   --image-ids imageTag=latest \
>   --region ap-south-1
> ```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `VPCId not found` CloudFormation error | Wrong property casing | Use `VpcId` not `VPCId` |
| `EarlyValidation` changeset failure | ECR image doesn't exist yet | First deploy uses placeholder image, real image passed in step 8 |
| ECS task stuck in PENDING | Image pull failure or bad entrypoint | Check CloudWatch logs at `/ecs/secure-container-app` |
| ALB returns 502/503 | Health check failing | Ensure `/health` returns 200, check ECS security group allows port 5000 from ALB |
| `TargetGroupArn` invalid | Wrong placement in ECS Service | Must be inside `LoadBalancers` block, not top-level |
| Task running but app not accessible | Flask not binding to `0.0.0.0` | Ensure `app.run(host='0.0.0.0')` in `app.py` |
