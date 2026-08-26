'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TrafficMetrics } from '@/types';

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

export function useWebSocket(wsUrl: string) {
  const [metrics, setMetrics] = useState<TrafficMetrics>(INITIAL_METRICS);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!wsUrl || typeof window === 'undefined') return;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data: TrafficMetrics = JSON.parse(event.data);
          setMetrics(data);
        } catch (err) {
          console.error("Failed to parse WebSocket JSON payload", err);
        }
      };

      ws.onerror = () => {
        setError("WebSocket connection encountered an error.");
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential reconnect every 2.5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 2500);
      };
    } catch (err) {
      setError("Unable to establish WebSocket connection.");
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [wsUrl]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return { metrics, isConnected, error };
}
