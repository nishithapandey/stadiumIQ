# 🏟️ StadiumIQ — FIFA World Cup 2026 Smart Stadium Assistant

> **Challenge 4: Smart Stadiums & Tournament Operations**
> GenAI-powered assistant for fans, staff, volunteers, and organizers.

---

## Chosen Vertical

**Smart Stadium Operations** — an AI assistant that serves four distinct personas across the most critical operational dimensions of a World Cup venue: crowd management, indoor navigation, accessibility, transportation, multilingual support, and real-time decision intelligence.

---

## Approach & Logic

StadiumIQ uses **Google Gemini 1.5 Flash** as its core intelligence engine. GenAI is not a bolt-on feature — it powers every natural language interaction and generates context-aware guidance based on the active persona, language, and stadium section.

### Persona-Driven AI
Each persona (Fan / Staff / Volunteer / Organizer) receives a distinct system prompt:
- **Fan**: Friendly wayfinding and match-day help
- **Staff**: Operational precision with zone identifiers
- **Volunteer**: Step-by-step guidance and escalation paths
- **Organizer**: Data-driven decision support with priority levels

### Core Modules
| Module | Technology | Description |
|--------|-----------|-------------|
| AI Chat | Gemini 1.5 Flash | Contextual assistant with multi-turn conversation |
| Crowd Dashboard | FastAPI + simulated sensors | Gate density heatmap with 30s auto-refresh |
| Navigation | Gemini + structured prompt | AI-generated step-by-step indoor wayfinding |
| Transport | Static data + FastAPI | Shuttle, metro, parking options with eco notes |
| Multilingual | react-i18next | UI in English, Spanish, French, Arabic (RTL support) |
| Accessibility | CSS + ARIA | High-contrast mode, font size cycling, screen reader support |

---

## How the Solution Works

1. **User selects a persona** (Fan / Staff / Volunteer / Organizer)
2. **User selects a language** — UI updates immediately; Gemini also replies in that language
3. **Chat tab**: User messages are sent to `/api/chat` → FastAPI validates → Gemini generates
   a persona-specific, language-aware response → reply and suggested quick actions are returned
4. **Crowd tab**: Polls `/api/crowd/status` every 30 seconds — returns simulated density data
   (designed to plug into real sensor APIs in production)
5. **Navigation tab**: User picks From/To → FastAPI calls Gemini with a structured wayfinding
   prompt → returns ordered steps and ETA, with accessibility mode for wheelchair routes
6. **Transport tab**: Fetches pre-seeded transport data with eco-friendly priority ordering

---

## Assumptions Made

- Crowd data is simulated using a time-of-day sinusoidal model (production would use
  actual CCTV/sensor feeds from the venue management system)
- Stadium map is based on MetLife Stadium (New York/New Jersey) as the primary venue
- Gemini 1.5 Flash is used for its speed and free-tier availability during development
- The `/api/chat` history is capped at 10 turns to manage API token costs
- Transport data is static seed data (production would integrate with real-time transit APIs)

---

## Setup & Run

### Prerequisites
- Docker & Docker Compose
- A free [Google AI Studio](https://aistudio.google.com/) API key (Gemini)

### Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/stadiumiq.git
cd stadiumiq
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY
docker-compose up --build
# Open: http://localhost:5173
```

### Local Dev (without Docker)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test
```

---

## Security Practices

- API key never exposed to frontend (backend-only)
- Input length limited: 500 chars (frontend) + 500 chars (Pydantic validation)
- Gemini safety filters: BLOCK_MEDIUM_AND_ABOVE for all harm categories
- CORS restricted to known origins via ALLOWED_ORIGINS env var
- Docker runs as non-root user
- No sensitive data stored; conversation history is in-memory only

---

## Accessibility

WCAG 2.1 AA compliant:
- ARIA roles and labels throughout
- "Skip to main content" link for keyboard users
- High-contrast mode (yellow-on-black)
- Font size cycling (small / base / large)
- RTL layout support for Arabic
- Screen reader live regions on chat and crowd updates
- All interactive elements have visible focus rings
- Semantic HTML: `<nav>`, `<main>`, `<section>`, `<fieldset>`, `<legend>`

---

## Sustainability Features

- Transport panel prioritizes eco-friendly options (public transit, EV charging)
- AI responses proactively suggest sustainable travel choices
- Gemini Flash model chosen for lower energy consumption vs. larger models

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| AI | Google Gemini 1.5 Flash |
| i18n | react-i18next (EN/ES/FR/AR) |
| Testing | Pytest (backend), Vitest (frontend) |
| Infra | Docker, Docker Compose |

---

## Features Checklist

✅ **GenAI Core**
- Gemini 1.5 Flash for all chat responses
- Persona-specific system prompts
- Language-aware responses (EN/ES/FR/AR)
- AI-generated navigation instructions
- Context injection (stadium section, persona, language)

✅ **Smart & Dynamic**
- Multi-turn conversation with history
- Suggested quick-action buttons per persona
- Alert banner for critical crowd conditions
- Crowd auto-refresh every 30 seconds
- Real-time simulated sensor data

✅ **Code Quality**
- Pydantic validation on all requests/responses
- Service layer separation
- Comprehensive error handling
- Input sanitization
- Docstrings on all functions

✅ **Security**
- API key in backend environment only
- Gemini safety filters enabled
- CORS restrictions
- Non-root Docker user
- No sensitive data persistence

✅ **Testing**
- Pytest async tests for backend
- Vitest tests for frontend components
- Mocked API calls in tests
- Health check endpoint

✅ **Accessibility**
- ARIA roles (log, alert, status, progressbar, tablist)
- Skip-to-main link
- High-contrast mode
- RTL support for Arabic
- Font size cycling
- Semantic HTML throughout

---

## Project Structure

```
stadiumiq/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── routers/
│   │   ├── chat.py
│   │   ├── crowd.py
│   │   ├── navigation.py
│   │   └── transport.py
│   ├── services/
│   │   ├── gemini_service.py
│   │   ├── crowd_service.py
│   │   └── prompt_builder.py
│   ├── models/
│   │   └── schemas.py
│   ├── data/
│   │   ├── stadium_map.json
│   │   └── transport_data.json
│   └── tests/
│       └── test_chat.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── i18n.js
│   │   ├── components/
│   │   ├── locales/
│   │   ├── services/
│   │   └── tests/
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## License

MIT License - Built for FIFA World Cup 2026 Hackathon
