/**
 * ChatInterface — AI chat component using useChat custom hook.
 *
 * Features:
 * - Separated logic via useChat hook
 * - Auto-scroll to latest message
 * - Character count indicator
 * - Loading spinner with accessible labels
 * - Error display with alert role
 */
import { useTranslation } from "react-i18next";
import { Send, Loader2 } from "lucide-react";
import useChat from "../hooks/useChat";

export default function ChatInterface({ persona, language, onAlert, highContrast }) {
  const { t } = useTranslation();
  const {
    messages,
    input,
    setInput,
    loading,
    error,
    bottomRef,
    inputRef,
    handleSend,
    handleKeyDown,
  } = useChat({
    persona,
    language,
    onAlert,
    welcomeMessage: t("welcome_message"),
  });

  const inputBg = highContrast
    ? "bg-black border-yellow-300 text-yellow-300 placeholder-yellow-700"
    : "bg-slate-800 border-slate-600 text-white placeholder-slate-400";
  const bubbleUser = highContrast ? "bg-yellow-300 text-black" : "bg-blue-600 text-white";
  const bubbleAssistant = highContrast ? "bg-yellow-900 text-yellow-100" : "bg-slate-700 text-white";

  return (
    <section aria-label={t("chat_section_label")}>
      {/* Message list */}
      <div
        className="h-[55vh] overflow-y-auto space-y-3 py-2 scroll-smooth"
        role="log"
        aria-live="polite"
        aria-label={t("conversation_log")}
      >
        {messages.map((msg, i) => (
          <div
            key={`${msg.role}-${i}`}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
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
          <div className="text-red-400 text-sm text-center" role="alert">
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="flex gap-2 mt-3">
        <label htmlFor="chat-input" className="sr-only">
          {t("input_label")}
        </label>
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
      <p className={`text-xs mt-1 text-right ${highContrast ? "text-yellow-700" : "text-slate-500"}`}>
        {input.length}/500
      </p>
    </section>
  );
}
