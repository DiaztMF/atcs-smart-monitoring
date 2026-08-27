'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Video } from 'lucide-react';
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

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/metrics';

const LANES = ['Jalur 1', 'Jalur 2', 'Jalur 3', 'Jalur Utama'];

export default function Dashboard() {
  const { metrics, isConnected } = useWebSocket(WS_URL);
  const [roi, setROI] = useState<ROICoordinates>({
    inbound: [],
    outbound: [],
  });
  const [streamInfo, setStreamInfo] = useState<StreamSourceInfo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [streamKey, setStreamKey] = useState(0);
  const [detectionLogs, setDetectionLogs] = useState<DetectionLogEvent[]>([]);

  // Keep ref of previous breakdown counts to generate delta log events
  const prevMetricsRef = useRef(metrics);

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

  // Generate real-time detection events when breakdown counters increment
  useEffect(() => {
    const prev = prevMetricsRef.current;
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-GB');
    const newEvents: DetectionLogEvent[] = [];

    const types: VehicleType[] = ['motorcycle', 'car', 'bus', 'truck'];

    // Check Inbound deltas
    types.forEach((type) => {
      const diff = metrics.inbound.breakdown[type] - prev.inbound.breakdown[type];
      if (diff > 0) {
        for (let i = 0; i < Math.min(diff, 5); i++) {
          newEvents.push({
            id: `${Date.now()}-in-${type}-${i}`,
            time: timeStr,
            type,
            direction: 'IN',
            lane: LANES[Math.floor(Math.random() * LANES.length)],
            status: `${Math.floor(Math.random() * 35) + 25} km/h`,
          });
        }
      }
    });

    // Check Outbound deltas
    types.forEach((type) => {
      const diff = metrics.outbound.breakdown[type] - prev.outbound.breakdown[type];
      if (diff > 0) {
        for (let i = 0; i < Math.min(diff, 5); i++) {
          newEvents.push({
            id: `${Date.now()}-out-${type}-${i}`,
            time: timeStr,
            type,
            direction: 'OUT',
            lane: LANES[Math.floor(Math.random() * LANES.length)],
            status: `${Math.floor(Math.random() * 35) + 25} km/h`,
          });
        }
      }
    });

    if (newEvents.length > 0) {
      setDetectionLogs((existing) => [...newEvents, ...existing].slice(0, 50));
    }

    prevMetricsRef.current = metrics;
  }, [metrics]);

  const handleSelectStreamSource = async (url: string, name: string) => {
    const res = await fetch(`${BACKEND_URL}/api/v1/stream-source`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, name }),
    });
    if (!res.ok) throw new Error(`Failed to switch stream: ${res.status}`);
    fetchStreamSource();
    setStreamKey((prev) => prev + 1);
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
  const greenSplit = totalSMP > 0
    ? Math.round((metrics.inbound.total_smp / totalSMP) * 100)
    : 50;

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
                : 'bg-red-50 text-red-700 border-red-200'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'
              }`}
            />
            {isConnected ? 'WebSocket Terhubung' : 'WebSocket Terputus'}
          </span>

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
          <AdaptiveSignalSplit
            greenSplit={greenSplit}
            cycleTimeSeconds={90}
          />
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
