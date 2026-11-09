import React, { useState, useRef, useCallback } from 'react';
import { Columns } from 'lucide-react';

export default function SplitScreenWipe({
  mockupSrc,
  liveSrc,
  aspectRatio = '1440/1000'
}) {
  const [sliderPos, setSliderPos] = useState(50); // percentage 0-100
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  const handleMove = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(pct);
  }, []);

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);

  const handleMouseMove = (e) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  const handleTouchMove = (e) => {
    if (e.touches && e.touches[0]) {
      handleMove(e.touches[0].clientX);
    }
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchMove={handleTouchMove}
      className="relative select-none overflow-hidden rounded-xl border border-[#1E293B] bg-[#0B0F14] shadow-2xl cursor-ew-resize group"
      style={{ aspectRatio: '1440 / 1000' }}
    >
      {/* Background Image: Live Screenshot (Right side visible) */}
      <img
        src={liveSrc}
        alt="Live Webpage Implementation"
        className="absolute inset-0 w-full h-full object-cover pointer-events-none"
      />

      {/* Foreground Image: Golden Mockup (Clipped by slider position) */}
      <div
        className="absolute inset-0 overflow-hidden pointer-events-none"
        style={{ width: `${sliderPos}%` }}
      >
        <img
          src={mockupSrc}
          alt="Golden Design Mockup"
          className="absolute inset-0 w-full h-full object-cover max-w-none"
          style={{ width: `${containerRef.current?.clientWidth || 1000}px` }}
        />
      </div>

      {/* Floating Labels */}
      <div className="absolute top-4 left-4 z-10 px-3 py-1 rounded bg-[#0B0F14]/80 backdrop-blur border border-cyan-500/40 text-cyan-400 font-mono text-xs font-bold pointer-events-none">
        DESIGN MOCKUP (GOLDEN)
      </div>
      <div className="absolute top-4 right-4 z-10 px-3 py-1 rounded bg-[#0B0F14]/80 backdrop-blur border border-emerald-500/40 text-emerald-400 font-mono text-xs font-bold pointer-events-none">
        LIVE IMPLEMENTATION
      </div>

      {/* Divider Bar & Handle */}
      <div
        className="absolute top-0 bottom-0 z-20 w-0.5 bg-white shadow-[0_0_12px_rgba(255,255,255,0.8)]"
        style={{ left: `${sliderPos}%` }}
        onMouseDown={handleMouseDown}
        onTouchStart={handleMouseDown}
      >
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-[#111923] border-2 border-white flex items-center justify-center shadow-xl cursor-ew-resize text-white">
          <Columns className="w-4 h-4 text-cyan-400" />
        </div>
      </div>
    </div>
  );
}

