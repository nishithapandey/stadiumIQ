import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 30000,
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
    console.error("API error:", error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export const sendChat = (payload) => API.post("/api/chat", payload);
export const getCrowdStatus = () => API.get("/api/crowd/status");
export const getNavigation = (payload) => API.post("/api/navigation", payload);
export const getTransport = () => API.get("/api/transport");
