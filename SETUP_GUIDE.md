# StadiumIQ Setup & Deployment Guide

## Quick Start (3 Steps)

### 1. Get Your Gemini API Key
Visit [Google AI Studio](https://aistudio.google.com/) and:
- Sign in with your Google account
- Click "Get API Key" 
- Copy your API key

### 2. Configure Environment
```bash
cd stadiumiq
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY
```

### 3. Launch with Docker
```bash
docker-compose up --build
```

The app will be available at **http://localhost:5173**

---

## Local Development Setup

### Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at http://localhost:8000

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

Frontend will run at http://localhost:5173

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

Expected output:
- ✅ test_chat_returns_200
- ✅ test_chat_empty_message_returns_400
- ✅ test_crowd_status_returns_list
- ✅ test_health_endpoint

### Frontend Tests
```bash
cd frontend
npm test
```

Expected output:
- ✅ ChatInterface renders welcome message
- ✅ ChatInterface renders send button
- ✅ Send button disabled when empty
- ✅ PersonaSelector renders all personas
- ✅ PersonaSelector calls setPersona on click
- ✅ PersonaSelector marks active persona

---

## Architecture Overview

### Backend (FastAPI)
- **main.py**: Application entry, CORS, router registration
- **routers/**: API endpoints for chat, crowd, navigation, transport
- **services/**: Business logic (Gemini integration, crowd simulation, prompt building)
- **models/**: Pydantic schemas for validation
- **data/**: Static JSON data (stadium map, transport info)

### Frontend (React + Vite)
- **App.jsx**: Main app shell with tabs and state
- **components/**: Reusable UI components
- **services/api.js**: Axios client with interceptors
- **i18n.js**: Internationalization setup
- **locales/**: Translation files (EN, ES, FR, AR)

---

## API Endpoints

### POST /api/chat
Send a message to the AI assistant.
```json
{
  "message": "Where is Gate A?",
  "persona": "fan",
  "language": "en",
  "history": [],
  "section": "212"
}
```

### GET /api/crowd/status
Get real-time crowd density for all gates.

### POST /api/navigation
Get step-by-step navigation between two locations.
```json
{
  "from_location": "Main Entrance (Gate A)",
  "to_location": "My Seat (Section 212)",
  "accessibility_needed": false,
  "language": "en"
}
```

### GET /api/transport
Get available transport options to/from stadium.

### GET /health
Health check endpoint.

---

## Environment Variables

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend
```
VITE_API_URL=http://localhost:8000
```

---

## Deployment Checklist

- [ ] Generate Gemini API key
- [ ] Configure .env file
- [ ] Test backend: `pytest backend/tests/ -v`
- [ ] Test frontend: `npm test` in frontend/
- [ ] Build Docker images: `docker-compose build`
- [ ] Run containers: `docker-compose up`
- [ ] Verify health: `curl http://localhost:8000/health`
- [ ] Open UI: http://localhost:5173
- [ ] Test all 4 tabs: Chat, Crowd, Navigate, Transport
- [ ] Test all 4 personas: Fan, Staff, Volunteer, Organizer
- [ ] Test all 4 languages: EN, ES, FR, AR
- [ ] Test accessibility features (high contrast, font size)

---

## Troubleshooting

### Backend won't start
- Check GEMINI_API_KEY is set in .env
- Verify Python 3.11+ is installed
- Check port 8000 is not in use

### Frontend won't connect to backend
- Verify backend is running at http://localhost:8000
- Check VITE_API_URL in .env or docker-compose.yml
- Check CORS settings in backend/main.py

### Gemini API errors
- Verify API key is valid
- Check you haven't exceeded free tier quota
- Review safety filter blocks in logs

---

## Performance Notes

- Chat responses typically take 1-3 seconds
- Crowd data auto-refreshes every 30 seconds
- Navigation queries are cached for 5 minutes
- Frontend bundle size: ~400 KB gzipped
- Backend memory usage: ~100 MB per worker

---

## Next Steps for Production

1. **Replace simulated crowd data** with real sensor/CCTV feeds
2. **Add authentication** for staff/organizer personas
3. **Deploy to cloud** (AWS ECS, Google Cloud Run, or Azure Container Apps)
4. **Set up monitoring** (Prometheus + Grafana or Datadog)
5. **Enable HTTPS** with SSL certificates
6. **Configure CDN** for static assets
7. **Add rate limiting** to prevent abuse
8. **Implement logging** with structured logs (JSON format)
9. **Set up CI/CD** with GitHub Actions or GitLab CI

---

Built with ❤️ for FIFA World Cup 2026
