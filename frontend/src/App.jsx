/**
 * App.jsx — Main application shell with tab navigation.
 *
 * Features:
 * - React.lazy code-splitting for tab panels
 * - Keyboard arrow-key navigation between tabs (WCAG)
 * - Proper aria-labelledby connections
 * - Live region for tab panel changes
 * - High contrast and font size accessibility controls
 */
import { useState, Suspense, lazy, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
import PersonaSelector from "./components/PersonaSelector";
import LanguageSwitcher from "./components/LanguageSwitcher";
import AccessibilityBar from "./components/AccessibilityBar";
import AlertBanner from "./components/AlertBanner";

// Code-split tab panels for optimal bundle size
const ChatInterface = lazy(() => import("./components/ChatInterface"));
const CrowdDashboard = lazy(() => import("./components/CrowdDashboard"));
const NavigationPanel = lazy(() => import("./components/NavigationPanel"));
const TransportPanel = lazy(() => import("./components/TransportPanel"));

const TABS = [
  { id: "chat", labelKey: "tab_assistant", emoji: "💬" },
  { id: "crowd", labelKey: "tab_crowd", emoji: "👥" },
  { id: "navigation", labelKey: "tab_navigate", emoji: "🗺️" },
  { id: "transport", labelKey: "tab_transport", emoji: "🚌" },
];

const FONT_SIZE_CLASSES = { small: "text-sm", base: "text-base", large: "text-lg" };

/** Loading fallback for lazy-loaded components */
function TabFallback() {
  return (
    <div className="flex items-center justify-center py-12" role="status">
      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" aria-hidden="true" />
      <span className="ml-3 text-slate-400 text-sm">Loading…</span>
    </div>
  );
}

export default function App() {
  const { t } = useTranslation();
  const [persona, setPersona] = useState("fan");
  const [language, setLanguage] = useState("en");
  const [activeTab, setActiveTab] = useState("chat");
  const [alert, setAlert] = useState(null);
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState("base");
  const tabRefs = useRef({});

  const fontSizeClass = FONT_SIZE_CLASSES[fontSize];

  /** Handle keyboard arrow-key navigation between tabs (WCAG 2.1) */
  const handleTabKeyDown = useCallback(
    (e) => {
      const currentIndex = TABS.findIndex((tab) => tab.id === activeTab);
      let newIndex = currentIndex;

      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        newIndex = (currentIndex + 1) % TABS.length;
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        newIndex = (currentIndex - 1 + TABS.length) % TABS.length;
      } else if (e.key === "Home") {
        e.preventDefault();
        newIndex = 0;
      } else if (e.key === "End") {
        e.preventDefault();
        newIndex = TABS.length - 1;
      } else {
        return;
      }

      const newTab = TABS[newIndex].id;
      setActiveTab(newTab);
      tabRefs.current[newTab]?.focus();
    },
    [activeTab]
  );

  return (
    <div
      className={`min-h-screen ${highContrast ? "bg-black text-yellow-300" : "bg-slate-950 text-white"} ${fontSizeClass}`}
    >
      {/* Skip to main content — accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-white focus:text-black focus:p-2 focus:rounded"
      >
        Skip to main content
      </a>

      {/* Header */}
      <header
        className={`${highContrast ? "bg-yellow-300 text-black" : "bg-slate-900 border-b border-slate-700"} px-4 py-3 flex items-center justify-between`}
        role="banner"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl" aria-hidden="true">🏟️</span>
          <div>
            <h1 className="font-bold text-lg leading-tight">StadiumIQ</h1>
            <p className={`text-xs ${highContrast ? "text-black" : "text-slate-400"}`}>
              FIFA World Cup 2026 Assistant
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <LanguageSwitcher language={language} setLanguage={setLanguage} />
          <AccessibilityBar
            highContrast={highContrast}
            setHighContrast={setHighContrast}
            fontSize={fontSize}
            setFontSize={setFontSize}
          />
        </div>
      </header>

      {alert && <AlertBanner message={alert} onClose={() => setAlert(null)} />}

      {/* Persona Selector */}
      <div className="px-4 py-3 border-b border-slate-800">
        <PersonaSelector persona={persona} setPersona={setPersona} highContrast={highContrast} />
      </div>

      {/* Tab Navigation with keyboard support */}
      <nav
        className="flex border-b border-slate-800 px-4"
        role="tablist"
        aria-label={t("main_navigation")}
        onKeyDown={handleTabKeyDown}
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            ref={(el) => { tabRefs.current[tab.id] = el; }}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-3 text-sm font-medium border-b-2 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-950
              ${activeTab === tab.id
                ? highContrast
                  ? "border-yellow-300 text-yellow-300"
                  : "border-blue-500 text-blue-400"
                : highContrast
                  ? "border-transparent text-yellow-100 hover:text-yellow-300"
                  : "border-transparent text-slate-400 hover:text-white"
              }`}
          >
            <span aria-hidden="true">{tab.emoji}</span> {t(tab.labelKey)}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main id="main-content" className="container mx-auto px-4 py-4 max-w-3xl">
        <Suspense fallback={<TabFallback />}>
          <div
            role="tabpanel"
            id="panel-chat"
            aria-labelledby="tab-chat"
            hidden={activeTab !== "chat"}
          >
            {activeTab === "chat" && (
              <ChatInterface persona={persona} language={language} onAlert={setAlert} highContrast={highContrast} />
            )}
          </div>
          <div
            role="tabpanel"
            id="panel-crowd"
            aria-labelledby="tab-crowd"
            hidden={activeTab !== "crowd"}
          >
            {activeTab === "crowd" && <CrowdDashboard highContrast={highContrast} />}
          </div>
          <div
            role="tabpanel"
            id="panel-navigation"
            aria-labelledby="tab-navigation"
            hidden={activeTab !== "navigation"}
          >
            {activeTab === "navigation" && <NavigationPanel language={language} highContrast={highContrast} />}
          </div>
          <div
            role="tabpanel"
            id="panel-transport"
            aria-labelledby="tab-transport"
            hidden={activeTab !== "transport"}
          >
            {activeTab === "transport" && <TransportPanel highContrast={highContrast} />}
          </div>
        </Suspense>
      </main>

      {/* Footer */}
      <footer className={`text-center py-4 text-xs ${highContrast ? "text-yellow-700" : "text-slate-600"} border-t ${highContrast ? "border-yellow-900" : "border-slate-800"}`}>
        <p>StadiumIQ &copy; 2026 FIFA World Cup — Powered by Google Gemini AI</p>
      </footer>
    </div>
  );
}
