import { useState, useEffect, useCallback, useRef } from "react";
import { fetchSummary, fetchVenueDetail, fetchAlerts } from "../api/dashboard";
import { useWebSocket } from "./useWebSocket";

export function useDashboard() {
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState("connecting");

  const [selectedVenueId, setSelectedVenueId] = useState(null);
  const [venueDetail, setVenueDetail] = useState(null);
  const [venueDetailLoading, setVenueDetailLoading] = useState(false);
  const debounceRef = useRef(null);

  const loadSummary = useCallback(async () => {
    try {
      const data = await fetchSummary();
      setSummary(data);
    } catch (e) {
      console.error("Failed to load summary", e);
    }
  }, []);

  const loadAlerts = useCallback(async () => {
    try {
      const data = await fetchAlerts();
      setAlerts(data);
    } catch (e) {
      console.error("Failed to load alerts", e);
    }
  }, []);

  const loadVenueDetail = useCallback(async (venueId) => {
    setVenueDetailLoading(true);
    try {
      const data = await fetchVenueDetail(venueId);
      setVenueDetail(data);
    } catch (e) {
      console.error("Failed to load venue detail", e);
    } finally {
      setVenueDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSummary();
    loadAlerts();
  }, [loadSummary, loadAlerts]);

  const debouncedSummaryRefresh = useCallback(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(loadSummary, 3000);
  }, [loadSummary]);

  const selectedVenueIdRef = useRef(selectedVenueId);
  useEffect(() => {
    selectedVenueIdRef.current = selectedVenueId;
  }, [selectedVenueId]);

  const handleWsMessage = useCallback(
    (msg) => {
      if (msg.type === "venue_metrics_updated") {
        debouncedSummaryRefresh();
        if (selectedVenueIdRef.current === msg.venue_id) {
          loadVenueDetail(msg.venue_id);
        }
      } else if (msg.type === "alert_triggered") {
        setAlerts((prev) => {
          const exists = prev.some((a) => a.id === msg.alert.id);
          return exists ? prev : [msg.alert, ...prev];
        });
      } else if (msg.type === "alert_resolved") {
        setAlerts((prev) => prev.filter((a) => a.id !== msg.alert_id));
      }
      setWsStatus("connected");
    },
    [debouncedSummaryRefresh, loadVenueDetail],
  );

  const wsRef = useWebSocket(handleWsMessage);

  useEffect(() => {
    const ws = wsRef.current;
    if (!ws) {
      return;
    }
    const onOpen = () => setWsStatus("connected");
    const onClose = () => setWsStatus("reconnecting");
    ws.addEventListener("open", onOpen);
    ws.addEventListener("close", onClose);

    // clear everything
    return () => {
      ws.removeEventListener("open", onOpen);
      ws.removeEventListener("close", onClose);
    };
  });

  const openVenue = useCallback(
    (venueId) => {
      setSelectedVenueId(venueId);
      loadVenueDetail(venueId);
    },
    [loadVenueDetail],
  );

  const closeVenue = useCallback(() => {
    setSelectedVenueId(null);
    setVenueDetail(null);
  }, []);

  return {
    summary,
    alerts,
    wsStatus,
    selectedVenueId,
    venueDetail,
    venueDetailLoading,
    openVenue,
    closeVenue,
  };
}
