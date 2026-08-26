'use client';

import React, { useState } from 'react';
import { X, Camera, Link as LinkIcon, Check, MapPin, Radio, Sparkles } from 'lucide-react';
import { StreamSourceInfo, CCTVPreset } from '@/types';

interface CCTVSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  streamInfo: StreamSourceInfo | null;
  onSelectSource: (url: string, name: string) => Promise<void>;
}

export default function CCTVSelectorModal({
  isOpen,
  onClose,
  streamInfo,
  onSelectSource,
}: CCTVSelectorModalProps) {
  const [customUrl, setCustomUrl] = useState('');
  const [customName, setCustomName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleSelectPreset = async (preset: CCTVPreset) => {
    setIsSubmitting(true);
    setErrorMsg('');
    try {
      await onSelectSource(preset.url, preset.name);
      onClose();
    } catch (err) {
      setErrorMsg('Gagal mengganti sumber CCTV. Periksa koneksi backend.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCustomSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customUrl.trim()) {
      setErrorMsg('Harap masukkan URL streaming CCTV yang valid.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');
    try {
      const name = customName.trim() || 'Custom CCTV Stream';
      await onSelectSource(customUrl.trim(), name);
      setCustomUrl('');
      setCustomName('');
      onClose();
    } catch (err) {
      setErrorMsg('Gagal menyambungkan URL streaming. Pastikan backend aktif.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeUrl = streamInfo?.active_source?.url || '';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Pilih / Input Sumber CCTV</h2>
              <p className="text-xs text-slate-400">
                Pilih dari preset kamera ATCS Dishub atau masukkan URL streaming kustom
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 overflow-y-auto">
          {errorMsg && (
            <div className="p-3 text-xs bg-rose-950/60 text-rose-300 border border-rose-800/80 rounded-xl">
              {errorMsg}
            </div>
          )}

          {/* Section 1: Preset CCTV ATCS */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-400" /> Preset Kamera ATCS Surakarta
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {streamInfo?.presets.map((preset) => {
                const isActive = activeUrl === preset.url;
                return (
                  <button
                    key={preset.id}
                    onClick={() => handleSelectPreset(preset)}
                    disabled={isSubmitting}
                    className={`p-3.5 rounded-xl text-left border transition-all relative ${
                      isActive
                        ? 'bg-emerald-950/40 border-emerald-500/80 ring-1 ring-emerald-500/40'
                        : 'bg-slate-950/50 border-slate-800/90 hover:border-slate-700 hover:bg-slate-800/40'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="font-semibold text-xs text-slate-100 flex items-center gap-1.5">
                        {preset.id === 'synthetic_loop' ? (
                          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        ) : (
                          <Camera className="w-3.5 h-3.5 text-emerald-400" />
                        )}
                        {preset.name}
                      </div>
                      {isActive && (
                        <span className="p-1 rounded-full bg-emerald-500/20 text-emerald-400">
                          <Check className="w-3.5 h-3.5" />
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-1.5">
                      <MapPin className="w-3 h-3 text-slate-500" /> {preset.location}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section 2: Custom URL Form */}
          <div className="pt-4 border-t border-slate-800/80 space-y-3">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <LinkIcon className="w-3.5 h-3.5 text-sky-400" /> Input URL Streaming Kustom
            </h3>
            <p className="text-xs text-slate-400">
              Mendukung URL live stream FLV, HLS (.m3u8), MP4 video, atau RTSP dari Dishub kota lain.
            </p>

            <form onSubmit={handleCustomSubmit} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-300 mb-1">
                    Nama Kamera (Opsional)
                  </label>
                  <input
                    type="text"
                    placeholder="Contoh: ATCS Bandung Simpang Dago"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-300 mb-1">
                    URL Streaming (FLV / HLS / MP4) *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="http://.../live.flv atau https://.../stream.m3u8"
                    value={customUrl}
                    onChange={(e) => setCustomUrl(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white text-xs font-semibold rounded-xl transition-colors shadow-lg"
                >
                  {isSubmitting ? 'Menyambungkan...' : 'Hubungkan CCTV Kustom'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
