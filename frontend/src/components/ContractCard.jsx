import React from 'react';
import { ShieldCheck, AlertCircle, FileText, CheckCircle2, XCircle } from 'lucide-react';

export default function ContractCard({ contracts = [] }) {
  const getCriticalityBadge = (crit) => {
    switch (crit) {
      case 'CRITICAL':
        return 'bg-rose-950/80 text-rose-400 border border-rose-500/40';
      case 'MAJOR':
        return 'bg-amber-950/80 text-amber-400 border border-amber-500/40';
      case 'MINOR':
        return 'bg-blue-950/80 text-blue-400 border border-blue-500/40';
      default:
        return 'bg-slate-800 text-slate-300 border border-slate-700';
    }
  };

  return (
    <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-forensicSlate">
            Business & Legal Rule Engine
          </span>
          <h2 className="text-xl font-bold text-white flex items-center gap-2 mt-0.5">
            <FileText className="w-5 h-5 text-cyan-400" />
            Active Reference Data Contracts
          </h2>
          <p className="text-xs text-forensicSlate mt-1 max-w-xl">
            Deterministic business contracts enforced alongside visual geometry. Critical contract
            failures override visual similarity and enforce immediate application failure.
          </p>
        </div>
        <div className="px-3 py-1 rounded-full bg-[#182330] border border-[#334155] font-mono text-xs text-white">
          {contracts.length} Registered Rules
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contracts.map((c) => (
          <div
            key={c.id}
            className="p-4 rounded-xl bg-[#0B0F14] border border-[#1E293B] flex flex-col justify-between space-y-3"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-cyan-400">{c.id}</span>
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${getCriticalityBadge(
                    c.criticality
                  )}`}
                >
                  {c.criticality}
                </span>
              </div>
              <h4 className="text-sm font-bold text-white mt-1.5">{c.name}</h4>
              <p className="text-xs text-forensicSlate mt-1 leading-relaxed">
                {c.description}
              </p>
            </div>

            <div className="bg-[#111923] p-2.5 rounded-lg border border-[#1E293B] text-[11px] font-mono space-y-1">
              <div className="text-slate-300">
                <span className="text-forensicSlate">Role: </span>
                <strong className="text-white">{c.target_role}</strong>
              </div>
              <div className="text-slate-300">
                <span className="text-forensicSlate">Rule: </span>
                <span className="text-cyan-400">{c.rule}</span>
              </div>
              <div className="text-slate-300">
                <span className="text-forensicSlate">Expected: </span>
                <span className="text-emerald-400 font-bold">{String(c.expected_value)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

