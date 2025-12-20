# Quickstart: FastAPI RAG Backend with Docusaurus Frontend Integration

**Feature**: 004-fastapi-docusaurus-integration
**Date**: 2025-12-11
**Phase**: 1 - Development Setup Guide

## Overview

This quickstart guide provides step-by-step instructions for setting up the local development environment to work on the Docusaurus chatbot integration with the FastAPI RAG backend.

## Prerequisites

### Required Software

- **Node.js**: >= 20.0 (check with `node --version`)
- **npm**: >= 9.0 (included with Node.js)
- **Python**: >= 3.9 (for backend, check with `python --version`)
- **Git**: For version control

### Backend Dependencies (from Spec-3)

- FastAPI backend from Spec-3 must be set up and operational
- Qdrant vector store populated with book embeddings (from Spec-1)
- OpenAI API key configured in backend `.env` file
- Cohere API key configured (if used for embeddings)

### Verify Prerequisites

```bash
# Check Node.js version
node --version  # Should be >= 20.0

# Check Python version
python --version  # Should be >= 3.9

# Check npm version
npm --version  # Should be >= 9.0
```

---

## Repository Structure

```
Book-Wr-Claude/
├── docs/                     # Docusaurus frontend
│   ├── src/
│   │   ├── components/      # React components (chatbot will be added here)
│   │   ├── theme/           # Theme customization
│   │   └── utils/           # Utility functions (API client)
│   ├── static/              # Static assets
│   ├── docusaurus.config.js # Docusaurus configuration
│   └── package.json         # Frontend dependencies
├── backend/                 # FastAPI backend (from Spec-3)
│   ├── src/                 # Backend source code
│   └── requirements.txt     # Backend dependencies
├── specs/                   # Feature specifications
│   └── 004-fastapi-docusaurus-integration/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md    # This file
│       └── contracts/
└── .env                     # Environment variables (API keys)
```

---

## Step 1: Clone and Navigate to Repository

```bash
# If not already cloned
git clone https://github.com/junaidkhen/Book-Writing-Physical-AI-Humanoid-Robotics.git
cd Book-Writing-Physical-AI-Humanoid-Robotics

# Check current branch
git branch

# Switch to feature branch (if not already on it)
git checkout 004-fastapi-docusaurus-integration
```

---

## Step 2: Install Frontend Dependencies

```bash
# Navigate to Docusaurus directory
cd docs

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

### Expected Dependencies

- `@docusaurus/core`: 3.9.2
- `@docusaurus/preset-classic`: 3.9.2
- `react`: 19.0.0
- `react-dom`: 19.0.0

---

## Step 3: Configure API Endpoints (Local Development)

### Option A: Using docusaurus.config.js (Recommended)

Edit `docs/docusaurus.config.js` and add custom fields:

```javascript
// docs/docusaurus.config.js
module.exports = {
  // ... existing config
  customFields: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
  },
};
```

### Option B: Create Runtime Configuration File

Create `docs/static/config/api-config.json`:

```json
{
  "development": {
    "apiBaseUrl": "http://localhost:8000"
  },
  "production": {
    "apiBaseUrl": "https://api.yourproject.com"
  }
}
```

---

## Step 4: Start Backend Services (FastAPI + Qdrant)

### Terminal 1: Start Qdrant (if not already running)

**If using Docker**:
```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

**If using Qdrant Cloud**:
- Ensure `.env` file contains:
  ```
  QDRANT_URL="https://your-cluster.qdrant.io:6333"
  QDRANT_API_KEY="your-api-key"
  ```

### Terminal 2: Start FastAPI Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if using venv)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install backend dependencies (if not already installed)
pip install -r requirements.txt

# Start FastAPI server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verify Backend is Running

Open browser and navigate to:
- **API Docs**: http://localhost:8000/docs (FastAPI Swagger UI)
- **Health Check**: http://localhost:8000/health

Expected health check response:
```json
{
  "status": "healthy",
  "qdrantConnected": true,
  "openaiAccessible": true,
  "uptime": 10,
  "timestamp": "2025-12-11T10:30:00Z"
}
```

---

## Step 5: Start Docusaurus Development Server

### Terminal 3: Start Docusaurus

```bash
# Navigate to docs directory
cd docs

# Start development server
npm start
```

**Expected Output**:
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### Verify Docusaurus is Running

Open browser and navigate to:
- **Homepage**: http://localhost:3000/
- Verify existing textbook content loads correctly

---

## Step 6: Configure CORS on Backend (If Not Already Done)

Edit `backend/main.py` to enable CORS for localhost:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Docusaurus dev server
        "http://localhost:3001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Restart FastAPI server after making changes**.

---

## Step 7: Test API Connectivity (Manual)

### Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test ask endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key components of a humanoid robot?", "topK": 5, "temperature": 0.1, "stream": false}'
```

### Using Browser Console (in Docusaurus site)

Open browser console (F12) on http://localhost:3000/ and run:

```javascript
// Test basic fetch
fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log('Health:', data))
  .catch(err => console.error('Error:', err));

// Test ask endpoint
fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "What is inverse kinematics?",
    topK: 5,
    temperature: 0.1,
    stream: false
  })
})
  .then(res => res.json())
  .then(data => console.log('Response:', data))
  .catch(err => console.error('Error:', err));
```

**Expected**: No CORS errors, successful JSON responses.

---

## Step 8: Development Workflow

### Recommended Terminal Setup

- **Terminal 1**: Qdrant (if using Docker)
- **Terminal 2**: FastAPI backend (`uvicorn` with `--reload`)
- **Terminal 3**: Docusaurus frontend (`npm start`)
- **Terminal 4**: Git commands, file editing, testing

### Hot Reload Behavior

- **Docusaurus**: Automatically reloads on file changes in `src/`, `docs/`, etc.
- **FastAPI**: Automatically reloads with `--reload` flag when Python files change
- **Static Config**: Requires manual page refresh for `static/config/api-config.json` changes

### Code Locations

- **Chatbot Components**: `docs/src/components/RAGChatbot/`
- **Theme Integration**: `docs/src/theme/Root.tsx`
- **API Client Logic**: `docs/src/utils/apiClient.ts`
- **Styles**: `docs/src/components/RAGChatbot/styles.module.css`

---

## Step 9: Running Tests

### Frontend Tests (Once Implemented)

```bash
cd docs
npm test
```

### Backend Tests (From Spec-3)

```bash
cd backend
pytest tests/
```

### Integration Tests (Manual E2E)

1. Submit query via chatbot UI
2. Verify response displays correctly
3. Check citations are clickable and navigate correctly
4. Test error scenarios (backend down, network error)
5. Test streaming functionality
6. Test text selection context feature

---

## Troubleshooting

### Issue: CORS Errors in Browser Console

**Symptom**:
```
Access to fetch at 'http://localhost:8000/ask' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solution**:
1. Verify CORS middleware is configured in `backend/main.py`
2. Ensure `allow_origins` includes `http://localhost:3000`
3. Restart FastAPI server after changes
4. Clear browser cache and hard refresh (Ctrl+Shift+R)

---

### Issue: FastAPI Backend Not Starting

**Symptom**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
cd backend
pip install -r requirements.txt

# If venv not activated, activate it first
source venv/bin/activate  # Linux/Mac
```

---

### Issue: Qdrant Connection Failed

**Symptom**:
```
{"status": "degraded", "qdrantConnected": false, ...}
```

**Solution**:
1. Verify Qdrant is running (`docker ps` or check Qdrant Cloud dashboard)
2. Check `.env` file has correct `QDRANT_URL` and `QDRANT_API_KEY`
3. Test direct connection: `curl http://localhost:6333/health` (local) or check Qdrant Cloud logs
4. Verify firewall/network settings

---

### Issue: Docusaurus Build Errors

**Symptom**:
```
Error: Cannot find module 'react'
```

**Solution**:
```bash
cd docs
rm -rf node_modules package-lock.json
npm install
```

---

### Issue: Port Already in Use

**Symptom**:
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution**:
```bash
# Find process using port 3000
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or use a different port
npm start -- --port 3001
```

---

## Environment Variables Reference

### Backend `.env` (root directory)

```env
# Qdrant Configuration
QDRANT_URL="https://your-cluster.qdrant.io:6333"
QDRANT_API_KEY="your-qdrant-api-key"

# OpenAI Configuration
OPENAI_API_KEY="your-openai-api-key"

# Cohere Configuration (if used)
COHERE_API_KEY="your-cohere-api-key"

# FastAPI Configuration
API_BASE_URL="http://localhost:8000"  # For frontend to reference
```

### Frontend Environment Variables (Optional)

If using `.env` in `docs/`:

```env
# API Configuration
API_BASE_URL=http://localhost:8000
```

Then in `docusaurus.config.js`:

```javascript
require('dotenv').config();

module.exports = {
  customFields: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
  },
};
```

---

## Useful Commands

### Frontend (Docusaurus)

```bash
cd docs

# Start development server
npm start

# Build for production
npm run build

# Serve production build locally
npm run serve

# Clear cache
npm run clear

# Check for outdated dependencies
npm outdated
```

### Backend (FastAPI)

```bash
cd backend

# Start server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start with specific log level
uvicorn main:app --reload --log-level debug

# Run tests
pytest tests/ -v

# Check code formatting
black . --check

# Format code
black .
```

### Git Workflow

