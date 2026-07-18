/**
 * API client for StadiumIQ backend.
 *
 * Features:
 * - Automatic retry with exponential backoff (3 attempts)
 * - Request sanitization (message length capping)
 * - Unified error handling with structured logging
 * - Configurable base URL via environment variable
 */
import axios from "axios";

/** Maximum retry attempts for failed requests */
const MAX_RETRIES = 3;
const RETRY_BASE_DELAY_MS = 1000;

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — sanitize input
API.interceptors.request.use((config) => {
  if (config.data?.message) {
    config.data.message = config.data.message.slice(0, 500);
  }
  return config;
});

// Response interceptor — unified error handling
API.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status;
    const message = error.response?.data?.detail || error.message;
    console.error(`[StadiumIQ API] ${error.config?.method?.toUpperCase()} ${error.config?.url} → ${status}: ${message}`);
    return Promise.reject(error);
  }
);

/**
 * Retry a request with exponential backoff.
 * Only retries on 5xx server errors or network failures.
 */
async function withRetry(requestFn, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      const status = error.response?.status;
      const isRetryable = !status || status >= 500;

      if (!isRetryable || attempt === retries - 1) {
        throw error;
      }

      const delay = RETRY_BASE_DELAY_MS * 2 ** attempt;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
}

export const sendChat = (payload) =>
  withRetry(() => API.post("/api/chat", payload));

export const getCrowdStatus = () =>
  withRetry(() => API.get("/api/crowd/status"));

export const getNavigation = (payload) =>
  withRetry(() => API.post("/api/navigation", payload));

export const getTransport = () =>
  withRetry(() => API.get("/api/transport"));
