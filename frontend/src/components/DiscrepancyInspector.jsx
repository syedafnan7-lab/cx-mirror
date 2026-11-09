import React from 'react';
import { AlertCircle, AlertTriangle, Info, Eye, Layers } from 'lucide-react';

export default function DiscrepancyInspector({
  discrepancies = [],
  selectedNodeId,
  onSelectNode
}) {
  const getSeverityBadge = (severity) => {
    switch (severity) {
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

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'business_contract':
        return <AlertCircle className="w-4 h-4 text-rose-400" />;
      case 'geometry':
        return <Layers className="w-4 h-4 text-cyan-400" />;
      case 'typography':
      case 'color':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-wider text-forensicSlate">
            Forensic Audit
          </span>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 mt-0.5">
            <Eye className="w-4 h-4 text-cyan-400" />
            Discrepancy & Contract Inspector
          </h3>
        </div>
        <span className="px-2.5 py-0.5 rounded-full bg-[#182330] border border-[#334155] font-mono text-xs text-white">
          {discrepancies.length} {discrepancies.length === 1 ? 'item' : 'items'}
        </span>
      </div>

      <div className="mt-4 space-y-3 overflow-y-auto max-h-[580px] pr-1">
        {discrepancies.length === 0 ? (
          <div className="text-center py-12 text-forensicSlate text-xs font-mono">
            No regressions or discrepancies detected.
          </div>
        ) : (
          discrepancies.map((disc, idx) => {
            const isSelected = selectedNodeId === disc.node_id;

            return (
              <div
                key={`disc_${disc.node_id}_${idx}`}
                onClick={() => onSelectNode(disc.node_id)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#182330] border-cyan-500 shadow-lg shadow-cyan-500/10'
                    : 'bg-[#0B0F14] border-[#1E293B] hover:border-[#334155]'
                }`}
              >
                {/* Header row */}
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {getCategoryIcon(disc.category)}
                    <span className="font-mono text-xs font-bold text-white">
                      {disc.node_id}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${getSeverityBadge(
                      disc.severity
                    )}`}
                  >
                    {disc.severity}
                  </span>
                </div>

                {/* Explanation */}
                <p className="text-xs text-slate-300 mt-2 font-medium leading-relaxed">
                  {disc.explanation}
                </p>

                {/* Metric Diff */}
                <div className="mt-2 text-[11px] font-mono bg-[#111923] p-2 rounded border border-[#1E293B] space-y-1">
                  <div className="text-cyan-400 truncate">
                    <span className="text-forensicSlate">Expected: </span>
                    {typeof disc.expected === 'object' ? JSON.stringify(disc.expected) : String(disc.expected)}
                  </div>
                  <div className="text-rose-400 truncate">
                    <span className="text-forensicSlate">Actual: </span>
                    {typeof disc.actual === 'object' ? JSON.stringify(disc.actual) : String(disc.actual)}
                  </div>
                  <div className="text-emerald-400 text-[10px] pt-0.5 border-t border-[#1E293B]">
                    <span>Difference: </span>
                    {disc.difference}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

