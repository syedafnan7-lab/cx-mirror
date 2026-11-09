import React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  BarChart2,
  FileCheck,
  ArrowRight,
  Sparkles,
  Cpu
} from 'lucide-react';

export default function Dashboard({
  analysis,
  onNavigateTab,
  onSelectPreset,
  activePreset
}) {
  const isPass = analysis?.verdict === 'PASS';

  return (
    <div className="space-y-8 pb-12">
      {/* Hero Executive Banner */}
      <div className="bg-gradient-to-r from-[#111923] via-[#14202e] to-[#111923] border border-[#1E293B] rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <div className="max-w-3xl space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-800 text-cyan-400 font-mono text-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span>HackStellar PS-18 — AI Testing Against Design Mockups</span>
          </div>

          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            Your Design. Your Experience.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              Mathematically Verified.
            </span>
          </h1>

          <p className="text-sm text-forensicSlate leading-relaxed">
            CX Mirror eliminates the fragility of pixel-diff and hallucinations of pure vision LLMs
            through a multi-modal deterministic verification engine: Complete IoU (CIoU), windowed SSIM,
            CIE L*a*b* Delta E, Hungarian assignment, and statutory business contracts.
          </p>

          <div className="pt-2 flex items-center gap-4">
            <button
              onClick={() => onNavigateTab('workbench')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs font-bold shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
            >
              <span>OPEN FORENSIC WORKBENCH</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigateTab('benchmark')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#182330] hover:bg-[#202d3d] border border-[#334155] text-forensicSlate hover:text-white font-mono text-xs font-semibold transition-all cursor-pointer"
            >
              <BarChart2 className="w-4 h-4 text-cyan-400" />
              <span>VIEW 60-ROC BENCHMARK</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Verification Status */}
        <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
          <div className="text-[11px] font-mono text-forensicSlate uppercase">Verdict</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-2xl font-extrabold font-mono text-white">
              {analysis?.verdict || 'PENDING'}
            </span>
            <div
              className={`p-2 rounded-lg ${
                isPass
                  ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/40'
                  : 'bg-rose-950/80 text-rose-400 border border-rose-500/40'
              }`}
            >
              {isPass ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
            </div>
          </div>
          <div className="text-xs text-forensicSlate font-mono mt-2">
            Preset: <strong className="text-cyan-400">{activePreset.toUpperCase()}</strong>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
          <div className="text-[11px] font-mono text-forensicSlate uppercase">Confidence Score</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold font-mono text-cyan-400">
              {analysis?.confidence !== undefined ? `${analysis.confidence.toFixed(1)}%` : '—'}
            </span>
            <span className="text-xs font-mono text-forensicSlate">Threshold: 95%</span>
          </div>
          <div className="w-full bg-[#0B0F14] h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-cyan-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, analysis?.confidence || 0)}%` }}
            />
          </div>
        </div>

        {/* Matched Nodes */}
        <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
          <div className="text-[11px] font-mono text-forensicSlate uppercase">Graph Matching</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold font-mono text-white">
              {analysis?.summary?.matched_nodes || 0}
            </span>
            <span className="text-xs font-mono text-emerald-400 font-semibold">
              / {analysis?.summary?.total_mockup_nodes || 0} design nodes
            </span>
          </div>
          <div className="text-xs text-forensicSlate font-mono mt-3">
            Bipartite Hungarian Assignment
          </div>
        </div>

        {/* Discrepancies */}
        <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
          <div className="text-[11px] font-mono text-forensicSlate uppercase">Regressions</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span
              className={`text-3xl font-extrabold font-mono ${
                (analysis?.summary?.critical_failures || 0) > 0 ? 'text-rose-400' : 'text-white'
              }`}
            >
              {analysis?.summary?.discrepancies || 0}
            </span>
            <span className="text-xs font-mono text-rose-400">
              {analysis?.summary?.critical_failures || 0} Critical
            </span>
          </div>
          <div className="text-xs text-forensicSlate font-mono mt-3">
            Latency: {analysis?.execution_time_ms ? `${analysis.execution_time_ms} ms` : '—'}
          </div>
        </div>
      </div>

      {/* 30-Second Judging Demonstration Sequence */}
      <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-6 shadow-xl space-y-4">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-cyan-400 font-bold">
            Judging Panel Walkthrough
          </span>
          <h3 className="text-base font-bold text-white mt-0.5">
            The 5-Step Hackathon Demonstration Sequence
          </h3>
          <p className="text-xs text-forensicSlate mt-0.5">
            Click any step to verify live application behavior across all defect classes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div
            onClick={() => onSelectPreset('clean')}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              activePreset === 'clean' ? 'bg-[#182330] border-cyan-500' : 'bg-[#0B0F14] border-[#1E293B]'
            }`}
          >
            <div className="text-xs font-mono font-bold text-emerald-400">STEP 1: CLEAN</div>
            <div className="text-sm font-bold text-white mt-1">Dynamic Awareness</div>
            <p className="text-xs text-forensicSlate mt-1">
              Golden mockup vs live checkout with authorized SKU contract.
            </p>
            <div className="mt-2 text-[10px] font-mono text-emerald-400 font-bold">EXPECTED: PASS</div>
          </div>

          <div
            onClick={() => onSelectPreset('price_bug')}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              activePreset === 'price_bug' ? 'bg-[#182330] border-cyan-500' : 'bg-[#0B0F14] border-[#1E293B]'
            }`}
          >
            <div className="text-xs font-mono font-bold text-rose-400">STEP 2: PRICE BUG</div>
            <div className="text-sm font-bold text-white mt-1">Contract Integrity</div>
            <p className="text-xs text-forensicSlate mt-1">
              $19.99 live price violates $24.99 SKU business contract.
            </p>
            <div className="mt-2 text-[10px] font-mono text-rose-400 font-bold">EXPECTED: CRITICAL FAIL</div>
          </div>

          <div
            onClick={() => onSelectPreset('legal_hidden')}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              activePreset === 'legal_hidden' ? 'bg-[#182330] border-cyan-500' : 'bg-[#0B0F14] border-[#1E293B]'
            }`}
          >
            <div className="text-xs font-mono font-bold text-rose-400">STEP 3: LEGAL HIDDEN</div>
            <div className="text-sm font-bold text-white mt-1">Statutory Compliance</div>
            <p className="text-xs text-forensicSlate mt-1">
              Disclaimer shrunk to 5px with 0.05 opacity (WCAG AA violation).
            </p>
            <div className="mt-2 text-[10px] font-mono text-rose-400 font-bold">EXPECTED: CRITICAL FAIL</div>
          </div>

          <div
            onClick={() => onSelectPreset('drifted')}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              activePreset === 'drifted' ? 'bg-[#182330] border-cyan-500' : 'bg-[#0B0F14] border-[#1E293B]'
            }`}
          >
            <div className="text-xs font-mono font-bold text-amber-400">STEP 4: DRIFTED</div>
            <div className="text-sm font-bold text-white mt-1">Displacement Lasers</div>
            <p className="text-xs text-forensicSlate mt-1">
              Interactive SVG lasers display exact dx, dy, and Delta E vectors.
            </p>
            <div className="mt-2 text-[10px] font-mono text-rose-400 font-bold">EXPECTED: FAIL</div>
          </div>

          <div
            onClick={() => onNavigateTab('benchmark')}
            className="p-4 rounded-xl border border-[#1E293B] bg-[#0B0F14] cursor-pointer hover:border-[#334155] transition-all"
          >
            <div className="text-xs font-mono font-bold text-cyan-400">STEP 5: BENCHMARK</div>
            <div className="text-sm font-bold text-white mt-1">ROC-AUC Proof</div>
            <p className="text-xs text-forensicSlate mt-1">
              60 scenarios proving superiority over pixel diff (AUC &ge; 0.98 vs ~0.61).
            </p>
            <div className="mt-2 text-[10px] font-mono text-cyan-400 font-bold">VIEW LAB &rarr;</div>
          </div>
        </div>
      </div>
    </div>
  );
}

