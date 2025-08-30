# EcoWatch Backend - Deployment Guide

## Overview

This guide covers how to deploy the EcoWatch Backend API to Render and run it locally for development.

## Prerequisites

- Python 3.11+
- Git
- Google Gemini API key
- Render account (free tier available)
- Firebase credentials (optional, based on your implementation)

## Project Structure

```
ecowatch-backend/
├── app.py                    # Main Flask application
├── gemini_analyzer.py        # AI analysis logic
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment configuration
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
├── .env                    # Environment variables (local only)
└── docs/
    └── deployment.md       # This file
```

## Environment Variables

The following environment variables are required:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Port number (automatically set by Render)
- `FLASK_ENV`: Set to 'production' for production deployment

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Ashish200528/EcoWatch_backend.git
cd EcoWatch_backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
PORT=5000
```

### 5. Run Locally

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Render Deployment

### Method 1: Using Render Dashboard (Recommended)

1. **Fork/Push to GitHub**: Ensure your code is in a GitHub repository

2. **Create New Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Service**:
   - **Name**: `ecowatch-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or paid plan for better performance)

4. **Set Environment Variables**:
   - Go to Environment tab
   - Add `GEMINI_API_KEY` with your API key
   - Add `FLASK_ENV` set to `production`

5. **Deploy**: Click "Create Web Service"

### Method 2: Using render.yaml (Infrastructure as Code)

The `render.yaml` file is included for automated deployment:

1. Push your code to GitHub
2. In Render dashboard, use "Infrastructure as Code"
3. Connect to your repository
4. Render will read the `render.yaml` file automatically

**Note**: You'll still need to set environment variables manually in the dashboard.

### Method 3: Render CLI (Advanced)

```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Deploy using the yaml file
render deploy
```

## API Endpoints

### Health Check
- **GET** `/` - Welcome message
- **GET** `/health` - Health status

### Analysis
- **POST** `/upload` - Analyze mangrove monitoring data

#### Upload Endpoint Parameters:
- `user_uuid` (form): User identifier
- `description` (form): Report description
- `category` (form): Report category
- `latitude` (form): Location latitude
- `longitude` (form): Location longitude
- `image` (file): Site image for analysis

#### Example Request:
```bash
curl -X POST https://your-app.onrender.com/upload \
  -F "user_uuid=123" \
  -F "description=Mangrove restoration site" \
  -F "category=restoration" \
  -F "latitude=25.7617" \
  -F "longitude=-80.1918" \
  -F "image=@/path/to/image.jpg"
```

## Monitoring and Logs

### Render Logs
- Access logs through Render Dashboard
- Real-time log streaming available
- Log retention based on plan

### Health Monitoring
Use the `/health` endpoint for uptime monitoring:
```bash
curl https://your-app.onrender.com/health
```

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check `requirements.txt` for correct package versions
   - Ensure Python version compatibility

2. **Environment Variable Issues**:
   - Verify all required environment variables are set
   - Check for typos in variable names

3. **API Key Problems**:
   - Ensure GEMINI_API_KEY is correctly set
   - Verify API key has proper permissions

4. **Image Upload Issues**:
   - Check file size limits (Render has a 10MB limit)
   - Verify image format support

### Debugging

Enable debug mode locally:
```bash
export FLASK_ENV=development
python app.py
```

Check Render logs for production issues:
- Go to your service in Render Dashboard
- Click on "Logs" tab
- Monitor real-time logs

## Performance Optimization

### For Production

1. **Use Gunicorn with multiple workers**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

2. **Enable caching** for repeated requests

3. **Implement rate limiting** to prevent abuse

4. **Use environment-specific configurations**

### Scaling

- **Free Tier**: Limited to 750 hours/month, sleeps after 15 minutes of inactivity
- **Paid Plans**: Always-on, more resources, custom domains, SSL certificates

## Security Best Practices

1. **Never commit sensitive data**:
   - Use `.env` files locally
   - Set environment variables in Render dashboard

2. **API Key Management**:
   - Rotate API keys regularly
   - Use least-privilege access

3. **Input Validation**:
   - Validate all user inputs
   - Sanitize file uploads

4. **HTTPS**:
   - Render provides HTTPS by default
   - Always use HTTPS in production

## Support and Resources

- [Render Documentation](https://render.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Generative AI Documentation](https://ai.google.dev/docs)

## Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` updated
- [ ] Environment variables configured
- [ ] Render service created
- [ ] GEMINI_API_KEY set in Render
- [ ] Deployment successful
- [ ] Health check endpoint working
- [ ] API endpoints tested
- [ ] Logs monitoring set up
