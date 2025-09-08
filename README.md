# Drone Control API (FastAPI)

This is a FastAPI-based backend service for the drone control system, designed to be deployed on Render.

## Features

- RESTful API for sensor data and control commands
- WebSocket support for real-time updates
- CORS enabled for web interface integration
- Structured logging
- Input validation using Pydantic models

## Deployment to Render

1. Push this code to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - Name: `drone-control-api`
   - Region: Choose the closest to you
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click "Create Web Service"

## Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

4. The API will be available at `http://localhost:8000`

## API Documentation

Once running, you can access:
- Interactive API docs: `/docs`
- Alternative API docs: `/redoc`
- OpenAPI schema: `/openapi.json`

## Environment Variables

- `PORT`: The port to run the server on (default: 8000)
- `PYTHON_VERSION`: Python version (default: 3.9.0)
