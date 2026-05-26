# Deployment Guide - Medical Report Interpreter

## 🚀 Deployment Options

### 1. Docker Deployment (Recommended)

**Prerequisites:**
- Docker installed
- Docker Compose installed

**Steps:**
```bash
# 1. Build and start containers
docker-compose up --build -d

# 2. Check logs
docker-compose logs -f

# 3. Access application
Frontend: http://localhost:3000
Backend: http://localhost:8000
```

**Environment Variables:**
Create `.env` file:
```
DATABASE_URL=postgresql://postgres:yourpassword@postgres:5432/medical
SECRET_KEY=your-secret-key-change-this
OPENAI_API_KEY=sk-your-openai-key-here
```

### 2. Cloud Deployment Options

#### A. Vercel (Frontend) + Railway (Backend + DB)

**Frontend on Vercel:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel deploy --prod
```

**Backend on Railway:**
1. Push code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Create new project from GitHub repo
4. Add PostgreSQL database
5. Set environment variables
6. Deploy

**Environment Variables for Railway:**
```
DATABASE_URL=[auto-populated]
SECRET_KEY=[generate random]
OPENAI_API_KEY=[your key]
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
```

#### B. AWS Deployment

**Components:**
- **Frontend**: S3 + CloudFront
- **Backend**: ECS or EC2
- **Database**: RDS PostgreSQL
- **File Storage**: S3

**Backend (ECS):**
```bash
# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t medical-backend ./backend
docker tag medical-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/medical-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/medical-backend:latest
```

**Frontend (S3 + CloudFront):**
```bash
# Build frontend
cd frontend
npm run build

# Deploy to S3
aws s3 sync out/ s3://medical-reports-frontend/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### C. Azure Deployment

**Components:**
- **Frontend**: Azure Static Web Apps
- **Backend**: Azure App Service
- **Database**: Azure Database for PostgreSQL

**Deploy Frontend:**
```bash
# Using Azure Static Web Apps CLI
cd frontend
npm install -g @azure/static-web-apps-cli
swa deploy
```

**Deploy Backend:**
```bash
# Using Azure CLI
az webapp up --name medical-backend --resource-group medical-rg --runtime "PYTHON:3.11"
```

#### D. Digital Ocean

**App Platform Deployment:**
1. Push to GitHub
2. Create new App in App Platform
3. Connect GitHub repo
4. Configure components:
   - Backend: Python app (backend/)
   - Frontend: Node.js app (frontend/)
   - Database: PostgreSQL managed database
5. Set environment variables
6. Deploy

### 3. Production Considerations

#### Security Checklist
- [ ] Change SECRET_KEY to a strong random value
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Set CORS_ORIGINS to specific domains
- [ ] Enable rate limiting
- [ ] Set DEBUG=False
- [ ] Use environment-specific .env files

#### Performance Optimization
- [ ] Use CDN for static assets
- [ ] Enable caching (Redis/Memcached)
- [ ] Use production-grade ASGI server (Gunicorn + Uvicorn)
- [ ] Database connection pooling
- [ ] Compress images/PDFs
- [ ] Enable br/gzip compression

#### Monitoring & Logging
- [ ] Set up application monitoring (DataDog, New Relic, etc.)
- [ ] Configure error tracking (Sentry)
- [ ] Set up log aggregation
- [ ] Enable health check endpoints
- [ ] Configure alerts for failures

#### Backup Strategy
- [ ] Automated database backups
- [ ] File storage backups (S3 versioning)
- [ ] Disaster recovery plan
- [ ] Regular restore testing

### 4. CI/CD Pipeline

**GitHub Actions Example:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          curl -X POST ${{ secrets.RAILWAY_DEPLOY_HOOK }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

### 5. Scaling Considerations

**Horizontal Scaling:**
- Use load balancer (ALB, NGINX)
- Stateless backend design
- Shared session storage (Redis)
- Multi-region deployment

**Vertical Scaling:**
- Increase container CPU/memory
- Database instance size
- Worker process count

**Auto-scaling Rules:**
- CPU utilization > 70%
- Memory utilization > 80%
- Request queue depth > 100

### 6. Cost Optimization

**Free Tier Options:**
- Railway: $5 free credit/month
- Vercel: Free for hobby projects
- Supabase: Free PostgreSQL (up to 500MB)
- Render: Free tier available

**Estimated Monthly Costs:**
- **Small (< 1000 users)**: $10-30/month
- **Medium (1000-10K users)**: $50-200/month
- **Large (10K+ users)**: $500+/month

### 7. Environment Variables Summary

**Required:**
```
DATABASE_URL=postgresql://...
SECRET_KEY=random-secret-key
```

**Optional:**
```
OPENAI_API_KEY=sk-...
ENABLE_AI_EXPLANATIONS=true
ENABLE_PDF_EXPORT=true
ENABLE_SHARING=true
CORS_ORIGINS=["https://yourdomain.com"]
DEBUG=false
```

### 8. Health Check Endpoints

```
GET /              - Basic health check
GET /health        - Detailed health status (TODO)
GET /api/reports   - Test database connectivity
```

### 9. Troubleshooting

**Common Issues:**
1. **Database connection failed**: Check DATABASE_URL and network access
2. **CORS errors**: Update CORS_ORIGINS in .env
3. **File upload fails**: Check UPLOAD_DIR permissions and disk space
4. **OCR errors**: Ensure sufficient memory for PaddleOCR
5. **PDF generation fails**: Install reportlab dependencies

**Logs:**
```bash
# Docker
docker-compose logs backend

# Railway
railway logs

# Vercel
vercel logs
```

---

Need help? Open an issue on GitHub or contact support.
