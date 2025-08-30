# EcoWatch_backend

Backend API for the EcoWatch mangrove monitoring application.

## Description

EcoWatch is a mangrove monitoring system that analyzes environmental reports using AI. This backend provides API endpoints for processing and analyzing mangrove monitoring data using Google's Gemini AI.

## Features

- Flask-based REST API
- Integration with Google Gemini AI for report analysis
- Firebase integration for data storage
- Image processing capabilities for environmental monitoring

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in a `.env` file:
   - `GEMINI_API_KEY`: Your Google Gemini API key
4. Configure Firebase credentials
5. Run the application: `python app.py`

## API Endpoints

- `GET /`: Welcome message and API status
- Additional endpoints for report analysis and data processing

## Technologies Used

- Python
- Flask
- Google Gemini AI
- Firebase
- Environment variable management with python-dotenv
