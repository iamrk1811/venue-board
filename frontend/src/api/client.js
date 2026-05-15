import axios from "axios";
import { store } from "../store/store";
import { logout } from "../store/slices/authSlice";

const client = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// access token from memory on every request
client.interceptors.request.use((config) => {
  const token = window.__accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// unwrap standard envelope {success, data} — pass JWT responses through unchanged
client.interceptors.response.use(
  (res) => {
    if (res.data && typeof res.data === "object" && "success" in res.data) {
      res.data = res.data.data;
    }
    return res;
  },
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem("refresh_token");
        if (!refresh) {
          throw new Error("no refresh token");
        }
        const { data } = await axios.post("/api/auth/token/refresh/", {
          refresh,
        });
        window.__accessToken = data.access;
        localStorage.setItem("access_token", data.access);
        // persist rotated refresh token if the backend returns one
        if (data.refresh) {
          localStorage.setItem("refresh_token", data.refresh);
        }
        original.headers.Authorization = `Bearer ${data.access}`;
        return client(original);
      } catch {
        // update redux state so the ui without a page reload
        store.dispatch(logout());
      }
    }
    return Promise.reject(error);
  },
);

export default client;
