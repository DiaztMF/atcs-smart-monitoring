'use client';

import React, { useState } from 'react';
import { Camera, Radio, RefreshCw, Layers, Trash2, Video } from 'lucide-react';
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
  onOpenStreamModal: () => void;
}

export default function VideoPlayer({
  streamUrl,
  fps,
  cameraName,
  isConnected,
  roi,
  onSaveROI,
  onResetCounters,
  onOpenStreamModal,
}: VideoPlayerProps) {
  const [editMode, setEditMode] = useState<'inbound' | 'outbound' | 'view'>('view');

  const handleClearROI = () => {
    if (editMode === 'inbound') {
      onSaveROI({ ...roi, inbound: [] });
    } else if (editMode === 'outbound') {
      onSaveROI({ ...roi, outbound: [] });
    } else {
      onSaveROI({ inbound: [], outbound: [] });
    }
  };

  return (
    <div className="glass-panel rounded-2xl overflow-hidden flex flex-col border border-slate-800 shadow-2xl">
      {/* Stream Header */}
      <div className="px-5 py-3.5 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              {cameraName}
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                <Radio className="w-3 h-3 mr-1 animate-pulse" /> LIVE
              </span>
            </h2>
            <p className="text-xs text-slate-400">YOLOv11n + ByteTrack Real-Time Inference</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <div className="text-xs text-slate-400">Stream Rate</div>
            <div className="text-xs font-mono font-bold text-slate-200">{fps.toFixed(1)} FPS</div>
          </div>
          <button
            onClick={onOpenStreamModal}
            className="px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 border border-emerald-500/30"
          >
            <Video className="w-3.5 h-3.5" /> Ganti CCTV / URL
          </button>
          <button
            onClick={onResetCounters}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 border border-slate-700"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      {/* Video Stream Container with Canvas Overlay */}
      <div className="relative aspect-video w-full bg-black flex items-center justify-center overflow-hidden">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={streamUrl}
          alt="Live Traffic Video Stream"
          className="w-full h-full object-cover select-none"
        />

        <CanvasROI
          mode={editMode}
          roi={roi}
          onUpdateROI={onSaveROI}
        />
      </div>

      {/* ROI Toolbar Controls */}
      <div className="px-5 py-3 bg-slate-900/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-medium flex items-center gap-1.5">
            <Layers className="w-4 h-4" /> ROI Mode:
          </span>
          <button
            onClick={() => setEditMode('view')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              editMode === 'view'
                ? 'bg-slate-700 text-white'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            View Only
          </button>
          <button
            onClick={() => setEditMode('inbound')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors border ${
              editMode === 'inbound'
                ? 'bg-emerald-600 text-white border-emerald-500'
                : 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40 hover:bg-emerald-900/60'
            }`}
          >
            Draw Inbound (Green)
          </button>
          <button
            onClick={() => setEditMode('outbound')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors border ${
              editMode === 'outbound'
                ? 'bg-amber-600 text-white border-amber-500'
                : 'bg-amber-950/40 text-amber-400 border-amber-800/40 hover:bg-amber-900/60'
            }`}
          >
            Draw Outbound (Amber)
          </button>
          <button
            onClick={handleClearROI}
            className="px-2.5 py-1.5 rounded-lg bg-rose-950/40 text-rose-400 border border-rose-800/40 hover:bg-rose-900/60 transition-colors flex items-center gap-1"
          >
            <Trash2 className="w-3.5 h-3.5" /> Clear
          </button>
        </div>

        {editMode !== 'view' && (
          <p className="text-slate-400 italic">
            Klik untuk membuat titik (min. 3 titik), <b>Double Click</b> untuk menyimpan poligon.
          </p>
        )}
      </div>
    </div>
  );
}
