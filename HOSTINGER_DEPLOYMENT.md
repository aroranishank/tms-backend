# Hostinger Deployment Guide for TMS Backend

This guide covers deploying your FastAPI Task Management System backend to Hostinger hosting.

## Prerequisites

1. Hostinger hosting account with Python support
2. Git repository access
3. SSH access to your Hostinger server

## Step 1: Prepare Your Project

### 1.1 Create Production Requirements
Ensure your `requirements.txt` includes all dependencies:
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
bcrypt
python-jose[cryptography]
python-multipart
python-dotenv
passlib[bcrypt]
```

### 1.2 Create WSGI/ASGI Entry Point
Create `wsgi.py` in your project root:
```python
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 2: Database Configuration

### 2.1 Update Environment Variables
Create production `.env` file:
```
SECRET_KEY=your_production_secret_key_here
DATABASE_URL=sqlite:///./taskmanager.db
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2.2 Consider Database Migration
For production, consider using PostgreSQL or MySQL instead of SQLite:
```
DATABASE_URL=postgresql://username:password@localhost/dbname
```

## Step 3: Upload to Hostinger

### Method 1: Using Git (Recommended)

1. **SSH into your Hostinger server:**
   ```bash
   ssh username@your-server-ip
   ```

2. **Navigate to your domain directory:**
   ```bash
   cd public_html/your-domain.com
   ```

3. **Clone your repository:**
   ```bash
   git clone https://github.com/yourusername/task-management-system.git
   cd task-management-system/tms-backend
   ```

### Method 2: Using File Manager
1. Zip your project files
2. Upload via Hostinger File Manager
3. Extract in the appropriate directory

## Step 4: Set Up Python Environment

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Step 5: Configure Hostinger Settings

### 5.1 Python App Configuration
In Hostinger Control Panel:
1. Go to "Website" section
2. Select your domain
3. Click "Python" or "Python App"
4. Set:
   - **Python Version**: 3.8 or higher
   - **Application Root**: `/path/to/your/tms-backend`
   - **Application URL**: `/api` (or `/`)
   - **Application Startup File**: `wsgi.py`
   - **Application Entry Point**: `app`

### 5.2 Environment Variables
Set environment variables in Hostinger panel:
- `SECRET_KEY`: Your production secret
- `DATABASE_URL`: Your database connection string
- `CORS_ORIGINS`: Your frontend domain

## Step 6: Database Setup

1. **Initialize database:**
   ```bash
   cd /path/to/your/tms-backend
   source venv/bin/activate
   python -c "from app.db_init import init_db; init_db()"
   ```

## Step 7: Configure Web Server

### For Apache (.htaccess)
Create `.htaccess` in your domain root:
```apache
RewriteEngine On
RewriteCond %{REQUEST_URI} ^/api/.*$
RewriteRule ^api/(.*)$ /cgi-bin/python-app.cgi/$1 [L]
```

### For Nginx
Add to your Nginx config:
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Step 8: SSL Certificate

1. Enable SSL in Hostinger Control Panel
2. Update CORS_ORIGINS to use HTTPS URLs
3. Test API endpoints with HTTPS

## Step 9: Testing Deployment

1. **Test the root endpoint:**
   ```bash
   curl https://yourdomain.com/api/
   ```

2. **Check API documentation:**
   Visit: `https://yourdomain.com/api/docs`

3. **Test authentication:**
   ```bash
   curl -X POST https://yourdomain.com/api/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpass"
   ```

## Step 10: Monitoring and Maintenance

### Log Files
Check application logs:
```bash
tail -f /path/to/logs/error.log
tail -f /path/to/logs/access.log
```

### Database Backup
Set up regular database backups:
```bash
# For SQLite
cp taskmanager.db backups/taskmanager_$(date +%Y%m%d).db

# For PostgreSQL
pg_dump dbname > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure all dependencies are installed
   - Check Python path configuration

2. **Database Connection:**
   - Verify DATABASE_URL format
   - Check file permissions for SQLite

3. **CORS Issues:**
   - Update CORS_ORIGINS with production domains
   - Include both www and non-www versions

4. **Permission Errors:**
   ```bash
   chmod 755 /path/to/your/app
   chmod 644 /path/to/your/files
   ```

### Performance Optimization

1. **Use Production ASGI Server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

2. **Enable Caching:**
   - Use Redis for session storage
   - Implement response caching

3. **Database Optimization:**
   - Use connection pooling
   - Add database indexes
   - Consider using PostgreSQL for better performance

## Security Checklist

- [ ] Strong SECRET_KEY in production
- [ ] HTTPS enabled
- [ ] Environment variables secured
- [ ] Database credentials protected
- [ ] CORS properly configured
- [ ] Error messages don't expose sensitive info
- [ ] Rate limiting implemented
- [ ] Input validation in place

## Maintenance Commands

```bash
# Update code
git pull origin main
pip install -r requirements.txt

# Restart application (method depends on Hostinger setup)
# Usually handled automatically by Hostinger

# Database migrations (if using Alembic)
alembic upgrade head

# Check application status
curl https://yourdomain.com/api/
```

## Support

For Hostinger-specific issues:
- Check Hostinger documentation
- Contact Hostinger support
- Review error logs in control panel

For application issues:
- Check application logs
- Verify environment configuration
- Test locally first