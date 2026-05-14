import { createSlice } from "@reduxjs/toolkit";

// rehydrate access token into memory on every app boot
window.__accessToken = localStorage.getItem("access_token") || null;

const authSlice = createSlice({
  name: "auth",
  initialState: {
    authenticated: !!localStorage.getItem("refresh_token"),
  },
  reducers: {
    loginSuccess: (state, action) => {
      state.authenticated = true;
      window.__accessToken = action.payload.access;
      localStorage.setItem("access_token", action.payload.access);
      localStorage.setItem("refresh_token", action.payload.refresh);
    },
    logout: (state) => {
      state.authenticated = false;
      window.__accessToken = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },
  },
});

export const { loginSuccess, logout } = authSlice.actions;
export default authSlice.reducer;
