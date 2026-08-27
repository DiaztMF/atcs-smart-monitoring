'use client';

import React, { useState, useEffect } from 'react';
import { Layers, Trash2, RefreshCw, CheckCircle2, Pencil } from 'lucide-react';
import CanvasROI from './CanvasROI';
import { ROICoordinates } from '@/types';

interface VideoPlayerProps {
  streamUrl: string;
  fps: number;
  cameraName: string;
  isConnected: boolean;
  roi: ROICoordinates;
  onSaveROI: (roi: ROICoordinates) => void;
  onResetCounters: () => void;
}

export default function VideoPlayer({
  streamUrl,
  fps,
  cameraName,
  isConnected,
  roi,
  onSaveROI,
  onResetCounters,
}: VideoPlayerProps) {
  const [editMode, setEditMode] = useState<'inbound' | 'outbound' | 'view'>('inbound');
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentTime, setCurrentTime] = useState<string>('');

  // Update clock every second
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        `${now.toLocaleDateString('id-ID')} ${now.toLocaleTimeString('en-GB')}`
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleClearROI = () => {
    if (editMode === 'inbound') {
      onSaveROI({ ...roi, inbound: [] });
    } else if (editMode === 'outbound') {
      onSaveROI({ ...roi, outbound: [] });
    } else {
      onSaveROI({ inbound: [], outbound: [] });
    }
  };

  const currentMode = isDrawing ? editMode : 'view';

  return (
    <div className="flex flex-col gap-3">
      {/* CCTV HUD Video Frame */}
      <div className="bg-slate-950 rounded-xl overflow-hidden aspect-video relative flex-shrink-0 border border-slate-800 shadow-sm">
        {/* Stream Video Image */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={streamUrl}
          alt="Live Traffic Video Stream"
          className="w-full h-full object-cover select-none"
        />

        {/* Interactive Canvas Overlay */}
        <CanvasROI
          mode={currentMode}
          roi={roi}
          onUpdateROI={(updated) => {
            onSaveROI(updated);
            setIsDrawing(false);
          }}
        />

        {/* HUD: Top-Left Camera Name */}
        <div className="absolute top-3 left-3 pointer-events-none z-20">
          <span className="text-[11px] font-mono text-slate-200 bg-slate-900/80 px-2 py-1 rounded backdrop-blur-sm border border-slate-700/50">
            {cameraName}
          </span>
        </div>

        {/* HUD: Top-Right LIVE & FPS Badges */}
        <div className="absolute top-3 right-3 flex items-center gap-2 pointer-events-none z-20">
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-red-600 text-white text-[11px] font-bold tracking-widest shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            LIVE
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-800/80 text-slate-200 text-[11px] font-mono border border-slate-700/50">
            {fps > 0 ? `${fps.toFixed(0)} FPS` : '15 FPS'}
          </span>
        </div>

        {/* HUD: Bottom-Left Timestamp */}
        <div className="absolute bottom-3 left-3 pointer-events-none z-20">
          <span className="text-[11px] font-mono text-slate-300 bg-slate-900/80 px-2 py-1 rounded backdrop-blur-sm border border-slate-700/50">
            {currentTime || 'Memuat waktu...'}
          </span>
        </div>

        {/* HUD: Drawing Mode Helper Indicator */}
        {isDrawing && (
          <div className="absolute bottom-3 right-3 z-20">
            <span className="text-[11px] font-medium text-white bg-emerald-600/90 px-2.5 py-1 rounded backdrop-blur-sm shadow border border-emerald-400/50 animate-pulse">
              Mode Gambar Aktif: Klik titik di canvas, Double-click untuk simpan.
            </span>
          </div>
        )}
      </div>

      {/* ROI Toolbar */}
      <div className="bg-white border border-[#e2e8f0] rounded-lg px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
        {/* Left Side: ROI Mode Selection */}
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1 mr-1">
            <Layers className="w-3.5 h-3.5" /> ROI Mode
          </span>

          <button
            onClick={() => {
              setEditMode('inbound');
            }}
            className={`px-3 py-1.5 rounded-md text-[13px] font-semibold transition-colors border ${
              editMode === 'inbound'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm'
                : 'bg-slate-50 text-slate-600 border-transparent hover:border-slate-200'
            }`}
          >
            Masuk (Inbound)
          </button>

          <button
            onClick={() => {
              setEditMode('outbound');
            }}
            className={`px-3 py-1.5 rounded-md text-[13px] font-semibold transition-colors border ${
              editMode === 'outbound'
                ? 'bg-amber-50 text-amber-700 border-amber-200 shadow-sm'
                : 'bg-slate-50 text-slate-600 border-transparent hover:border-slate-200'
            }`}
          >
            Keluar (Outbound)
          </button>
        </div>

        {/* Right Side: ROI Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsDrawing((prev) => !prev)}
            className={`px-3 py-1.5 rounded-md text-[13px] font-medium transition-colors flex items-center gap-1.5 border ${
              isDrawing
                ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            {isDrawing ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Selesai Gambar
              </>
            ) : (
              <>
                <Pencil className="w-3.5 h-3.5 text-slate-500" /> Edit Poligon
              </>
            )}
          </button>

          <button
            onClick={handleClearROI}
            className="px-3 py-1.5 rounded-md text-[13px] font-medium text-red-600 hover:bg-red-50 border border-transparent hover:border-red-200 transition-colors flex items-center gap-1.5"
            title="Hapus titik poligon aktif"
          >
            <Trash2 className="w-3.5 h-3.5" /> Reset ROI
          </button>

          <button
            onClick={onResetCounters}
            className="px-3 py-1.5 rounded-md text-[13px] font-medium text-slate-600 hover:bg-slate-100 border border-slate-200 transition-colors flex items-center gap-1.5"
            title="Reset akumulasi hitungan kendaraan"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" /> Reset Hitungan
          </button>
        </div>
      </div>
    </div>
  );
}
