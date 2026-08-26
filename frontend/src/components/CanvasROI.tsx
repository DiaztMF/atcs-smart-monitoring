'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ROICoordinates } from '@/types';

interface CanvasROIProps {
  mode: 'inbound' | 'outbound' | 'view';
  roi: ROICoordinates;
  onUpdateROI: (updatedROI: ROICoordinates) => void;
}

export default function CanvasROI({ mode, roi, onUpdateROI }: CanvasROIProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [activePoints, setActivePoints] = useState<[number, number][]>([]);

  // Redraw canvas whenever ROI, active points, or mode change
  const renderCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Draw Inbound saved polygon (Emerald / Cyan: #10b981)
    if (roi.inbound && roi.inbound.length > 2) {
      ctx.beginPath();
      ctx.moveTo(roi.inbound[0][0] * w, roi.inbound[0][1] * h);
      for (let i = 1; i < roi.inbound.length; i++) {
        ctx.lineTo(roi.inbound[i][0] * w, roi.inbound[i][1] * h);
      }
      ctx.closePath();
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2.5;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.18)';
      ctx.fill();
      ctx.stroke();

      // Vertex dots
      for (const pt of roi.inbound) {
        ctx.beginPath();
        ctx.arc(pt[0] * w, pt[1] * h, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#10b981';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
      }
    }

    // Draw Outbound saved polygon (Amber / Rose: #f59e0b)
    if (roi.outbound && roi.outbound.length > 2) {
      ctx.beginPath();
      ctx.moveTo(roi.outbound[0][0] * w, roi.outbound[0][1] * h);
      for (let i = 1; i < roi.outbound.length; i++) {
        ctx.lineTo(roi.outbound[i][0] * w, roi.outbound[i][1] * h);
      }
      ctx.closePath();
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2.5;
      ctx.fillStyle = 'rgba(245, 158, 11, 0.18)';
      ctx.fill();
      ctx.stroke();

      // Vertex dots
      for (const pt of roi.outbound) {
        ctx.beginPath();
        ctx.arc(pt[0] * w, pt[1] * h, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#f59e0b';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
      }
    }

    // Draw currently active points being placed by the user
    if (activePoints.length > 0) {
      ctx.beginPath();
      ctx.moveTo(activePoints[0][0] * w, activePoints[0][1] * h);
      for (let i = 1; i < activePoints.length; i++) {
        ctx.lineTo(activePoints[i][0] * w, activePoints[i][1] * h);
      }
      ctx.strokeStyle = mode === 'inbound' ? '#34d399' : '#fbbf24';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw active vertices
      for (const pt of activePoints) {
        ctx.beginPath();
        ctx.arc(pt[0] * w, pt[1] * h, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  }, [roi, activePoints, mode]);

  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (canvas && canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        renderCanvas();
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [renderCanvas]);

  useEffect(() => {
    renderCanvas();
  }, [renderCanvas]);

  // Reset active points if user switches modes
  useEffect(() => {
    setActivePoints([]);
  }, [mode]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (mode === 'view') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    // Normalizing coordinates to 0.0 - 1.0 range
    const normalizedPoint: [number, number] = [
      Math.max(0, Math.min(1, Number(x.toFixed(3)))),
      Math.max(0, Math.min(1, Number(y.toFixed(3)))),
    ];

    setActivePoints((prev) => [...prev, normalizedPoint]);
  };

  const handleDoubleClick = () => {
    if (mode === 'view' || activePoints.length < 3) return;
    const updated = { ...roi };
    if (mode === 'inbound') {
      updated.inbound = activePoints;
    } else if (mode === 'outbound') {
      updated.outbound = activePoints;
    }
    onUpdateROI(updated);
    setActivePoints([]);
  };

  return (
    <canvas
      ref={canvasRef}
      onClick={handleCanvasClick}
      onDoubleClick={handleDoubleClick}
      className={`absolute inset-0 z-10 w-full h-full ${
        mode !== 'view' ? 'cursor-crosshair pointer-events-auto' : 'pointer-events-none'
      }`}
    />
  );
}
