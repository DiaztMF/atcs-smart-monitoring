'use client';

import React, { useState, useMemo } from 'react';
import { X, Camera, Link as LinkIcon, Check, MapPin, Radio, Sparkles, Search } from 'lucide-react';
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
  const [searchQuery, setSearchQuery] = useState('');
  const [customUrl, setCustomUrl] = useState('');
  const [customName, setCustomName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const presets = streamInfo?.presets || [];

  const filteredPresets = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return presets;
    return presets.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        (p.location && p.location.toLowerCase().includes(q)) ||
        p.url.toLowerCase().includes(q)
    );
  }, [presets, searchQuery]);

  if (!isOpen) return null;

  const handleSelectPreset = async (preset: CCTVPreset) => {
    setIsSubmitting(true);
    setErrorMsg('');
    try {
      await onSelectSource(preset.url, preset.name);
      onClose();
    } catch {
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
    } catch {
      setErrorMsg('Gagal menyambungkan URL streaming. Pastikan backend aktif.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeUrl = streamInfo?.active_source?.url || '';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div className="relative w-full max-w-3xl bg-white border border-[#e2e8f0] rounded-xl shadow-xl overflow-hidden flex flex-col max-h-[90vh] animate-modal-enter">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-[#e2e8f0] flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-slate-100 text-slate-700">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Pilih Sumber CCTV</h2>
              <p className="text-xs text-slate-500">
                Pilih dari {presets.length} kamera live streaming ATCS Dishub Surakarta atau input URL kustom
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 overflow-y-auto">
          {errorMsg && (
            <div className="p-3 text-xs bg-red-50 text-red-700 border border-red-200 rounded-lg">
              {errorMsg}
            </div>
          )}

          {/* Section 1: Preset CCTV ATCS with Search */}
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-emerald-600" /> Preset Kamera ATCS ({filteredPresets.length} Kamera)
              </h3>

              {/* Search Bar */}
              <div className="relative w-full sm:w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Cari lokasi / simpang..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-7 py-1.5 text-xs bg-slate-50 border border-[#e2e8f0] rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>

            {/* Presets Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 max-h-[340px] overflow-y-auto pr-1">
              {filteredPresets.length === 0 ? (
                <div className="col-span-full py-8 text-center text-xs text-slate-400">
                  Tidak ditemukan kamera dengan kata kunci &quot;{searchQuery}&quot;
                </div>
              ) : (
                filteredPresets.map((preset) => {
                  const isActive = activeUrl === preset.url;
                  return (
                    <button
                      key={preset.id}
                      onClick={() => handleSelectPreset(preset)}
                      disabled={isSubmitting}
                      className={`p-3 rounded-lg text-left border transition-all ${
                        isActive
                          ? 'bg-emerald-50/70 border-emerald-300 ring-1 ring-emerald-300 shadow-sm'
                          : 'bg-white border-[#e2e8f0] hover:border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-1.5">
                        <div className="font-semibold text-[11px] text-slate-800 flex items-center gap-1.5 truncate">
                          {preset.id === 'synthetic_loop' ? (
                            <Sparkles className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                          ) : (
                            <Camera className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          )}
                          <span className="truncate">{preset.name}</span>
                        </div>
                        {isActive && (
                          <span className="p-0.5 rounded-full bg-emerald-100 text-emerald-600 shrink-0">
                            <Check className="w-3 h-3" />
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-1 font-mono truncate">
                        <MapPin className="w-2.5 h-2.5 text-slate-400 shrink-0" />{' '}
                        <span className="truncate">{preset.location}</span>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Section 2: Custom URL Form */}
          <div className="pt-4 border-t border-[#e2e8f0] space-y-3">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <LinkIcon className="w-3.5 h-3.5 text-sky-500" /> Input URL Streaming Kustom
            </h3>
            <p className="text-xs text-slate-500">
              Mendukung URL live stream FLV, HLS (.m3u8), atau MP4 video dari sumber publik Dishub kota lain.
            </p>

            <form onSubmit={handleCustomSubmit} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    Nama Kamera (Opsional)
                  </label>
                  <input
                    type="text"
                    placeholder="Contoh: ATCS Bandung Simpang Dago"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-[#e2e8f0] rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    URL Streaming (FLV / HLS / MP4) *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="http://.../live.flv"
                    value={customUrl}
                    onChange={(e) => setCustomUrl(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-[#e2e8f0] rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 font-mono transition-shadow"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-1">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white text-xs font-medium rounded-md transition-colors active:scale-[0.98] shadow-sm"
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
