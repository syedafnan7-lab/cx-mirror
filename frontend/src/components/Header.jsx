import React from 'react';
import { ShieldCheck, Activity, Layers, FileCheck, Sliders, PlayCircle } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, healthStatus }) {
  const tabs = [
    { id: 'dashboard', label: 'Overview', icon: Activity },
    { id: 'workbench', label: 'Forensic Workbench', icon: Layers },
    { id: 'benchmark', label: 'Benchmark Lab (60-ROC)', icon: Sliders },
    { id: 'contracts', label: 'Reference Contracts', icon: FileCheck },
  ];

  return (
    <header className="border-b border-[#1E293B] bg-[#111923] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-wider text-white">CX MIRROR</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                v2.28+ Native
              </span>
            </div>
            <p className="text-xs text-forensicSlate font-medium">
              Your Design. Your Experience. Mathematically Verified.
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-[#0B0F14] p-1 rounded-lg border border-[#1E293B]">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-forensicSlate hover:text-white hover:bg-[#182330]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System Status Pill */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#182330] border border-[#334155] text-xs">
            <span className={`w-2 h-2 rounded-full ${healthStatus === 'ok' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span className="text-forensicSlate font-mono text-[11px]">
              Engine: <strong className="text-white">{healthStatus === 'ok' ? 'ONLINE' : 'CONNECTING...'}</strong>
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

