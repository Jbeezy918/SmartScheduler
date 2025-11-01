# 🚀 SmartScheduler Deployment Guide

## Quick Deploy to Heroku (Recommended for MVP)

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- Git initialized in project

### Steps

1. **Install Heroku CLI** (if not already installed)
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from
# https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku App**
```bash
cd SmartScheduler
heroku create smartscheduler-prod
```

4. **Add PostgreSQL Database**
```bash
heroku addons:create heroku-postgresql:mini
```

5. **Add Redis (for caching)**
```bash
heroku addons:create heroku-redis:mini
```

6. **Set Environment Variables**
```bash
heroku config:set OPENAI_API_KEY=your_openai_key
heroku config:set TWILIO_ACCOUNT_SID=your_twilio_sid
heroku config:set TWILIO_AUTH_TOKEN=your_twilio_token
heroku config:set SENDGRID_API_KEY=your_sendgrid_key
heroku config:set STRIPE_SECRET_KEY=your_stripe_key
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
```

7. **Create Procfile**
```bash
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

8. **Deploy**
```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

9. **Open Your App**
```bash
heroku open
```

10. **View Logs**
```bash
heroku logs --tail
```

---

## Alternative: Deploy to Railway

Railway is even easier than Heroku:

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Add PostgreSQL and Redis from Railway
5. Set environment variables in dashboard
6. Deploy! ✅

---

## Alternative: Deploy to Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database
6. Set environment variables
7. Deploy!

---

## Production Deployment (AWS/GCP/Azure)

### Architecture
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────▼────┐
    │   API   │ (FastAPI)
    │ Servers │ (Auto-scaling)
    └────┬────┘
         │
    ┌────▼────┐
    │Database │ (PostgreSQL)
    └─────────┘
         │
    ┌────▼────┐
    │  Cache  │ (Redis)
    └─────────┘
         │
    ┌────▼────┐
    │  Queue  │ (Celery)
    └─────────┘
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t smartscheduler .
docker run -p 8000:8000 smartscheduler
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/smartscheduler
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=smartscheduler
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  celery:
    build: .
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

**Run:**
```bash
docker-compose up -d
```

---

## Environment Variables

Required for production:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# API Keys
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
SENDGRID_API_KEY=SG...
STRIPE_SECRET_KEY=sk_live_...

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Config
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=smartscheduler.io,www.smartscheduler.io
```

---

## DNS & Domain Setup

1. **Purchase domain** (e.g., from Namecheap, Google Domains)

2. **Configure DNS:**
```
Type    Name    Value                           TTL
A       @       your-server-ip                  3600
CNAME   www     your-heroku-app.herokuapp.com   3600
CNAME   api     your-heroku-app.herokuapp.com   3600
```

3. **Enable SSL** (Heroku does this automatically)

---

## Monitoring & Logging

### Sentry (Error Tracking)
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### LogDNA / Datadog
```bash
heroku addons:create logdna:quaco
```

### Uptime Monitoring
- UptimeRobot (free)
- Pingdom
- StatusCake

---

## Scaling

### Heroku Scaling
```bash
# Scale web dynos
heroku ps:scale web=2

# Upgrade dyno type
heroku ps:resize web=standard-2x

# Add worker dynos for background jobs
heroku ps:scale worker=1
```

### Performance Optimization
- Enable Redis caching
- Use CDN for static files
- Implement database indexing
- Use connection pooling
- Add rate limiting

---

## Database Migrations

Using Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# On Heroku
heroku run alembic upgrade head
```

---

## Backup Strategy

### Database Backups
```bash
# Heroku Postgres automatic backups
heroku addons:create scheduler:standard

# Manual backup
heroku pg:backups:capture
heroku pg:backups:download
```

### Automated Daily Backups
```bash
# Schedule daily at 2 AM
heroku scheduler:add "pg_dump $DATABASE_URL > backup.sql && upload-to-s3"
```

---

## Security Checklist

- [ ] HTTPS enabled (SSL certificate)
- [ ] Environment variables secured
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] SQL injection protection (use ORMs)
- [ ] Input validation on all endpoints
- [ ] Authentication & authorization
- [ ] Regular dependency updates
- [ ] Security headers configured
- [ ] Database backups automated

---

## Cost Estimates

### Heroku (Small Business)
- **Dyno:** $25/month (Hobby)
- **Database:** $9/month (Mini Postgres)
- **Redis:** $15/month (Premium 0)
- **Total:** ~$49/month

### Heroku (Growing Business)
- **Dynos:** $50/month (2x Standard 1X)
- **Database:** $50/month (Standard 0)
- **Redis:** $30/month (Premium 1)
- **Add-ons:** $20/month (monitoring, logging)
- **Total:** ~$150/month

### AWS (Enterprise)
- **EC2:** $100/month (t3.medium x2)
- **RDS:** $150/month (db.t3.medium)
- **ElastiCache:** $50/month (cache.t3.small)
- **Load Balancer:** $20/month
- **Total:** ~$320/month

---

## Support

For deployment help:
- **Email:** devops@smartscheduler.io
- **Docs:** https://docs.smartscheduler.io/deployment
- **Slack:** smartscheduler-community.slack.com

---

## Next Steps After Deployment

1. ✅ Verify all endpoints work
2. ✅ Test appointment booking flow
3. ✅ Configure email/SMS providers
4. ✅ Set up monitoring
5. ✅ Run security scan
6. ✅ Load test
7. ✅ Create status page
8. ✅ Launch! 🚀