```bash
# Check status
git status

# Create new feature branch
git checkout -b feature/chatbot-component

# Stage changes
git add docs/src/components/RAGChatbot/

# Commit changes
git commit -m "feat: Add ChatWidget component"

# Push to remote
git push origin feature/chatbot-component
```

---

## Deployment Guide

### Production Deployment to GitHub Pages

#### Step 1: Configure Production API Endpoint

Update the API configuration for production:

1. **Update `docs/static/config/api-config.json`**:
   ```json
   {
     "development": {
       "apiBaseUrl": "http://localhost:8000"
     },
     "production": {
       "apiBaseUrl": "https://your-production-api.com"  // Replace with your actual API URL
     }
   }
   ```

2. **Update `docs/docusaurus.config.js`** for production build:
   ```javascript
   // For production builds, the API_BASE_URL can be set via environment variable
   customFields: {
     apiBaseUrl: process.env.API_BASE_URL || process.env.REACT_APP_API_URL || 'https://your-production-api.com',
   },
   ```

#### Step 2: Build for Production

```bash
# Navigate to docs directory
cd docs

# Build the site with production API URL
API_BASE_URL=https://your-production-api.com npm run build

# OR using the script we added
npm run build:production
```

#### Step 3: Deploy to GitHub Pages

1. **Ensure GitHub Pages is enabled** in your repository settings:
   - Go to Repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages`, `/ (root)`
   - Save

2. **Deploy using Docusaurus command**:
   ```bash
   # This will build and deploy to GitHub Pages
   npm run deploy
   ```

   Or, if you want to deploy manually:
   ```bash
   # Build the site
   npm run build

   # The build output is in the `build/` directory
   # You can manually copy this to your GitHub Pages branch
   ```

#### Step 4: Verify Production Deployment

After deployment:

1. **Visit your GitHub Pages site**: `https://your-username.github.io/your-repo-name/`
2. **Test the chatbot functionality**:
   - Open the chatbot widget
   - Submit a query to verify backend connectivity
   - Check that responses and citations work correctly
3. **Check browser console** for any errors
4. **Verify HTTPS** - ensure the site is served over HTTPS

#### Step 5: Backend Configuration for Production

Ensure your production backend is configured to accept requests from your GitHub Pages domain:

1. **Update CORS settings in `backend/src/main.py`**:
   ```python
   origins = [
       "http://localhost:3000",  # Development
       "https://your-username.github.io",  # GitHub Pages (replace with your actual domain)
       "https://your-custom-domain.com",  # If using custom domain
   ]
   ```

2. **Deploy your backend** to a cloud provider (AWS, GCP, Azure, etc.) or container service
3. **Ensure HTTPS** is enabled on your backend API
4. **Monitor API usage** and set up rate limiting if needed

#### Step 6: Environment-Specific Configuration

For different environments, you can use:

1. **Environment variables** during build time:
   ```bash
   # For staging
   API_BASE_URL=https://staging-api.yourdomain.com npm run build

   # For production
   API_BASE_URL=https://api.yourdomain.com npm run build
   ```

2. **Runtime configuration** via `api-config.json` file

#### Troubleshooting Production Deployment

**Issue: Chatbot not connecting to API in production**

- **Check**: Browser console for CORS errors
- **Solution**: Verify CORS settings in backend allow your GitHub Pages domain

**Issue: Mixed content warnings (HTTP/HTTPS)**

- **Check**: All resources loaded over HTTPS in production
- **Solution**: Ensure API endpoints use HTTPS in production config

**Issue: GitHub Pages not serving the site**

- **Check**: Verify `gh-pages` branch exists and contains build files
- **Solution**: Run `npm run deploy` to push build to GitHub Pages

---

## Testing Production Build Locally

Before deploying to production, test the build locally:

```bash
cd docs

# Build for production
npm run build

# Serve the production build locally
npm run serve
```

This will start a local server (usually on http://localhost:3000) with your production build, allowing you to test functionality before deploying.

---

## Next Steps

After completing this quickstart:

1. **Review Design Documents**:
   - Read `data-model.md` for data structures
   - Review `contracts/chatbot-api.openapi.yaml` for API specifications

2. **Implement Components** (per tasks.md, Phase 2):
   - Create chatbot UI components
   - Implement API client logic
   - Add theme integration

3. **Testing**:
   - Write component unit tests
   - Perform manual E2E integration tests
   - Validate 5+ full RAG query flows

4. **Deployment Preparation**:
   - Configure production API endpoint
   - Test GitHub Pages build
   - Verify HTTPS compatibility

---

## Support Resources

- **Docusaurus Docs**: https://docusaurus.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **OpenAPI Spec**: `contracts/chatbot-api.openapi.yaml`

---

**Quickstart Completed**: 2025-12-11
**Status**: ✅ Ready for development
**Estimated Setup Time**: 30-45 minutes (assuming all prerequisites met)
