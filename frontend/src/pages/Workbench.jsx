import React, { useState } from 'react';
import {
  Layers,
  Columns,
  SplitSquareVertical,
  PlayCircle,
  Upload,
  Sliders,
  Sparkles,
  Info
} from 'lucide-react';
import LaserOverlay from '../components/LaserOverlay';
import SplitScreenWipe from '../components/SplitScreenWipe';
import ConfidenceGauge from '../components/ConfidenceGauge';
import DiscrepancyInspector from '../components/DiscrepancyInspector';

export default function Workbench({
  analysis,
  loading,
  error,
  threshold,
  setThreshold,
  activePreset,
  onRunAnalysis,
  mockupFile,
  setMockupFile
}) {
  const [viewMode, setViewMode] = useState('laser'); // 'laser' | 'split' | 'side'
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [showMockupBoxes, setShowMockupBoxes] = useState(true);
  const [showDomBoxes, setShowDomBoxes] = useState(true);
  const [showLasers, setShowLasers] = useState(true);

  const mockupUrl = analysis?.artifacts?.mockup_image || '/golden_mockup.png';
  const liveUrl = analysis?.artifacts?.live_screenshot || '/golden_mockup.png';

  // Client-side instantaneous verdict recalculation with threshold slider
  const effectiveVerdict =
    analysis?.summary?.critical_failures > 0
      ? 'FAIL'
      : (analysis?.confidence || 0) >= threshold
      ? 'PASS'
      : 'FAIL';

  return (
    <div className="space-y-6">
      {/* Top Toolbar: View Modes & Overlays Toggle */}
      <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
        {/* Left: View Mode Selectors */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-forensicSlate uppercase tracking-wider mr-2">
            Forensic View:
          </span>
          <div className="flex bg-[#0B0F14] p-1 rounded-lg border border-[#1E293B]">
            <button
              onClick={() => setViewMode('laser')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                viewMode === 'laser'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-forensicSlate hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>SVG Displacement Lasers</span>
            </button>
            <button
              onClick={() => setViewMode('split')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                viewMode === 'split'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-forensicSlate hover:text-white'
              }`}
            >
              <Columns className="w-3.5 h-3.5" />
              <span>Split-Screen Wipe</span>
            </button>
            <button
              onClick={() => setViewMode('side')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                viewMode === 'side'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-forensicSlate hover:text-white'
              }`}
            >
              <SplitSquareVertical className="w-3.5 h-3.5" />
              <span>Side-by-Side</span>
            </button>
          </div>
        </div>

        {/* Right: SVG Toggle Controls */}
        {viewMode === 'laser' && (
          <div className="flex items-center gap-4 text-xs font-mono">
            <label className="flex items-center gap-2 cursor-pointer text-cyan-400">
              <input
                type="checkbox"
                checked={showMockupBoxes}
                onChange={(e) => setShowMockupBoxes(e.target.checked)}
                className="accent-cyan-500 rounded"
              />
              <span>Mockup Boxes</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-emerald-400">
              <input
                type="checkbox"
                checked={showDomBoxes}
                onChange={(e) => setShowDomBoxes(e.target.checked)}
                className="accent-emerald-500 rounded"
              />
              <span>DOM Boxes</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-rose-400">
              <input
                type="checkbox"
                checked={showLasers}
                onChange={(e) => setShowLasers(e.target.checked)}
                className="accent-rose-500 rounded"
              />
              <span>Displacement Lasers</span>
            </label>
          </div>
        )}

        {/* Re-Analyze Button */}
        <button
          onClick={() => onRunAnalysis(activePreset)}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold shadow-lg shadow-emerald-600/20 transition-all cursor-pointer disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          <span>{loading ? 'VERIFYING...' : 'RUN VERIFICATION'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs font-mono">
          Verification Error: {error}
        </div>
      )}

      {/* Main Forensic Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Visual Canvas View */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-4 shadow-xl">
            {/* View Mode 1: SVG Laser Overlay */}
            {viewMode === 'laser' && (
              <div
                className="relative overflow-hidden rounded-lg border border-[#1E293B] bg-[#0B0F14]"
                style={{ aspectRatio: '1440 / 1000' }}
              >
                {/* Live Implementation Screenshot Background */}
                <img
                  src={liveUrl}
                  alt="Live DOM Webpage"
                  className="w-full h-full object-cover"
                />

                {/* Interactive Laser Vector Overlay */}
                <LaserOverlay
                  matches={analysis?.matches || []}
                  mockupNodes={analysis?.graph?.mockup_nodes || {}}
                  domNodes={analysis?.graph?.dom_nodes || {}}
                  selectedNodeId={selectedNodeId}
                  onSelectNode={setSelectedNodeId}
                  showMockupBoxes={showMockupBoxes}
                  showDomBoxes={showDomBoxes}
                  showLasers={showLasers}
                  showLabels={true}
                />
              </div>
            )}

            {/* View Mode 2: Split-Screen Wipe */}
            {viewMode === 'split' && (
              <SplitScreenWipe mockupSrc={mockupUrl} liveSrc={liveUrl} />
            )}

            {/* View Mode 3: Side-by-Side */}
            {viewMode === 'side' && (
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div className="text-[11px] font-mono text-cyan-400 font-bold px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-800 inline-block">
                    GOLDEN MOCKUP (DESIGN)
                  </div>
                  <div className="rounded-lg border border-[#1E293B] overflow-hidden" style={{ aspectRatio: '1440 / 1000' }}>
                    <img src={mockupUrl} alt="Mockup" className="w-full h-full object-cover" />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="text-[11px] font-mono text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 inline-block">
                    LIVE WEBPAGE (DOM)
                  </div>
                  <div className="rounded-lg border border-[#1E293B] overflow-hidden" style={{ aspectRatio: '1440 / 1000' }}>
                    <img src={liveUrl} alt="Live" className="w-full h-full object-cover" />
                  </div>
                </div>
              </div>
            )}

            {/* Canvas Footer Metadata */}
            <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-forensicSlate pt-2 border-t border-[#1E293B]">
              <div>
                Viewport: <span className="text-white">1440 x 1000</span> | Renderer:{' '}
                <span className="text-white">Chromium CDP</span>
              </div>
              <div>
                Matches: <span className="text-emerald-400 font-bold">{analysis?.summary?.matched_nodes || 0}</span> /{' '}
                {analysis?.summary?.total_mockup_nodes || 0} nodes
              </div>
            </div>
          </div>
        </div>

        {/* Right Col: Confidence Gauge & Discrepancy Inspector */}
        <div className="space-y-6">
          <ConfidenceGauge
            scores={analysis?.scores}
            verdict={effectiveVerdict}
            confidence={analysis?.confidence}
            threshold={threshold}
            onThresholdChange={setThreshold}
            criticalFailures={analysis?.summary?.critical_failures || 0}
            executionTimeMs={analysis?.execution_time_ms}
          />

          <DiscrepancyInspector
            discrepancies={analysis?.discrepancies || []}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
          />
        </div>
      </div>
    </div>
  );
}

