import { createSlice } from "@reduxjs/toolkit";

const authSlice = createSlice({
  name: "auth",
  initialState: {
    authenticated: !!localStorage.getItem("refresh_token"),
  },
  reducers: {
    loginSuccess: (state, action) => {
      state.authenticated = true;
      window.__accessToken = action.payload.access;
      localStorage.setItem("refresh_token", action.payload.refresh);
    },
    logout: (state) => {
      state.authenticated = false;
      window.__accessToken = null;
      localStorage.removeItem("refresh_token");
    },
  },
});

export const { loginSuccess, logout } = authSlice.actions;
export default authSlice.reducer;
