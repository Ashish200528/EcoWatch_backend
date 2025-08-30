# EcoWatch_backend

Backend API for the EcoWatch mangrove monitoring application.

## Description

EcoWatch is a mangrove monitoring system that analyzes environmental reports using AI. This backend provides API endpoints for processing and analyzing mangrove monitoring data using Google's Gemini AI.

## Features

- Flask-based REST API
- Integration with Google Gemini AI for report analysis
- Image processing capabilities for environmental monitoring
- Production-ready deployment configuration for Render
- Comprehensive error handling and logging

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ashish200528/EcoWatch_backend.git
   cd EcoWatch_backend
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

### Production Deployment (Render)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Set environment variables (GEMINI_API_KEY, FLASK_ENV=production)
6. Deploy!

📖 **[Complete Deployment Guide](docs/deployment.md)**

## API Endpoints

- `GET /`: Welcome message and API status
- `GET /health`: Health check endpoint  
- `POST /upload`: Analyze mangrove monitoring data

### Upload Endpoint

**Parameters:**
- `user_uuid` (form): User identifier
- `description` (form): Report description  
- `category` (form): Report category
- `latitude` (form): Location latitude
- `longitude` (form): Location longitude
- `image` (file): Site image for analysis

**Example:**
```bash
curl -X POST http://localhost:5000/upload \
  -F "user_uuid=123" \
  -F "description=Mangrove site monitoring" \
  -F "category=monitoring" \
  -F "latitude=25.7617" \
  -F "longitude=-80.1918" \
  -F "image=@path/to/image.jpg"
```

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `FLASK_ENV`: Environment mode (development/production)
- `PORT`: Server port (default: 5000)

## Technologies Used

- **Python 3.11+**: Core programming language
- **Flask**: Web framework
- **Google Generative AI**: AI analysis engine  
- **Gunicorn**: WSGI HTTP Server for production
- **Pillow**: Image processing
- **python-dotenv**: Environment variable management

## Project Structure

```
├── app.py                 # Main Flask application
├── gemini_analyzer.py     # AI analysis logic
├── requirements.txt       # Python dependencies  
├── render.yaml           # Render deployment config
├── .env.example          # Environment variables template
├── docs/
│   └── deployment.md     # Deployment documentation
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For deployment issues or questions, refer to the [deployment documentation](docs/deployment.md) or create an issue.
