# 🔑 Environment Variables for Render Deployment

## Required Environment Variables

Add these in your Render dashboard **Environment Variables** section:

| Variable | Value | Description |
|----------|-------|-------------|
| `GEMINI_API_KEY` | `AIzaSyBKfl_X43XkeoKnZ8B6DEZDwuQ0H4DpBeI` | Google Gemini API for concept detection |
| `OPENAI_API_KEY` | `sk-proj-9Yz7t3sbrf4q...` | OpenAI API for image generation |
| `FLASK_ENV` | `production` | Flask environment setting |
| `SECRET_KEY` | `echosketch-super-secret-key-2024-render` | Flask secret key |
| `DEBUG` | `False` | Disable debug mode for production |

## Optional Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `10000` | Server port (auto-set by Render) |
| `HOST` | `0.0.0.0` | Server host |
| `MONGODB_URI` | `mongodb+srv://...` | Database connection (optional) |

## How to Add in Render

1. In your Render service dashboard
2. Go to **Environment** tab
3. Click **Add Environment Variable**
4. Add each key-value pair from the table above
5. **Deploy** your service

## Security Note

- Never commit API keys to version control
- Use Render's environment variables for secure storage
- Rotate API keys regularly for security