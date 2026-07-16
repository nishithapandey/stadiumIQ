# 🚀 StadiumIQ Deployment Guide

## ✅ Current Status
- ✅ Code pushed to GitHub: https://github.com/nishithapandey/stadiumIQ
- ✅ Application tested and working locally
- ✅ API key configured (in .env, not in git)
- ✅ All features functional

---

## 🎯 Deployment Options

### Option 1: Docker Deployment (Recommended for Production)

#### Prerequisites
- Install Docker Desktop: https://www.docker.com/products/docker-desktop/
- Or install Docker + Docker Compose on Linux

#### Steps
1. **Clone the repository** (on your deployment server)
```bash
git clone https://github.com/nishithapandey/stadiumIQ.git
cd stadiumIQ
```

2. **Create .env file**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build -d
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health Check: http://localhost:8000/health

5. **View logs**
```bash
docker-compose logs -f
```

6. **Stop the application**
```bash
docker-compose down
```

---

### Option 2: Cloud Deployment

#### A. Deploy to **Render** (Free Tier Available)

**Backend Deployment:**
1. Go to https://render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repo: `nishithapandey/stadiumIQ`
4. Configure:
   - **Name**: `stadiumiq-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `GEMINI_API_KEY`: Your API key
     - `ALLOWED_ORIGINS`: `https://stadiumiq-frontend.onrender.com` (update after frontend deploy)
5. Click "Create Web Service"

**Frontend Deployment:**
1. Click "New +" → "Static Site"
2. Connect your GitHub repo: `nishithapandey/stadiumIQ`
3. Configure:
   - **Name**: `stadiumiq-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Environment Variables**:
     - `VITE_API_URL`: Your backend URL (e.g., `https://stadiumiq-backend.onrender.com`)
4. Click "Create Static Site"

**Update CORS:**
- Go back to backend service settings
- Update `ALLOWED_ORIGINS` to include your frontend URL

---

#### B. Deploy to **Vercel** (Frontend) + **Railway** (Backend)

**Frontend on Vercel:**
1. Go to https://vercel.com/
2. Import Git Repository: `nishithapandey/stadiumIQ`
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**:
     - `VITE_API_URL`: Your backend URL
4. Deploy

**Backend on Railway:**
1. Go to https://railway.app/
2. New Project → Deploy from GitHub
3. Select `nishithapandey/stadiumIQ`
4. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `GEMINI_API_KEY`: Your API key
     - `ALLOWED_ORIGINS`: Your Vercel frontend URL
5. Deploy

---

#### C. Deploy to **AWS** (Most Scalable)

**Using AWS ECS (Elastic Container Service):**

1. **Build and push Docker images**
```bash
# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag images
docker build -t stadiumiq-backend ./backend
docker build -t stadiumiq-frontend ./frontend

docker tag stadiumiq-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/stadiumiq-backend:latest
docker tag stadiumiq-frontend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/stadiumiq-frontend:latest

# Push to ECR
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/stadiumiq-backend:latest
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/stadiumiq-frontend:latest
```

2. **Create ECS Task Definitions**
- Backend: Port 8000
- Frontend: Port 80
- Set environment variables via AWS Systems Manager Parameter Store

3. **Create ECS Service**
- Use Application Load Balancer
- Configure health checks: `/health` for backend
- Set up auto-scaling based on CPU/memory

4. **Configure Route 53**
- Point domain to ALB
- Enable HTTPS with ACM certificate

---

### Option 3: Manual VPS Deployment (DigitalOcean, Linode, etc.)

**Prerequisites:**
- Ubuntu 22.04 server with SSH access
- Domain name (optional but recommended)

**Steps:**

1. **Connect to your server**
```bash
ssh root@your-server-ip
```

2. **Install dependencies**
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Install Nginx (for reverse proxy)
apt install nginx -y

# Install certbot (for SSL)
apt install certbot python3-certbot-nginx -y
```

3. **Clone and deploy**
```bash
cd /opt
git clone https://github.com/nishithapandey/stadiumIQ.git
cd stadiumIQ

# Create .env
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# Run with Docker Compose
docker compose up -d
```

4. **Configure Nginx reverse proxy**
```bash
nano /etc/nginx/sites-available/stadiumiq
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/stadiumiq /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

5. **Enable SSL with Let's Encrypt**
```bash
certbot --nginx -d your-domain.com
```

6. **Set up auto-restart**
```bash
# Create systemd service
nano /etc/systemd/system/stadiumiq.service
```

Add:
```ini
[Unit]
Description=StadiumIQ Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/stadiumIQ
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
systemctl enable stadiumiq
systemctl start stadiumiq
```

---

## 🔒 Production Security Checklist

- [ ] **API Key Security**
  - Store in environment variables
  - Use AWS Secrets Manager / Azure Key Vault in production
  - Rotate keys regularly

- [ ] **CORS Configuration**
  - Update `ALLOWED_ORIGINS` to only include your production frontend URL
  - Remove localhost from production

- [ ] **HTTPS**
  - Enable SSL/TLS certificates
  - Force HTTPS redirects

- [ ] **Rate Limiting**
  - Add rate limiting to API endpoints
  - Use services like Cloudflare for DDoS protection

- [ ] **Monitoring**
  - Set up error tracking (Sentry, Rollbar)
  - Configure uptime monitoring (UptimeRobot, Pingdom)
  - Enable application logs

- [ ] **Backups**
  - Regular backups of environment configuration
  - Document recovery procedures

---

## 📊 Post-Deployment Testing

After deployment, test these features:

1. **Health Check**
   - Visit `/health` endpoint
   - Should return `{"status":"ok","service":"StadiumIQ"}`

2. **Frontend Access**
   - Load the main page
   - Check all 4 tabs load

3. **AI Chat**
   - Test chat in all 4 personas
   - Test all 4 languages
   - Verify AI responses work

4. **Real-time Features**
   - Check crowd dashboard auto-refreshes
   - Verify navigation generates directions

5. **Accessibility**
   - Test high contrast mode
   - Test font size controls
   - Test keyboard navigation

---

## 🐛 Troubleshooting

### Backend won't start
- Check `GEMINI_API_KEY` is set correctly
- Verify port 8000 is available
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify `VITE_API_URL` is correct
- Check CORS settings in backend
- Test backend health endpoint directly

### Gemini API errors
- Verify API key is valid at https://aistudio.google.com/
- Check API quota hasn't been exceeded
- Ensure model name is `gemini-2.5-flash`

---

## 📞 Support

- **GitHub Issues**: https://github.com/nishithapandey/stadiumIQ/issues
- **Documentation**: See README.md for detailed features
- **API Documentation**: Visit `/docs` on your backend URL for interactive API docs

---

## 🎉 You're Ready!

Your StadiumIQ application is now:
- ✅ Fully functional
- ✅ Pushed to GitHub
- ✅ Ready for deployment

Choose your deployment method above and go live! 🚀
