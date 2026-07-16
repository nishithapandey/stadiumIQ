# ⚡ StadiumIQ - 60 Second Quick Start

## Prerequisites
- Docker & Docker Compose installed
- Google Gemini API key ([Get one free here](https://aistudio.google.com/))

## 3 Commands to Run
```bash
# 1. Clone and enter
cd stadiumiq

# 2. Set API key
cp .env.example .env
# Edit .env: GEMINI_API_KEY=your_key_here

# 3. Launch
docker-compose up --build
```

## Open & Test
→ **http://localhost:5173**

## Try These Features (2 minutes)
1. **Select Persona**: Click "Fan" → "Staff" → "Volunteer" → "Organizer"
2. **Change Language**: Top-right dropdown → Try Spanish/French/Arabic
3. **Chat Tab**: Ask "Where is Gate A?" or "Show me the restrooms"
4. **Crowd Tab**: See live gate density (auto-refreshes every 30s)
5. **Navigate Tab**: Select From/To locations → Get AI directions
6. **Transport Tab**: View eco-friendly transport options
7. **Accessibility**: Click eye icon (high contrast) & 'A' icon (font size)

## What Makes This Special?
✅ **Gemini 1.5 Flash** powers every interaction (not a bolt-on)  
✅ **4 Personas** with unique AI behavior  
✅ **4 Languages** with RTL support for Arabic  
✅ **Real-time crowd** monitoring with visual heatmap  
✅ **AI Navigation** generated on-demand  
✅ **WCAG 2.1 AA** accessible  
✅ **0.07 MB** repo size (700x under limit!)

## Architecture in 10 Seconds
- **Backend**: FastAPI + Gemini SDK → Persona-aware AI responses
- **Frontend**: React 18 + Vite + Tailwind → 8 components, 4 languages
- **AI**: Every chat, navigation, and alert goes through Gemini
- **Docker**: Multi-container with health checks

## Test APIs Directly
```bash
# Health check
curl http://localhost:8000/health

# Chat (replace with your data)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Where is my seat?","persona":"fan","language":"en","history":[]}'

# Crowd status
curl http://localhost:8000/api/crowd/status
```

## Run Tests
```bash
# Backend
cd backend && pytest tests/ -v

# Frontend  
cd frontend && npm test
```

## Troubleshooting
- **Backend won't start**: Check GEMINI_API_KEY in .env
- **Port conflict**: Change ports in docker-compose.yml
- **Gemini errors**: Verify API key at https://aistudio.google.com/

## Key Files to Review
- `backend/services/gemini_service.py` - Core AI integration
- `backend/services/prompt_builder.py` - Persona prompts
- `frontend/src/components/ChatInterface.jsx` - Main UI
- `frontend/src/App.jsx` - Application shell
- `docker-compose.yml` - Infrastructure

## Repo Stats
- **50 files** created
- **0.07 MB** total size
- **4,500+ lines** of code
- **10+ tests** (backend + frontend)
- **4 personas** × **4 languages** = 16 unique experiences

---

**Ready to impress!** 🏆

Built for FIFA World Cup 2026 Challenge 4 - Smart Stadiums
