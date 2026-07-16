# StadiumIQ Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React 18 + Tailwind CSS)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Persona      │  │  Language    │  │Accessibility │        │
│  │ Selector     │  │  Switcher    │  │  Controls    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  TAB NAVIGATION                                         │  │
│  ├─────────────┬────────────┬──────────────┬─────────────┤  │
│  │💬 Chat      │👥 Crowd    │🗺️ Navigate   │🚌 Transport │  │
│  │             │            │              │             │  │
│  │ AI Chat     │ Density    │ Wayfinding   │ Eco Options │  │
│  │ Interface   │ Heatmap    │ w/ Steps     │ + Routes    │  │
│  └─────────────┴────────────┴──────────────┴─────────────┘  │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP REST API
                       │ (Axios with interceptors)
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                     (Python 3.11 + Uvicorn)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  API ROUTERS                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ /chat    │  │ /crowd/  │  │/navigate │  │/transport│      │
│  │          │  │ status   │  │          │  │          │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │               │             │            │
│       └─────────────┴───────────────┴─────────────┘            │
│                     │                                           │
│  SERVICES           ↓                                           │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Gemini Service (gemini_service.py)              │          │
│  │  ┌─────────────────────────────────────────┐    │          │
│  │  │ • Persona-specific system prompts       │    │          │
│  │  │ • Multi-turn conversation history       │    │          │
│  │  │ • Safety filters (BLOCK_MEDIUM_+)       │    │          │
│  │  │ • Temperature: 0.4, Max tokens: 512     │    │          │
│  │  └─────────────────────────────────────────┘    │          │
│  └──────────────────────┬───────────────────────────┘          │
│                         │                                       │
│  ┌──────────────────────┴───────────────────────────┐          │
│  │  Prompt Builder (prompt_builder.py)              │          │
│  │  ┌─────────────────────────────────────────┐    │          │
│  │  │ Persona Context:                        │    │          │
│  │  │ • FAN: Friendly, concise, enthusiastic  │    │          │
│  │  │ • STAFF: Precise, safety-first          │    │          │
│  │  │ • VOLUNTEER: Supportive, step-by-step   │    │          │
│  │  │ • ORGANIZER: Data-driven, priorities    │    │          │
│  │  └─────────────────────────────────────────┘    │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Crowd Service (crowd_service.py)                │          │
│  │  • Sinusoidal time-based density model           │          │
│  │  • 6 gates with wait times                       │          │
│  │  • Accessibility gates prioritized               │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  DATA MODELS (Pydantic)                                         │
│  ┌──────────────────────────────────────────────────┐          │
│  │ • ChatRequest/Response                           │          │
│  │ • NavigationRequest/Response                     │          │
│  │ • CrowdStatus                                    │          │
│  │ • Input validation (max_length, patterns)        │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ google-generativeai SDK
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│               GOOGLE GEMINI 1.5 FLASH API                       │
│                  (Free Tier Friendly)                           │
├─────────────────────────────────────────────────────────────────┤
│  • Natural language understanding                               │
│  • Context-aware generation                                     │
│  • Multi-language support                                       │
│  • Safety filtering                                             │
│  • Fast inference (~1-3s response time)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### 1. Chat Message Flow
```
User types "Where is Gate A?"
    ↓
ChatInterface.jsx
    ↓ sendChat({ message, persona: "fan", language: "en", history: [...] })
    ↓
axios → /api/chat
    ↓
FastAPI chat.py router
    ↓ Validates with Pydantic ChatRequest
    ↓
gemini_service.generate_response()
    ↓ prompt_builder.build_system_prompt(persona, language)
    ↓ Constructs: Fan context + EN language + safety rules
    ↓
Google Gemini API
    ↓ Returns: "Gate A is located at the north entrance..."
    ↓
chat.py generates suggested_actions for persona
    ↓
ChatResponse { reply, persona, suggested_actions, alert }
    ↓
ChatInterface.jsx displays message bubble
```

### 2. Crowd Status Flow
```
Component mounts → useEffect()
    ↓
Every 30s: getCrowdStatus()
    ↓
axios → /api/crowd/status
    ↓
FastAPI crowd.py router
    ↓
crowd_service.get_all_gate_statuses()
    ↓ _simulate_density() for each gate
    ↓ Sinusoidal model: density = f(time, gate_type)
    ↓
Returns: [{ gate, density, wait_minutes, recommendation }, ...]
    ↓
CrowdDashboard.jsx renders color-coded cards
    ↓ Green (low) | Yellow (medium) | Orange (high) | Red (critical)
```

