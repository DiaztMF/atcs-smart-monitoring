'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Video, RefreshCw, AlertTriangle } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import VideoPlayer from '@/components/VideoPlayer';
import KPIRow from '@/components/MetricsCard';
import VehicleBreakdown from '@/components/VehicleBreakdown';
import AdaptiveSignalSplit from '@/components/AdaptiveSignalSplit';
import TrafficDirectionCard from '@/components/TrafficDirectionCard';
import TrafficChart from '@/components/TrafficChart';
import LiveFeed from '@/components/LiveFeed';
import CCTVSelectorModal from '@/components/CCTVSelectorModal';
import { ROICoordinates, StreamSourceInfo, DetectionLogEvent, VehicleType } from '@/types';
import { getBackendUrl } from '@/utils/config';

const BACKEND_URL = getBackendUrl();

type DirectionType = 'IN' | 'OUT';

interface VehicleEvent {
  id: string;
  timestamp: string;
  direction: 'inbound' | 'outbound';
  vehicle_type: string;
  smp: number;
}

const LANES = ['Jalur 1', 'Jalur 2', 'Jalur 3', 'Jalur Utama'];

export default function Dashboard() {
  const {
    metrics,
    isConnected,
    error: wsError,
    reconnectCount,
    maxRetries,
    isReconnecting,
    reconnect: handleReconnect,
  } = useWebSocket();

  const [roi, setROI] = useState<ROICoordinates>({
    inbound: [],
    outbound: [],
  });
  const [streamInfo, setStreamInfo] = useState<StreamSourceInfo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [streamKey, setStreamKey] = useState(0);
  const [detectionLogs, setDetectionLogs] = useState<DetectionLogEvent[]>([]);
  const prevEventIdsRef = useRef<Set<string>>(new Set());

  // Keep ref of previous breakdown counts to generate delta log events
  const prevMetricsRef = useRef(metrics);

  const LANE_MAP: Record<string, VehicleType> = {
    motorcycle: 'motorcycle',
    car: 'car',
    bus: 'bus',
    truck: 'truck',
  };

  const addDetectionLogsFromEvents = useCallback((events: VehicleEvent[]) => {
    const next: DetectionLogEvent[] = [];
    for (const evt of events) {
      if (prevEventIdsRef.current.has(evt.id)) continue;
      prevEventIdsRef.current.add(evt.id);
      const mappedType = LANE_MAP[evt.vehicle_type];
      if (!mappedType) continue;
      next.push({
        id: evt.id,
        time: (() => {
          const parts = evt.id.split('_');
          const msStr = parts.length > 2 ? parts[parts.length - 1] : String(Date.now());
          const ms = Number(msStr);
          return Number.isFinite(ms)
            ? new Date(ms).toLocaleTimeString('en-GB')
            : new Date().toLocaleTimeString('en-GB');
        })(),
        type: mappedType,
        direction: evt.direction.toUpperCase() as DirectionType,
        lane: LANES[Math.floor(Math.random() * LANES.length)],
        status: `${Math.floor(Math.random() * 35) + 25} km/h`,
      });
    }
    if (next.length) setDetectionLogs((existing) => [...next, ...existing].slice(0, 50));
  }, []);

  // Sync recent_events from backend when metrics change
  useEffect(() => {
    addDetectionLogsFromEvents(metrics.recent_events);
    prevMetricsRef.current = metrics;
  }, [metrics, addDetectionLogsFromEvents]);

  // Fetch initial ROIs from Backend
  useEffect(() => {
    fetch(`${BACKEND_URL}/api/v1/roi`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => setROI(data))
      .catch((err) => console.error('Failed to load initial ROI:', err));
  }, []);

  // Fetch initial Stream Source & Presets
  const fetchStreamSource = useCallback(() => {
    fetch(`${BACKEND_URL}/api/v1/stream-source`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => setStreamInfo(data))
      .catch((err) => console.error('Failed to load stream source:', err));
  }, []);

  useEffect(() => {
    fetchStreamSource();
  }, [fetchStreamSource]);

  const handleSelectStreamSource = async (url: string, name: string) => {
    const res = await fetch(`${BACKEND_URL}/api/v1/stream-source`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, name }),
    });
    if (!res.ok) throw new Error(`Failed to switch stream: ${res.status}`);
    fetchStreamSource();
    setStreamKey((prev) => prev + 1);
    setDetectionLogs([]);
    prevEventIdsRef.current = new Set();
  };

  const handleSaveROI = async (updatedROI: ROICoordinates) => {
    setROI(updatedROI);
    try {
      await fetch(`${BACKEND_URL}/api/v1/roi`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedROI),
      });
    } catch (err) {
      console.error('Failed to update ROI:', err);
    }
  };

  const handleResetCounters = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/v1/reset-counter`, { method: 'POST' });
      setDetectionLogs([]);
      prevEventIdsRef.current = new Set();
    } catch (err) {
      console.error('Failed to reset counters:', err);
    }
  };

  const cameraName = streamInfo?.active_source?.name || 'CAM-03 / ATCS Surakarta Balai Kota';

  const inboundTotalCount =
    metrics.inbound.breakdown.motorcycle +
    metrics.inbound.breakdown.car +
    metrics.inbound.breakdown.bus +
    metrics.inbound.breakdown.truck;

  const outboundTotalCount =
    metrics.outbound.breakdown.motorcycle +
    metrics.outbound.breakdown.car +
    metrics.outbound.breakdown.bus +
    metrics.outbound.breakdown.truck;

  const totalVehicles = inboundTotalCount + outboundTotalCount;
  const totalSMP = metrics.inbound.total_smp + metrics.outbound.total_smp;
  const greenSplit =
    totalSMP > 0 ? Math.round((metrics.inbound.total_smp / totalSMP) * 100) : 50;

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* Header */}
      <header className="bg-white border-b border-[#e2e8f0] h-14 flex items-center px-6 gap-4 shrink-0 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
        {/* Brand & Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-slate-900 flex items-center justify-center shadow-sm">
            <span className="text-white text-[11px] font-bold tracking-tight">ST</span>
          </div>
          <span className="text-[15px] font-bold text-slate-900 tracking-tight">
            Smart Traffic Monitoring
          </span>
        </div>

        {/* Vertical Divider */}
        <div className="h-5 w-px bg-[#e2e8f0] mx-1 hidden sm:block" />

        {/* Active Camera Location */}
        <span className="text-[13px] text-slate-500 font-mono hidden sm:inline truncate max-w-xs">
          {cameraName}
        </span>

        {/* Right Header Actions */}
        <div className="ml-auto flex items-center gap-3">
          {/* WebSocket Status Pill */}
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-medium border transition-colors ${
              isConnected
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : isReconnecting
                ? 'bg-amber-50 text-amber-700 border-amber-200'
                : 'bg-red-50 text-red-700 border-red-200'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isConnected
                  ? 'bg-emerald-500 animate-pulse'
                  : isReconnecting
                  ? 'bg-amber-500 animate-ping'
                  : 'bg-red-500'
              }`}
            />
            {isConnected
              ? 'WebSocket Terhubung'
              : isReconnecting
              ? `Menghubungkan (${reconnectCount}/${maxRetries})...`
              : 'WebSocket Terputus'}
          </span>

          {/* Manual Reconnect Button */}
          {!isConnected && (
            <button
              onClick={handleReconnect}
              className="px-2.5 py-1 rounded-md bg-amber-600 text-white text-[12px] font-medium hover:bg-amber-700 transition-colors flex items-center gap-1 shadow-sm"
              title="Coba hubungkan kembali ke WebSocket"
            >
              <RefreshCw className={`w-3 h-3 ${isReconnecting ? 'animate-spin' : ''}`} />
              <span>Coba Ulang</span>
            </button>
          )}

          {/* Switch CCTV Button */}
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-3 py-1.5 rounded-md bg-slate-100 text-[13px] font-medium text-slate-700 hover:bg-slate-200 transition-colors border border-[#e2e8f0] flex items-center gap-1.5 shadow-sm"
          >
            <Video className="w-3.5 h-3.5 text-slate-600" />
            <span>Ganti CCTV</span>
          </button>
        </div>
      </header>

      {/* Connection Notification Alert Banner */}
      {(!isConnected || wsError) && (
        <div className="mx-6 mt-3 px-4 py-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center justify-between gap-3 shadow-sm">
          <div className="flex items-center gap-2 truncate">
            {isReconnecting ? (
              <RefreshCw className="w-4 h-4 text-amber-600 animate-spin shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
            )}
            <span className="truncate font-medium">
              {wsError ||
                (isReconnecting
                  ? `Mencoba menghubungkan kembali ke WebSocket (${reconnectCount}/${maxRetries}) dalam 5 detik...`
                  : 'Koneksi ke backend WebSocket terputus. Backend mungkin sedang sleeping / cold start.')}
            </span>
          </div>
          <button
            onClick={handleReconnect}
            className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white text-[11px] font-semibold rounded transition-colors shadow-sm shrink-0"
          >
            Hubungkan Ulang
          </button>
        </div>
      )}

      {/* Top 4 KPI Cards */}
      <div className="px-6 pt-4 shrink-0">
        <KPIRow
          totalVehicles={totalVehicles}
          inboundSMP={metrics.inbound.total_smp}
          outboundSMP={metrics.outbound.total_smp}
          inboundCount={inboundTotalCount}
          outboundCount={outboundTotalCount}
          greenSplit={greenSplit}
        />
      </div>

      {/* Main 12-Column Grid Layout (7 : 5) */}
      <main className="flex-1 px-6 pt-3 pb-6 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0">
        {/* Left Column (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col gap-3 min-h-0">
          {/* Video Player & ROI Toolbar */}
          <VideoPlayer
            key={streamKey}
            streamUrl={`${BACKEND_URL}/api/v1/stream?t=${streamKey}`}
            fps={metrics.fps}
            cameraName={cameraName}
            isConnected={isConnected}
            roi={roi}
            onSaveROI={handleSaveROI}
            onResetCounters={handleResetCounters}
          />

          {/* PKJI Vehicle Breakdown Bento Grid */}
          <VehicleBreakdown
            inbound={metrics.inbound.breakdown}
            outbound={metrics.outbound.breakdown}
          />

          {/* Adaptive Signal Split Widget */}
          <AdaptiveSignalSplit greenSplit={greenSplit} cycleTimeSeconds={90} />
        </div>

        {/* Right Column (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-3 min-h-0">
          {/* Inbound Traffic Summary Card */}
          <TrafficDirectionCard
            direction="inbound"
            metrics={metrics.inbound}
            totalVehicles={inboundTotalCount}
          />

          {/* Outbound Traffic Summary Card */}
          <TrafficDirectionCard
            direction="outbound"
            metrics={metrics.outbound}
            totalVehicles={outboundTotalCount}
          />

          {/* Real-Time Traffic Volume Chart */}
          <TrafficChart
            inboundSMP={metrics.inbound.smp_per_minute}
            outboundSMP={metrics.outbound.smp_per_minute}
          />

          {/* Real-Time Detection Log Table */}
          <LiveFeed events={detectionLogs} />
        </div>
      </main>

      {/* CCTV Preset & Custom URL Modal */}
      <CCTVSelectorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        streamInfo={streamInfo}
        onSelectSource={handleSelectStreamSource}
      />
    </div>
  );
}
