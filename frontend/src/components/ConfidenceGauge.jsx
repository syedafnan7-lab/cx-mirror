import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, ShieldCheck, Cpu } from 'lucide-react';

export default function ConfidenceGauge({
  scores,
  verdict,
  confidence,
  threshold,
  onThresholdChange,
  criticalFailures = 0,
  executionTimeMs = 0
}) {
  const isPass = verdict === 'PASS';

  return (
    <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
      {/* Top Header & Verdict */}
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-forensicSlate">
            Decision Matrix
          </span>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 mt-0.5">
            <Cpu className="w-4 h-4 text-cyan-400" />
            Confidence & Verdict Engine
          </h3>
        </div>

        {/* Verdict Badge */}
        <div
          className={`px-4 py-1.5 rounded-lg flex items-center gap-2 font-mono font-bold text-sm tracking-wider shadow-lg ${
            isPass
              ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/40'
              : 'bg-rose-950/80 text-rose-400 border border-rose-500/40'
          }`}
        >
          {isPass ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          ) : (
            <XCircle className="w-4 h-4 text-rose-400" />
          )}
          <span>{verdict}</span>
        </div>
      </div>

      {/* Primary Score Ring & Stat */}
      <div className="py-5 flex items-center justify-between">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-extrabold font-mono tracking-tight text-white">
            {confidence?.toFixed(1) || '0.0'}%
          </span>
          <span className="text-xs text-forensicSlate font-mono">
            vs τ = {threshold}%
          </span>
        </div>

        <div className="text-right">
          <div className="text-xs font-mono text-forensicSlate">Latency</div>
          <div className="text-sm font-mono text-white font-semibold">
            {executionTimeMs ? `${executionTimeMs} ms` : '—'}
          </div>
        </div>
      </div>

      {/* Threshold Slider */}
      <div className="space-y-2 bg-[#0B0F14] p-3 rounded-lg border border-[#1E293B] mb-5">
        <div className="flex justify-between items-center text-xs">
          <span className="text-forensicSlate font-mono">Decision Threshold (τ)</span>
          <span className="font-mono text-cyan-400 font-bold">{threshold}%</span>
        </div>
        <input
          type="range"
          min="50"
          max="100"
          step="0.5"
          value={threshold}
          onChange={(e) => onThresholdChange(parseFloat(e.target.value))}
          className="w-full accent-cyan-500 cursor-pointer h-1.5 bg-[#1E293B] rounded-lg"
        />
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <span>Tolerant (50%)</span>
          <span>Standard (95%)</span>
          <span>Zero-Tolerance (100%)</span>
        </div>
      </div>

      {/* Breakdown Scores */}
      <div className="grid grid-cols-3 gap-3">
        {/* Visual (60%) */}
        <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
          <div className="text-[10px] font-mono text-forensicSlate uppercase">Visual (60%)</div>
          <div className="text-lg font-mono font-bold text-white mt-1">
            {scores?.visual !== undefined ? `${scores.visual.toFixed(1)}%` : '—'}
          </div>
          <div className="w-full bg-[#0B0F14] h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className="bg-cyan-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, scores?.visual || 0)}%` }}
            />
          </div>
        </div>

        {/* Structural (15%) */}
        <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
          <div className="text-[10px] font-mono text-forensicSlate uppercase">Structure (15%)</div>
          <div className="text-lg font-mono font-bold text-white mt-1">
            {scores?.structural !== undefined ? `${scores.structural.toFixed(1)}%` : '—'}
          </div>
          <div className="w-full bg-[#0B0F14] h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, scores?.structural || 0)}%` }}
            />
          </div>
        </div>

        {/* Contract (25%) */}
        <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
          <div className="text-[10px] font-mono text-forensicSlate uppercase">Contracts (25%)</div>
          <div
            className={`text-lg font-mono font-bold mt-1 ${
              criticalFailures > 0 ? 'text-rose-400' : 'text-emerald-400'
            }`}
          >
            {scores?.contract !== undefined ? `${scores.contract.toFixed(1)}%` : '—'}
          </div>
          <div className="w-full bg-[#0B0F14] h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                criticalFailures > 0 ? 'bg-rose-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, scores?.contract || 0)}%` }}
            />
          </div>
        </div>
      </div>

      {criticalFailures > 0 && (
        <div className="mt-4 p-2.5 rounded bg-rose-950/40 border border-rose-800/60 flex items-center gap-2 text-rose-300 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>
            <strong>CRITICAL CONTRACT VIOLATION:</strong> {criticalFailures} statutory or pricing
            contract(s) failed, forcing automatic FAIL.
          </span>
        </div>
      )}
    </div>
  );
}

