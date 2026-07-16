import { useState } from "react";
import { useTranslation } from "react-i18next";
import PersonaSelector from "./components/PersonaSelector";
import ChatInterface from "./components/ChatInterface";
import CrowdDashboard from "./components/CrowdDashboard";
import NavigationPanel from "./components/NavigationPanel";
import TransportPanel from "./components/TransportPanel";
import AccessibilityBar from "./components/AccessibilityBar";
import LanguageSwitcher from "./components/LanguageSwitcher";
import AlertBanner from "./components/AlertBanner";

export default function App() {
  const { t } = useTranslation();
  const [persona, setPersona] = useState("fan");
  const [language, setLanguage] = useState("en");
  const [activeTab, setActiveTab] = useState("chat");
  const [alert, setAlert] = useState(null);
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState("base");
  
  const fontSizeClass = { small: "text-sm", base: "text-base", large: "text-lg" }[fontSize];
  
  return (
    <div className={`min-h-screen ${highContrast ? "bg-black text-yellow-300" : "bg-slate-950 text-white"} ${fontSizeClass}`}>
      {/* Skip to main content — accessibility */}
      <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-white focus:text-black focus:p-2 focus:rounded">
        Skip to main content
      </a>
      
      {/* Header */}
      <header className={`${highContrast ? "bg-yellow-300 text-black" : "bg-slate-900 border-b border-slate-700"} px-4 py-3 flex items-center justify-between`} role="banner">
        <div className="flex items-center gap-3">
          <span className="text-2xl" aria-hidden="true">🏟️</span>
          <div>
            <h1 className="font-bold text-lg leading-tight">StadiumIQ</h1>
            <p className={`text-xs ${highContrast ? "text-black" : "text-slate-400"}`}>FIFA World Cup 2026 Assistant</p>
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
      
      {/* Tab Navigation */}
      <nav className="flex border-b border-slate-800 px-4" role="tablist" aria-label={t("main_navigation")}>
        {[
          { id: "chat", label: t("tab_assistant"), emoji: "💬" },
          { id: "crowd", label: t("tab_crowd"), emoji: "👥" },
          { id: "navigation", label: t("tab_navigate"), emoji: "🗺️" },
          { id: "transport", label: t("tab_transport"), emoji: "🚌" },
        ].map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-3 text-sm font-medium border-b-2 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-950
              ${activeTab === tab.id
                ? (highContrast ? "border-yellow-300 text-yellow-300" : "border-blue-500 text-blue-400")
                : (highContrast ? "border-transparent text-yellow-100 hover:text-yellow-300" : "border-transparent text-slate-400 hover:text-white")
              }`}
          >
            <span aria-hidden="true">{tab.emoji}</span> {tab.label}
          </button>
        ))}
      </nav>
      
      {/* Main Content */}
      <main id="main-content" className="container mx-auto px-4 py-4 max-w-3xl">
        <div role="tabpanel" id="panel-chat" hidden={activeTab !== "chat"} aria-labelledby="tab-chat">
          {activeTab === "chat" && (
            <ChatInterface persona={persona} language={language} onAlert={setAlert} highContrast={highContrast} />
          )}
        </div>
        <div role="tabpanel" id="panel-crowd" hidden={activeTab !== "crowd"}>
          {activeTab === "crowd" && <CrowdDashboard highContrast={highContrast} />}
        </div>
        <div role="tabpanel" id="panel-navigation" hidden={activeTab !== "navigation"}>
          {activeTab === "navigation" && <NavigationPanel language={language} highContrast={highContrast} />}
        </div>
        <div role="tabpanel" id="panel-transport" hidden={activeTab !== "transport"}>
          {activeTab === "transport" && <TransportPanel highContrast={highContrast} />}
        </div>
      </main>
    </div>
  );
}
