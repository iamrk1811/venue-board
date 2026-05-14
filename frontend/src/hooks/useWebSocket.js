import { useEffect, useRef, useCallback } from "react";

const BASE_DELAY = 1000;
const MAX_DELAY = 30000;

export function useWebSocket(onMessage) {
  const wsRef = useRef(null);
  const delayRef = useRef(BASE_DELAY);
  const onMessageRef = useRef(onMessage);
  const unmountedRef = useRef(false);

  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (unmountedRef.current)
      return;
    const token = window.__accessToken;

    const ws = new WebSocket(`/ws/dashboard/?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      delayRef.current = BASE_DELAY;
    };

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        onMessageRef.current(data);
      } catch {
        console.log("something went wrong")
      }
    };

    ws.onclose = () => {
      if (unmountedRef.current) return;
      const delay = delayRef.current;
      delayRef.current = Math.min(delay * 2, MAX_DELAY);
      setTimeout(connect, delay);
    };

    ws.onerror = () => ws.close();
  }, []);

  useEffect(() => {
    unmountedRef.current = false;
    connect();

    return () => {
      unmountedRef.current = true;
      wsRef.current?.close();
    };
  }, [connect]);

  return wsRef;
}
