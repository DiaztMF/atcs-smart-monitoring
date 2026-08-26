'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Cpu, Wifi, WifiOff, Video } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import VideoPlayer from '@/components/VideoPlayer';
import MetricsCard from '@/components/MetricsCard';
import VehicleBreakdown from '@/components/VehicleBreakdown';
import TrafficChart from '@/components/TrafficChart';
import LiveFeed from '@/components/LiveFeed';
import CCTVSelectorModal from '@/components/CCTVSelectorModal';
import { ROICoordinates, StreamSourceInfo } from '@/types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/metrics';

export default function Dashboard() {
  const { metrics, isConnected } = useWebSocket(WS_URL);
  const [roi, setROI] = useState<ROICoordinates>({
    inbound: [],
    outbound: [],
  });
  const [streamInfo, setStreamInfo] = useState<StreamSourceInfo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [streamKey, setStreamKey] = useState(0);

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
    setStreamKey((prev) => prev + 1); // Refresh image stream
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
    } catch (err) {
      console.error('Failed to reset counters:', err);
    }
  };

  const cameraName = streamInfo?.active_source?.name || 'ATCS Surakarta Balai Kota';

  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">
      {/* Header Bar */}
      <header className="glass-panel px-6 py-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-100 tracking-tight flex items-center gap-2">
              Smart Traffic Monitoring (SMP / PCU)
            </h1>
            <p className="text-xs text-slate-400">
              Sistem Kontrol & Pengukur Beban Jalan Adaptif Berbasis Computer Vision (YOLOv11 + ByteTrack)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-semibold transition-all shadow-md"
          >
            <Video className="w-4 h-4" />
            <span>Pilih / Ganti CCTV</span>
          </button>

          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            {isConnected ? (
              <>
                <Wifi className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400 font-medium">WebSocket Terhubung</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4 text-rose-400" />
                <span className="text-rose-400 font-medium">WebSocket Terputus</span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Grid: Left Column (Video & Canvas), Right Column (Analytics) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Live Stream Player & Interactive Canvas */}
        <div className="lg:col-span-7 space-y-6">
          <VideoPlayer
            key={streamKey}
            streamUrl={`${BACKEND_URL}/api/v1/stream`}
            fps={metrics.fps}
            cameraName={cameraName}
            isConnected={isConnected}
            roi={roi}
            onSaveROI={handleSaveROI}
            onResetCounters={handleResetCounters}
            onOpenStreamModal={() => setIsModalOpen(true)}
          />

          <VehicleBreakdown
            inbound={metrics.inbound.breakdown}
            outbound={metrics.outbound.breakdown}
          />
        </div>

        {/* Right Column: Inbound/Outbound Cards, Chart, Activity Log */}
        <div className="lg:col-span-5 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <MetricsCard
              title="Inbound Traffic"
              direction="inbound"
              data={metrics.inbound}
            />
            <MetricsCard
              title="Outbound Traffic"
              direction="outbound"
              data={metrics.outbound}
            />
          </div>

          <TrafficChart
            inboundSMP={metrics.inbound.smp_per_minute}
            outboundSMP={metrics.outbound.smp_per_minute}
          />

          <LiveFeed events={metrics.recent_events} />
        </div>
      </div>

      {/* CCTV Selector Modal */}
      <CCTVSelectorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        streamInfo={streamInfo}
        onSelectSource={handleSelectStreamSource}
      />
    </main>
  );
}
