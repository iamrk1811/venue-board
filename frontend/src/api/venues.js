import client from "./client";

export const fetchVenues = () => client.get("/venues/").then((r) => r.data);
