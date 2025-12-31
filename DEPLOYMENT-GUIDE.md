# Authentication Service Deployment Guide

This guide explains how to deploy the Better Auth authentication service to production and integrate it with your Docusaurus frontend.

## Architecture Overview

Your application has three components:
1. **Frontend (Docusaurus)**: Already deployed on Vercel
   - URL: https://book-writing-physical-ai-humanoid-r.vercel.app
2. **Backend API (FastAPI)**: Deployed on Hugging Face Spaces
   - URL: https://junaidkh84-python-backend.hf.space
3. **Auth Service (Node.js/Express)**: Needs deployment (this guide)
   - Location: `E:\Junaid\Hackathon-I\Hugging Face\python-backend\auth-service\`

## Prerequisites

- Vercel account (https://vercel.com)
- Vercel CLI installed globally: `npm install -g vercel`
- Git installed
- GitHub account (optional, for continuous deployment)

## Deployment Steps

### Step 1: Prepare Auth Service for Deployment

The auth service is already configured with:
- ✅ `vercel.json` - Vercel deployment configuration
- ✅ `.gitignore` - Git ignore rules
- ✅ `.env.example` - Environment variable template
- ✅ `README.md` - Documentation
- ✅ Production-ready Express server
- ✅ CORS configured for your frontend

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. **Open terminal in auth-service directory**:
   ```bash
   cd "E:\Junaid\Hackathon-I\Hugging Face\python-backend\auth-service"
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy to Vercel** (first deployment):
   ```bash
   vercel
   ```

   You'll be asked:
   - Set up and deploy? → **Yes**
   - Which scope? → Select your account
   - Link to existing project? → **No**
   - Project name? → `book-auth-service` (or your preferred name)
   - Directory? → **./** (press Enter)

4. **Configure Environment Variables**:

   After initial deployment, add environment variables:
   ```bash
   vercel env add DATABASE_URL
   ```
   Paste your database URL: `postgres://1e4dde8c8bc714f0d54ffbdfbeff181d4e5ba19e51a2588641479b5e4c877a80:sk_T5ebRMIFML8SpIZ0KVJgS@db.prisma.io:5432/postgres?sslmode=require`

   Select environment: **Production**

   ```bash
   vercel env add BETTER_AUTH_SECRET
   ```
   Paste your secret: `HbB0LQgjv6FCmBzbxUon7MvjGyx2iuJv`

   Select environment: **Production**

   ```bash
   vercel env add BETTER_AUTH_URL
   ```
   Paste the URL you got from the initial deployment (e.g., `https://book-auth-service.vercel.app`)

   Select environment: **Production**

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

6. **Note your deployment URL**:
   After deployment completes, Vercel will show you the URL:
   ```
   ✅ Production: https://book-auth-service.vercel.app
   ```

   **SAVE THIS URL** - you'll need it for the next steps.

#### Option B: Using GitHub + Vercel Dashboard

1. **Initialize Git repository** (if not already done):
   ```bash
   cd "E:\Junaid\Hackathon-I\Hugging Face\python-backend\auth-service"
   git init
   git add .
   git commit -m "Initial commit: Better Auth service"
   ```

2. **Create GitHub repository**:
   - Go to https://github.com/new
   - Repository name: `book-auth-service`
   - Visibility: Private (recommended)
   - Click "Create repository"

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/book-auth-service.git
   git branch -M main
   git push -u origin main
   ```

4. **Import to Vercel**:
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your `book-auth-service` repository
   - Click "Import"

5. **Configure Environment Variables in Vercel Dashboard**:
   - In project settings, go to "Environment Variables"
   - Add the following variables for **Production**:
     ```
     DATABASE_URL=postgres://1e4dde8c8bc714f0d54ffbdfbeff181d4e5ba19e51a2588641479b5e4c877a80:sk_T5ebRMIFML8SpIZ0KVJgS@db.prisma.io:5432/postgres?sslmode=require
     BETTER_AUTH_SECRET=HbB0LQgjv6FCmBzbxUon7MvjGyx2iuJv
     BETTER_AUTH_URL=https://your-deployment-url.vercel.app
     ```

6. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Note the deployment URL (e.g., `https://book-auth-service.vercel.app`)

### Step 3: Update Auth Service Configuration

After deployment, you need to update `BETTER_AUTH_URL` with the actual deployment URL:

1. **In Vercel Dashboard**:
   - Go to your auth service project
   - Settings → Environment Variables
   - Edit `BETTER_AUTH_URL`
   - Change to: `https://book-auth-service.vercel.app` (replace with your actual URL)
   - Save

2. **Redeploy** to apply changes:
   ```bash
   vercel --prod
   ```

### Step 4: Update Frontend to Use Deployed Auth Service

1. **Update `authClient.ts`**:

   Edit `E:\Junaid\Hackathon-I\Book-Wr-Claude\docs\src\utils\authClient.ts`:

   ```typescript
   const getBaseURL = () => {
     if (typeof window !== 'undefined') {
       // Development: use local auth service
       if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
         return 'http://localhost:3001';
       }

       // Production: Your deployed auth service URL
       return 'https://book-auth-service.vercel.app'; // ← UPDATE THIS
     }

     return "http://localhost:3001";
   };
   ```

2. **Update Auth Service CORS Origins**:

   Edit `E:\Junaid\Hackathon-I\Hugging Face\python-backend\auth-service\auth.js`:

   Make sure your frontend URL is in `trustedOrigins`:
   ```javascript
   trustedOrigins: [
     "http://localhost:3000",
     "https://book-writing-physical-ai-humanoid-r.vercel.app",
   ],
   ```

   And in `E:\Junaid\Hackathon-I\Hugging Face\python-backend\auth-service\index.js`:
   ```javascript
   app.use(cors({
     origin: [
       "http://localhost:3000",
       "https://book-writing-physical-ai-humanoid-r.vercel.app"
     ],
     credentials: true,
   }));
   ```

3. **Commit and deploy frontend**:
   ```bash
   cd "E:\Junaid\Hackathon-I\Book-Wr-Claude"
   git add .
   git commit -m "Update auth service URL to production"
   git push
   ```

   Vercel will automatically redeploy your frontend.

### Step 5: Verify Deployment

1. **Test Auth Service Health**:
   ```bash
   curl https://book-auth-service.vercel.app/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "Better Auth Service",
     "timestamp": "2025-12-31T..."
   }
   ```

2. **Test Authentication Flow**:
   - Visit: https://book-writing-physical-ai-humanoid-r.vercel.app/auth
   - Try to sign up with a test account
   - Check browser DevTools → Network tab for API calls
   - Verify calls are going to your auth service URL

3. **Check for Errors**:
   - **Vercel Logs**: https://vercel.com/dashboard → Your project → Deployments → Latest → Logs
   - **Browser Console**: F12 → Console tab
   - Look for CORS errors, 500 errors, or network failures

## Troubleshooting

### CORS Errors
**Problem**: `Access-Control-Allow-Origin` error in browser console

**Solution**:
- Verify frontend URL is in `trustedOrigins` in `auth.js`
- Verify frontend URL is in `cors({ origin: [...] })` in `index.js`
- Redeploy auth service after changes

### 500 Internal Server Error
**Problem**: Auth endpoints return 500 error

**Solution**:
- Check Vercel logs for error details
- Verify all environment variables are set correctly
- Ensure `DATABASE_URL` is valid and accessible
- Test database connection with Prisma Studio locally

### Database Connection Issues
**Problem**: Prisma client errors or connection timeouts

**Solution**:
- Verify `DATABASE_URL` is correct in Vercel environment variables
- Check Vercel Postgres database is accessible
- Run `npx prisma generate` locally to verify schema
- Ensure Prisma schema is pushed: `npx prisma db push`

### Authentication Not Working
**Problem**: Sign up/sign in not working, no errors shown

**Solution**:
- Check browser Network tab for failed requests
- Verify `BETTER_AUTH_URL` matches deployment URL
- Check auth service logs in Vercel
- Test auth endpoints directly with curl:
  ```bash
  curl -X POST https://book-auth-service.vercel.app/api/auth/sign-up \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'
  ```

## Security Checklist

Before going live:

- [ ] `BETTER_AUTH_SECRET` is at least 32 characters and randomly generated
- [ ] Database connection uses SSL (`?sslmode=require`)
- [ ] Environment variables are not committed to Git
- [ ] `.env` file is in `.gitignore`
- [ ] CORS origins are limited to your actual domains
- [ ] Email verification is enabled in production (`requireEmailVerification: true`)
- [ ] Auth service is deployed on HTTPS (Vercel provides this automatically)

## Production Checklist

- [ ] Auth service deployed to Vercel
- [ ] Environment variables configured in Vercel
- [ ] `BETTER_AUTH_URL` updated to deployment URL
- [ ] Frontend `authClient.ts` updated with production URL
- [ ] CORS origins configured for production domain
- [ ] Database schema pushed to production database
- [ ] Health check endpoint responding correctly
- [ ] Sign up flow tested in production
- [ ] Sign in flow tested in production
- [ ] Session persistence tested
- [ ] Sign out tested

## Next Steps

After successful deployment:

1. **Test Full Authentication Flow**:
   - Sign up a test user
   - Verify user in database (Prisma Studio)
   - Test sign in
   - Test session persistence
   - Test sign out

2. **Optional Enhancements**:
   - Set up email verification (requires email service)
   - Add OAuth providers (Google, GitHub, etc.)
   - Implement password reset flow
   - Add rate limiting
   - Set up monitoring and alerts

3. **Documentation**:
   - Document auth endpoints for your team
   - Update README with production URLs
   - Create runbook for common issues

## Support

If you encounter issues:

1. Check Vercel deployment logs
2. Review browser console for errors
3. Test auth endpoints with curl
4. Verify environment variables
5. Check database connectivity

## Environment URLs Reference

| Environment | Component | URL |
|-------------|-----------|-----|
| Production | Frontend | https://book-writing-physical-ai-humanoid-r.vercel.app |
| Production | Backend API | https://junaidkh84-python-backend.hf.space |
| Production | Auth Service | https://book-auth-service.vercel.app (UPDATE) |
| Local | Frontend | http://localhost:3000 |
| Local | Auth Service | http://localhost:3001 |
| Database | Vercel Postgres | db.prisma.io:5432 |

---

**Last Updated**: 2025-12-31
**Author**: Junaid Khan
**Project**: Book Writing Physical AI & Humanoid Robotics
