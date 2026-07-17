# 🌐 Deploy StadiumIQ to Google Cloud

## Overview
This guide will help you deploy StadiumIQ to Google Cloud Platform (GCP) using **Cloud Run** - a fully managed serverless platform that's perfect for containerized applications.

**Why Cloud Run?**
- ✅ Automatic scaling (scales to zero when not in use = cost-effective)
- ✅ Built-in HTTPS and custom domains
- ✅ Pay only for what you use
- ✅ Easy deployment from GitHub
- ✅ Works seamlessly with Gemini API (both Google products)

**Estimated Cost:** ~$5-10/month for moderate traffic (includes free tier)

---

## Prerequisites

1. **Google Cloud Account**
   - Go to https://console.cloud.google.com/
   - Sign in with your Google account
   - Enable billing (free tier available: $300 credit for 90 days)

2. **Install Google Cloud CLI** (optional but recommended)
   - Download: https://cloud.google.com/sdk/docs/install
   - Or use Cloud Shell (built into GCP console)

---

## Method 1: Deploy via Google Cloud Console (Easiest - No CLI needed)

### Step 1: Enable Required APIs

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one:
   - Click project dropdown → "New Project"
   - Name: `stadiumiq`
   - Click "Create"

3. Enable required APIs:
   - Go to **APIs & Services** → **Enable APIs and Services**
   - Search and enable:
     - ✅ Cloud Run API
     - ✅ Cloud Build API
     - ✅ Artifact Registry API
     - ✅ Secret Manager API

### Step 2: Create Secret for API Key

1. Go to **Security** → **Secret Manager**
2. Click **"Create Secret"**
   - Name: `GEMINI_API_KEY`
   - Secret value: `YOUR_ACTUAL_GEMINI_API_KEY_HERE`
   - Click **"Create Secret"**

### Step 3: Deploy Backend to Cloud Run

1. Go to **Cloud Run** → **Create Service**

2. Configure container:
   - Click **"Continuously deploy from a repository (source)"**
   - Click **"Set up with Cloud Build"**
   
3. Connect GitHub repository:
   - Provider: **GitHub**
   - Click **"Authenticate"** and authorize Google Cloud
   - Repository: `nishithapandey/stadiumIQ`
   - Branch: `main`
   - Build Type: **Dockerfile**
   - Source location: `/backend/Dockerfile`
   - Click **"Save"**

4. Configure service:
   - **Service name**: `stadiumiq-backend`
   - **Region**: Choose closest to your users (e.g., `us-central1`, `asia-south1`)
   - **CPU allocation**: "CPU is only allocated during request processing"
   - **Autoscaling**: Min 0, Max 10 instances
   - **Ingress**: "All"
   - **Authentication**: "Allow unauthenticated invocations"

5. Configure container:
   - **Container port**: `8000`
   - **Memory**: `512 MiB`
   - **CPU**: `1`
   - **Request timeout**: `300` seconds
   - **Maximum requests per container**: `80`