### 3. Navigation Flow
```
User selects From/To + Accessibility checkbox
    ↓
NavigationPanel.jsx → handleNavigate()
    ↓
getNavigation({ from_location, to_location, accessibility_needed, language })
    ↓
axios → /api/navigation
    ↓
FastAPI navigation.py router
    ↓ Validates with Pydantic NavigationRequest
    ↓
Constructs prompt: "Give step-by-step directions from X to Y..."
    ↓
gemini_service.generate_response()
    ↓
Google Gemini API
    ↓ Returns numbered list + estimated time
    ↓
navigation.py parses response
    ↓ Extracts steps[], estimated_minutes, accessibility_note
    ↓
NavigationResponse
    ↓
NavigationPanel.jsx renders ordered list with badges
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FRONTEND VALIDATION                                         │
│     • Input max length: 500 chars                               │
│     • Client-side trimming                                      │
│     • Axios interceptor sanitization                            │
│                                                                 │
│  2. CORS MIDDLEWARE                                             │
│     • Allowed origins from env var                              │
│     • Methods: GET, POST only                                   │
│     • Headers: Content-Type, Authorization                      │
│                                                                 │
│  3. PYDANTIC VALIDATION                                         │
│     • Strict type checking                                      │
│     • Max length enforcement                                    │
│     • Pattern matching (e.g., role: user|assistant)             │
│                                                                 │
│  4. GEMINI SAFETY FILTERS                                       │
│     • HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_MEDIUM_AND_ABOVE   │
│     • HARM_CATEGORY_HARASSMENT: BLOCK_MEDIUM_AND_ABOVE          │
│     • HARM_CATEGORY_HATE_SPEECH: BLOCK_MEDIUM_AND_ABOVE         │
│     • HARM_CATEGORY_SEXUALLY_EXPLICIT: BLOCK_MEDIUM_AND_ABOVE   │
│                                                                 │
│  5. ENVIRONMENT ISOLATION                                       │
│     • API keys in backend .env only                             │
│     • No secrets in frontend bundle                             │
│     • Docker secrets management                                 │
│                                                                 │
│  6. DOCKER SECURITY                                             │
│     • Non-root user (appuser:appgroup)                          │
│     • Minimal base images (alpine)                              │
│     • No unnecessary ports exposed                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Accessibility Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  ACCESSIBILITY FEATURES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SEMANTIC HTML                                                  │
│  <header role="banner">                                         │
│  <nav role="tablist">                                           │
│  <main id="main-content">                                       │
│  <section aria-label="...">                                     │
│                                                                 │
│  ARIA LIVE REGIONS                                              │
│  <div aria-live="polite"> → Chat messages                       │
│  <div aria-live="assertive"> → Critical alerts                  │
│  <div role="status"> → Loading states                           │
│  <div role="alert"> → Error messages                            │
│                                                                 │
│  KEYBOARD NAVIGATION                                            │
│  • Tab order follows logical flow                              │
│  • Skip-to-main-content link (hidden until focused)             │
│  • All buttons have :focus-visible rings                        │
│  • Enter key submits chat                                       │
│                                                                 │
│  VISUAL ACCOMMODATIONS                                          │
│  • High contrast mode (yellow-on-black)                         │
│  • Font size cycling (14px → 16px → 18px)                       │
│  • Color is never the only indicator                            │
│  • 4.5:1 contrast ratio minimum                                 │
│                                                                 │
│  SCREEN READER SUPPORT                                          │
│  • aria-label on all interactive elements                       │
│  • Hidden labels for inputs                                     │
│  • Status updates announced                                     │
│  • Progress indicators have aria-valuenow                       │
│                                                                 │
│  RTL SUPPORT                                                    │
│  • dir="rtl" set when Arabic selected                           │
│  • Flexbox direction automatically reverses                     │
│  • Text alignment adjusts                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE STACK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │  FRONTEND CONTAINER                      │                  │
│  │  ┌────────────────────────────────────┐ │                  │
│  │  │  nginx:alpine                      │ │                  │
│  │  │  • Serves React build (/dist)      │ │                  │
│  │  │  • Reverse proxy /api → backend    │ │                  │
│  │  │  • Port 5173:80                    │ │                  │
│  │  └────────────────────────────────────┘ │                  │
│  └──────────────────┬───────────────────────┘                  │
│                     │                                           │
│                     │ depends_on: backend (healthy)             │
│                     │                                           │
│  ┌──────────────────┴───────────────────────┐                  │
│  │  BACKEND CONTAINER                       │                  │
│  │  ┌────────────────────────────────────┐ │                  │
│  │  │  python:3.11-slim                  │ │                  │
│  │  │  • FastAPI + Uvicorn (2 workers)   │ │                  │
│  │  │  • Port 8000:8000                  │ │                  │
│  │  │  • Health check: /health           │ │                  │
│  │  │  • Environment: GEMINI_API_KEY     │ │                  │
│  │  │  • User: appuser (non-root)        │ │                  │
│  │  └────────────────────────────────────┘ │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  VOLUMES: None (stateless application)                          │
│  NETWORKS: Default bridge network                               │
│  RESTART POLICY: unless-stopped                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Choices Rationale

| Choice | Rationale |
|--------|-----------|
| **Gemini 1.5 Flash** | Fast inference, free tier, safety filters, multilingual |
| **FastAPI** | High performance, async support, automatic OpenAPI docs |
| **React 18** | Modern hooks, concurrent rendering, large ecosystem |
| **Vite** | Fast dev server, optimized production builds |
| **Tailwind CSS** | Utility-first, small bundle size, consistent design |
| **Pydantic** | Runtime validation, type safety, clear error messages |
| **Docker** | Reproducible builds, easy deployment, isolation |
| **Pytest** | Async support, fixtures, great mocking |
| **Vitest** | Vite-native, fast, Jest-compatible API |
| **react-i18next** | Battle-tested, lazy loading, pluralization |
| **Axios** | Interceptors, request/response transformation |

---

Built with clean architecture principles for FIFA World Cup 2026
