/**
 * useChat — Custom hook for managing AI chat state and interactions.
 *
 * Encapsulates all chat logic (messages, loading, errors, sending) into a
 * reusable hook, following React best practices for separation of concerns.
 *
 * @param {Object} options - Hook configuration
 * @param {string} options.persona - Active user persona
 * @param {string} options.language - Active language code
 * @param {Function} options.onAlert - Callback for crowd density alerts
 * @param {string} options.welcomeMessage - Initial welcome message text
 */
import { useState, useRef, useEffect, useCallback } from "react";
import { sendChat } from "../services/api";

const MAX_HISTORY_TURNS = 10;

export default function useChat({ persona, language, onAlert, welcomeMessage }) {
  const [messages, setMessages] = useState([
    { role: "assistant", content: welcomeMessage },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const history = messages.slice(-MAX_HISTORY_TURNS);
      const data = await sendChat({ message: text, persona, language, history });
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
      if (data.alert) onAlert(data.alert);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, messages, persona, language, onAlert]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return {
    messages,
    input,
    setInput,
    loading,
    error,
    bottomRef,
    inputRef,
    handleSend,
    handleKeyDown,
  };
}