6. Add environment variables:
   - Click **"Variables & Secrets"** → **"Reference a Secret"**
   - Select secret: `GEMINI_API_KEY`
   - Reference method: "Exposed as environment variable"
   - Name: `GEMINI_API_KEY`
   - Click **"Done"**
   
   - Click **"Add Variable"**
   - Name: `ALLOWED_ORIGINS`
   - Value: `*` (we'll update this after frontend is deployed)

7. Click **"Create"**

8. Wait 3-5 minutes for deployment. You'll get a URL like:
   ```
   https://stadiumiq-backend-xxxxx-uc.a.run.app
   ```

9. Test backend:
   - Visit: `https://stadiumiq-backend-xxxxx-uc.a.run.app/health`
   - Should return: `{"status":"ok","service":"StadiumIQ"}`

### Step 4: Deploy Frontend to Cloud Run

Since Cloud Run is designed for backend services, we'll use **Firebase Hosting** for the frontend (better for static sites):

#### Option A: Firebase Hosting (Recommended for Frontend)

1. Go to **Firebase Console**: https://console.firebase.google.com/
2. Click **"Add project"** → Select your GCP project `stadiumiq`
3. Enable Google Analytics (optional) → Click **"Create project"**

4. Install Firebase CLI on your local machine:
```bash
npm install -g firebase-tools
```

5. Login and initialize:
```bash
cd stadiumiq/frontend

# Login to Firebase
firebase login

# Initialize Firebase
firebase init hosting
```

Configure:
- **Project**: Select `stadiumiq`
- **Public directory**: `dist`
- **Single-page app**: `Yes`
- **GitHub deployment**: `No`

6. Update environment variable:
Create `frontend/.env.production`:
```env
VITE_API_URL=https://stadiumiq-backend-xxxxx-uc.a.run.app
```
(Replace with your actual backend URL)

7. Build and deploy:
```bash
# Build the frontend
npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

8. You'll get a URL like:
```
https://stadiumiq.web.app
```

9. **Update Backend CORS**:
   - Go back to Cloud Run → `stadiumiq-backend` → **Edit & Deploy New Revision**
   - Update `ALLOWED_ORIGINS` to: `https://stadiumiq.web.app`
   - Click **"Deploy"**

#### Option B: Cloud Storage + Cloud CDN (Alternative)

1. Create Cloud Storage bucket:
```bash
gsutil mb -p stadiumiq -c STANDARD -l US gs://stadiumiq-frontend/
gsutil web set -m index.html -e index.html gs://stadiumiq-frontend/
```

2. Make bucket public:
```bash
gsutil iam ch allUsers:objectViewer gs://stadiumiq-frontend/
```

3. Build and upload frontend:
```bash
cd frontend
npm run build
gsutil -m rsync -r dist gs://stadiumiq-frontend/
```

4. Access at: `https://storage.googleapis.com/stadiumiq-frontend/index.html`

---

## Method 2: Deploy via Google Cloud CLI (Faster for experienced users)

### Prerequisites
- Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
- Authenticate: `gcloud auth login`

### Deploy Backend

```bash
cd stadiumiq

# Set project
gcloud config set project stadiumiq

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create secret
echo -n "YOUR_ACTUAL_GEMINI_API_KEY_HERE" | \
  gcloud secrets create GEMINI_API_KEY --data-file=-

# Deploy backend
gcloud run deploy stadiumiq-backend \
  --source ./backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-env-vars ALLOWED_ORIGINS="*" \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10
```

### Deploy Frontend

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize (if not done)
cd frontend
firebase init hosting

# Build
npm run build

# Deploy
firebase deploy --only hosting
```

---

## Method 3: Deploy via GitHub Actions (CI/CD - Best for Production)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Google Cloud

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  PROJECT_ID: stadiumiq
  BACKEND_SERVICE: stadiumiq-backend
  REGION: us-central1

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - id: auth
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: ${{ env.BACKEND_SERVICE }}
          region: ${{ env.REGION }}
          source: ./backend
          secrets: |
            GEMINI_API_KEY=GEMINI_API_KEY:latest
          env_vars: |
            ALLOWED_ORIGINS=https://stadiumiq.web.app

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install and Build
        working-directory: ./frontend
        run: |
          npm ci
          npm run build
      
      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SA_KEY }}
          channelId: live
          projectId: stadiumiq
```

Setup secrets in GitHub:
- `GCP_SA_KEY`: Service account JSON key
- `FIREBASE_SA_KEY`: Firebase service account key

---

## Configuration Files for Google Cloud

### 1. Create `backend/app.yaml` (for App Engine alternative)

```yaml
runtime: python311
entrypoint: uvicorn main:app --host 0.0.0.0 --port $PORT

env_variables:
  ALLOWED_ORIGINS: "https://stadiumiq.web.app"

automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.65

resources:
  cpu: 1
  memory_gb: 0.5
  disk_size_gb: 10
```

### 2. Create `frontend/firebase.json`

```json
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      }
    ]
  }
}
```

---

## Cost Optimization

### Cloud Run Pricing
- **Free tier**: 2 million requests/month
- **Compute**: ~$0.00002400/vCPU-second, ~$0.00000250/GiB-second
- **Requests**: ~$0.40/million requests
- **Networking**: ~$0.12/GB

**Estimated monthly cost for moderate traffic:**
- 100,000 requests/month
- 200ms average response time
- 512MB memory
- **Total: ~$2-5/month**

### Firebase Hosting Pricing
- **Free tier**: 10 GB storage, 360 MB/day transfer
- **Paid**: $0.026/GB storage, $0.15/GB transfer
- **Estimated: ~$1-3/month**

### Tips to Reduce Costs:
1. ✅ Enable **autoscaling to zero** (scale down when not in use)
2. ✅ Use **Cloud CDN** for frontend caching
3. ✅ Set **max instances** to prevent runaway costs
4. ✅ Monitor usage in **Cloud Console**
5. ✅ Set up **budget alerts**

---

## Custom Domain Setup

### For Cloud Run (Backend)
1. Go to **Cloud Run** → `stadiumiq-backend` → **Manage Custom Domains**
2. Click **"Add Mapping"**
3. Enter domain: `api.yourdomain.com`
4. Follow DNS configuration instructions
5. Add A/AAAA records in your domain registrar

### For Firebase Hosting (Frontend)
1. Go to **Firebase Console** → **Hosting** → **Add Custom Domain**
2. Enter domain: `stadiumiq.yourdomain.com`
3. Verify ownership
4. Add DNS records provided by Firebase
5. Wait for SSL certificate provisioning (automatic)

---

## Monitoring & Logging

### Enable Monitoring
1. Go to **Cloud Run** → `stadiumiq-backend` → **Logs**
2. View real-time logs, errors, and requests
3. Set up **Alerts**:
   - High error rate
   - High latency
   - High memory usage

### Set Up Uptime Checks
1. Go to **Monitoring** → **Uptime Checks**
2. Create check:
   - URL: `https://stadiumiq-backend-xxxxx.run.app/health`
   - Frequency: Every 5 minutes
   - Alert if down for 2 consecutive checks

---

## Troubleshooting

### Backend deployment fails
```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log [BUILD_ID]

# Check service logs
gcloud run logs read stadiumiq-backend --region us-central1 --limit 50
```

### Frontend build fails
```bash
# Test build locally
cd frontend
npm run build

# Check Firebase hosting status
firebase hosting:channel:list
```

### CORS errors
Update backend CORS settings:
```bash
gcloud run services update stadiumiq-backend \
  --region us-central1 \
  --update-env-vars ALLOWED_ORIGINS="https://stadiumiq.web.app,https://yourdomain.com"
```

### API key issues
Verify secret:
```bash
gcloud secrets versions access latest --secret="GEMINI_API_KEY"
```

---

## Security Best Practices

1. ✅ **Use Secret Manager** for API keys (not environment variables)
2. ✅ **Enable Cloud Armor** for DDoS protection
3. ✅ **Configure CORS** properly (specific origins only)
4. ✅ **Enable Cloud Audit Logs**
5. ✅ **Set up IAM roles** properly
6. ✅ **Use HTTPS only** (automatic with Cloud Run/Firebase)
7. ✅ **Regular security updates** via automated deployments

---

## Quick Commands Reference

```bash
# View service status
gcloud run services describe stadiumiq-backend --region us-central1

# Update environment variable
gcloud run services update stadiumiq-backend \
  --region us-central1 \
  --update-env-vars KEY=VALUE

# Scale service
gcloud run services update stadiumiq-backend \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 20

# Delete service
gcloud run services delete stadiumiq-backend --region us-central1

# View logs
gcloud run logs read stadiumiq-backend --region us-central1 --tail

# Deploy new revision
gcloud run deploy stadiumiq-backend \
  --source ./backend \
  --region us-central1
```

---

## Final Checklist

- [ ] GCP project created
- [ ] APIs enabled (Cloud Run, Cloud Build, Secret Manager)
- [ ] API key stored in Secret Manager
- [ ] Backend deployed to Cloud Run
- [ ] Backend health endpoint working
- [ ] Frontend deployed to Firebase Hosting
- [ ] CORS configured correctly
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up
- [ ] Budget alerts configured
- [ ] Test all features work
- [ ] Security review completed

---

## Support & Resources

- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Firebase Hosting Docs**: https://firebase.google.com/docs/hosting
- **GCP Free Tier**: https://cloud.google.com/free
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Status Dashboard**: https://status.cloud.google.com/

---

## Estimated Deployment Time

- **Method 1 (Console)**: 20-30 minutes
- **Method 2 (CLI)**: 10-15 minutes
- **Method 3 (CI/CD)**: 30 minutes setup, then automatic

---

🎉 **Your StadiumIQ will be live on Google Cloud with enterprise-grade infrastructure!**

Questions? Check the troubleshooting section or create an issue on GitHub.
