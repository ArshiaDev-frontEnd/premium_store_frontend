import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `JWT ${token}`;
    }
  }
  return config;
});

// Response interceptor to handle errors (like 401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Here we can handle token refresh logic later
    return Promise.reject(error);
  }
);
