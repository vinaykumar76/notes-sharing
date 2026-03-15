# Vercel Deployment Guide

## Prerequisites
1. A MySQL database (local or hosted)
2. Vercel account connected to your GitHub repo
3. Environment variables configured

## Setup Steps

### 1. Configure Environment Variables
Add these environment variables to your Vercel project settings:

- **DB_HOST**: Your MySQL database host (e.g., `localhost` or `db.example.com`)
- **DB_USER**: MySQL username
- **DB_PASSWORD**: MySQL password
- **DB_NAME**: Database name (e.g., `p2p_notes`)
- **FLASK_SECRET_KEY**: A secure random string for Flask sessions

### 2. Local Development
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your local database credentials

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run locally:
   ```bash
   python app.py
   ```

### 3. Deploy to Vercel
1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Import your repository
4. Add environment variables in project settings
5. Click "Deploy"

## Important Notes

- **Database**: Ensure your MySQL database is accessible from Vercel's servers (not localhost)
- **File Uploads**: Currently stored in `/static/uploads/`. For production, consider using cloud storage (S3, Cloudinary)
- **Database Backups**: Set up regular backups for your MySQL database
- **SSL**: Vercel provides free HTTPS for all deployments

## Troubleshooting

### 502 Bad Gateway Error
- Check that all environment variables are set correctly
- Verify database connectivity
- Check app logs in Vercel dashboard

### Database Connection Failed
- Ensure DB_HOST is publicly accessible (not `localhost`)
- Verify firewall rules allow Vercel's IPs
- Check database credentials

### File Upload Issues
- Check that `/static/uploads/` directory has write permissions
- For serverless, consider migrating to cloud storage
