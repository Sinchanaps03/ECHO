# ECHOSKETCH - Render.com Deployment Guide

## Quick Deploy to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up/login with your GitHub account

### Step 2: Connect Repository
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub account
4. Select the `ECHO` repository

### Step 3: Configure Service
```
Name: echosketch
Environment: Python 3
Build Command: pip install -r requirements-render.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

### Step 4: Set Environment Variables
Add these in Render dashboard:
```
GEMINI_API_KEY=AIzaSyBKfl_X43XkeoKnZ8B6DEZDwuQ0H4DpBeI
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your app will be live at `https://your-app-name.onrender.com`

## Troubleshooting

### If build fails with PyTorch errors:
- Use the minimal `requirements-render.txt`
- Remove transformers and torch dependencies if not needed

### If memory issues occur:
- Upgrade to higher tier plan
- Or optimize dependencies further

### Environment Variables:
- GEMINI_API_KEY: Required for AI concept detection
- OPENAI_API_KEY: Required for image generation
- MONGODB_URI: Optional, for data persistence

## Performance Tips
- Use Render's paid tier for better performance
- Enable auto-scaling for traffic spikes
- Set up custom domain if needed