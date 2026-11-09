import React from 'react';
import { PlayCircle, ShieldCheck, Shuffle, DollarSign, EyeOff, Bug } from 'lucide-react';

export default function DemoPresetBar({ activePreset, onSelectPreset, onRunAnalysis, loading }) {
  const presets = [
    {
      id: 'clean',
      label: '1. Clean Baseline',
      badge: 'PASS',
      badgeColor: 'bg-emerald-950 text-emerald-400 border-emerald-800',
      icon: ShieldCheck,
      desc: 'Golden baseline, valid dynamic data awareness'
    },
    {
      id: 'drifted',
      label: '2. Drifted Layout',
      badge: 'FAIL',
      badgeColor: 'bg-rose-950 text-rose-400 border-rose-800',
      icon: Shuffle,
      desc: 'Layout displacement, button purple shift, CIoU drop'
    },
    {
      id: 'price_bug',
      label: '3. Price SKU Bug',
      badge: 'CRITICAL',
      badgeColor: 'bg-rose-950 text-rose-400 border-rose-800',
      icon: DollarSign,
      desc: '$19.99 live price violates $24.99 business catalog contract'
    },
    {
      id: 'legal_hidden',
      label: '4. Legal Hidden',
      badge: 'CRITICAL',
      badgeColor: 'bg-rose-950 text-rose-400 border-rose-800',
      icon: EyeOff,
      desc: 'Disclaimer shrunk to 5px with 0.05 opacity (WCAG 1.1:1)'
    },
    {
      id: 'all_bugs',
      label: '5. All Bugs',
      badge: 'CRITICAL',
      badgeColor: 'bg-rose-950 text-rose-400 border-rose-800',
      icon: Bug,
      desc: 'Compounded simultaneous regressions'
    }
  ];

  return (
    <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <PlayCircle className="w-4 h-4 text-cyan-400" />
          <span className="font-mono text-xs font-bold text-white uppercase tracking-wider">
            Hackathon Live Presets (30-Sec Judge Demonstration Sequence)
          </span>
        </div>
        <span className="text-[11px] font-mono text-forensicSlate">
          Select a preset to load and verify live
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5">
        {presets.map((p) => {
          const Icon = p.icon;
          const isSelected = activePreset === p.id;

          return (
            <button
              key={p.id}
              onClick={() => onSelectPreset(p.id)}
              disabled={loading}
              className={`p-3 rounded-lg border text-left transition-all cursor-pointer disabled:opacity-50 ${
                isSelected
                  ? 'bg-gradient-to-b from-[#182330] to-[#14202e] border-cyan-500 shadow-md shadow-cyan-500/10'
                  : 'bg-[#0B0F14] border-[#1E293B] hover:border-[#334155]'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                  <Icon className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{p.label}</span>
                </div>
                <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${p.badgeColor}`}>
                  {p.badge}
                </span>
              </div>
              <p className="text-[11px] text-forensicSlate leading-tight line-clamp-2">
                {p.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

