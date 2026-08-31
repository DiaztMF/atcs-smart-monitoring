'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TrafficMetrics } from '@/types';
import { getWebSocketUrl } from '@/utils/config';

const INITIAL_METRICS: TrafficMetrics = {
  timestamp: Date.now() / 1000,
  fps: 0,
  inbound: {
    total_smp: 0,
    smp_per_minute: 0,
    density_level: 'LANCAR',
    breakdown: { motorcycle: 0, car: 0, bus: 0, truck: 0 },
  },
  outbound: {
    total_smp: 0,
    smp_per_minute: 0,
    density_level: 'LANCAR',
    breakdown: { motorcycle: 0, car: 0, bus: 0, truck: 0 },
  },
  recent_events: [],
};

const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_INTERVAL_MS = 5000;

export interface UseWebSocketReturn {
  metrics: TrafficMetrics;
  isConnected: boolean;
  error: string | null;
  reconnectCount: number;
  maxRetries: number;
  isReconnecting: boolean;
  reconnect: () => void;
}

export function useWebSocket(rawWsUrl?: string): UseWebSocketReturn {
  const [metrics, setMetrics] = useState<TrafficMetrics>(INITIAL_METRICS);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [reconnectCount, setReconnectCount] = useState<number>(0);
  const [isReconnecting, setIsReconnecting] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef<number>(0);
  const isComponentUnmountedRef = useRef<boolean>(false);

  const connect = useCallback(() => {
    if (typeof window === 'undefined') return;

    // Resolve and force WSS protocol for production
    const activeUrl = getWebSocketUrl(rawWsUrl);
    if (!activeUrl) return;

    // Clean up existing socket before reconnecting
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }

    try {
      console.log(
        `[WebSocket] Attempting connection to: ${activeUrl} (Attempt ${
          reconnectCountRef.current + 1
        }/${MAX_RECONNECT_ATTEMPTS})`
      );

      const ws = new WebSocket(activeUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isComponentUnmountedRef.current) return;
        console.log(`[WebSocket] Connected successfully to ${activeUrl}`);
        setIsConnected(true);
        setError(null);
        setReconnectCount(0);
        reconnectCountRef.current = 0;
        setIsReconnecting(false);
      };

      ws.onmessage = (event) => {
        if (isComponentUnmountedRef.current) return;
        try {
          const data: TrafficMetrics = JSON.parse(event.data);
          setMetrics(data);
        } catch (err) {
          console.error('[WebSocket] Failed to parse JSON payload:', err);
        }
      };

      ws.onerror = (evt) => {
        if (isComponentUnmountedRef.current) return;
        console.warn('[WebSocket] Connection error event encountered:', evt);
      };

      ws.onclose = (event) => {
        if (isComponentUnmountedRef.current) return;
        console.log(
          `[WebSocket] Socket closed. Code: ${event.code}, Clean: ${event.wasClean}`
        );
        setIsConnected(false);

        if (reconnectCountRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectCountRef.current += 1;
          const currentAttempt = reconnectCountRef.current;
          setReconnectCount(currentAttempt);
          setIsReconnecting(true);
          setError(
            `Koneksi terputus. Mencoba menghubungkan kembali (${currentAttempt}/${MAX_RECONNECT_ATTEMPTS}) dalam 5 detik...`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            if (!isComponentUnmountedRef.current) {
              connect();
            }
          }, RECONNECT_INTERVAL_MS);
        } else {
          setIsReconnecting(false);
          setError(
            `Koneksi WebSocket gagal setelah ${MAX_RECONNECT_ATTEMPTS} kali percobaan. Backend Render mungkin sedang cold start (bangun dari tidur) atau offline.`
          );
        }
      };
    } catch (err) {
      if (isComponentUnmountedRef.current) return;
      console.error('[WebSocket] Instantiation error:', err);
      setIsConnected(false);

      if (reconnectCountRef.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectCountRef.current += 1;
        const currentAttempt = reconnectCountRef.current;
        setReconnectCount(currentAttempt);
        setIsReconnecting(true);
        setError(
          `Gagal membuat WebSocket. Mencoba lagi (${currentAttempt}/${MAX_RECONNECT_ATTEMPTS}) dalam 5 detik...`
        );

        reconnectTimeoutRef.current = setTimeout(() => {
          if (!isComponentUnmountedRef.current) {
            connect();
          }
        }, RECONNECT_INTERVAL_MS);
      } else {
        setIsReconnecting(false);
        setError(
          `Gagal menghubungkan WebSocket setelah ${MAX_RECONNECT_ATTEMPTS} kali percobaan.`
        );
      }
    }
  }, [rawWsUrl]);

  const reconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    reconnectCountRef.current = 0;
    setReconnectCount(0);
    setIsReconnecting(false);
    setError(null);
    connect();
  }, [connect]);

  useEffect(() => {
    isComponentUnmountedRef.current = false;
    connect();

    return () => {
      isComponentUnmountedRef.current = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.onopen = null;
        wsRef.current.onmessage = null;
        wsRef.current.onerror = null;
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return {
    metrics,
    isConnected,
    error,
    reconnectCount,
    maxRetries: MAX_RECONNECT_ATTEMPTS,
    isReconnecting,
    reconnect,
  };
}
