import client from "./client";

export const fetchSummary = () =>
  client.get("/dashboard/summary/").then((r) => r.data);

export const fetchVenueDetail = (venueId) =>
  client.get(`/venues/${venueId}/detail/`).then((r) => r.data);

export const fetchAlerts = () => client.get("/alerts/").then((r) => r.data);

export const login = (username, password) =>
  client.post("/auth/token/", { username, password }).then((r) => r.data);
