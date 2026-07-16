import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Send, Loader2 } from "lucide-react";
import { sendChat } from "../services/api";

export default function ChatInterface({ persona, language, onAlert, highContrast }) {
  const { t } = useTranslation();
  const [messages, setMessages] = useState([
    { role: "assistant", content: t("welcome_message") }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;
    
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);
    
    try {
      const history = messages.slice(-10);
      const data = await sendChat({ message: text, persona, language, history });
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
      if (data.alert) onAlert(data.alert);
    } catch (err) {
      setError(t("error_message"));
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  const inputBg = highContrast ? "bg-black border-yellow-300 text-yellow-300 placeholder-yellow-700" : "bg-slate-800 border-slate-600 text-white placeholder-slate-400";
  const bubbleUser = highContrast ? "bg-yellow-300 text-black" : "bg-blue-600 text-white";
  const bubbleAssistant = highContrast ? "bg-yellow-900 text-yellow-100" : "bg-slate-700 text-white";
  
  return (
    <section aria-label={t("chat_section_label")}>
      {/* Message list */}
      <div
        className="h-[55vh] overflow-y-auto space-y-3 py-2"
        role="log"
        aria-live="polite"
        aria-label={t("conversation_log")}
      >
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed
                ${msg.role === "user" ? bubbleUser : bubbleAssistant}`}
              role={msg.role === "assistant" ? "status" : undefined}
            >
              {msg.content}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start" aria-live="assertive" aria-label={t("loading_label")}>
            <div className={`px-4 py-2.5 rounded-2xl ${bubbleAssistant} flex items-center gap-2 text-sm`}>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              {t("thinking")}
            </div>
          </div>
        )}
        
        {error && (
          <div className="text-red-400 text-sm text-center" role="alert">{error}</div>
        )}
        <div ref={bottomRef} />
      </div>
      
      {/* Input area */}
      <div className="flex gap-2 mt-3">
        <label htmlFor="chat-input" className="sr-only">{t("input_label")}</label>
        <textarea
          id="chat-input"
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("input_placeholder")}
          rows={2}
          maxLength={500}
          aria-label={t("input_label")}
          className={`flex-1 rounded-xl border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 ${inputBg}`}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          aria-label={t("send_button")}
          className="self-end bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl p-2.5 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <Send className="w-5 h-5" aria-hidden="true" />
        </button>
      </div>
      <p className="text-xs text-slate-500 mt-1 text-right">{input.length}/500</p>
    </section>
  );
}
