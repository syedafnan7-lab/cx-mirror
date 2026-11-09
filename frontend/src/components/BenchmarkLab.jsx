import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { PlayCircle, ShieldCheck, AlertOctagon, BarChart2, RefreshCw } from 'lucide-react';
import { fetchROCBenchmark } from '../services/api';

export default function BenchmarkLab() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const loadBenchmark = async (seed = 42) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchROCBenchmark(seed);
      setBenchmarkData(data);
    } catch (err) {
      setError(err.message || 'Failed to execute benchmark');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBenchmark(42);
  }, []);

  // Merge ROC points for Recharts plotting
  const chartData = [];
  if (benchmarkData) {
    const cxCurve = benchmarkData.cx_roc_curve || [];
    const pixelCurve = benchmarkData.pixel_roc_curve || [];

    // Sample 20 points along FPR axis
    for (let i = 0; i <= 20; i++) {
      const fpr = i / 20;
      // Find closest CX TPR
      const cxPoint = cxCurve.reduce((prev, curr) =>
        Math.abs(curr.fpr - fpr) < Math.abs(prev.fpr - fpr) ? curr : prev, cxCurve[0] || { tpr: 0 });
      // Find closest Pixel TPR
      const pxPoint = pixelCurve.reduce((prev, curr) =>
        Math.abs(curr.fpr - fpr) < Math.abs(prev.fpr - fpr) ? curr : prev, pixelCurve[0] || { tpr: 0 });

      chartData.push({
        fpr: fpr,
        cxMirror: cxPoint ? cxPoint.tpr : fpr,
        pixelDiff: pxPoint ? pxPoint.tpr : fpr,
        baseline: fpr
      });
    }
  }

  return (
    <div className="space-y-6">
      {/* Header & Control Banner */}
      <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-6 shadow-xl flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono uppercase tracking-wider text-cyan-400 font-bold px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800">
              Honest Mathematical Benchmarking
            </span>
            <span className="text-xs font-mono text-forensicSlate">Seed = 42 (Fixed)</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">
            60-Scenario ROC-AUC Benchmark Laboratory
          </h2>
          <p className="text-xs text-forensicSlate mt-0.5 max-w-2xl">
            Empirical comparative analysis between CX Mirror multi-modal deterministic verification
            and traditional pixel-difference algorithms across 60 rigorous e-commerce checkout scenarios.
          </p>
        </div>

        <button
          onClick={() => loadBenchmark(42)}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-mono text-xs font-bold text-white shadow-lg shadow-blue-600/20 transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'CALCULATING...' : 'RUN 60-SCENARIO BENCHMARK'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs font-mono">
          Benchmark Error: {error}
        </div>
      )}

      {/* Main Results Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Recharts ROC Curve */}
        <div className="lg:col-span-2 bg-[#111923] border border-[#1E293B] rounded-xl p-6 shadow-xl flex flex-col">
          <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
            <div>
              <span className="text-[11px] font-mono text-forensicSlate uppercase">Receiver Operating Characteristic</span>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-cyan-400" />
                Comparative ROC Curves (TPR vs FPR)
              </h3>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-cyan-400 inline-block" />
                <span className="text-white">CX Mirror: <strong>AUC {benchmarkData?.cx_mirror_auc?.toFixed(4) || '—'}</strong></span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-rose-400 inline-block border-dashed border-b" />
                <span className="text-slate-400">Pixel Diff: <strong>AUC {benchmarkData?.pixel_diff_auc?.toFixed(4) || '—'}</strong></span>
              </div>
            </div>
          </div>

          <div className="h-[360px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis
                  dataKey="fpr"
                  domain={[0, 1]}
                  tick={{ fill: '#94A3B8', fontSize: 11, fontFamily: 'monospace' }}
                  label={{ value: 'False Positive Rate (FPR)', position: 'insideBottom', offset: -10, fill: '#94A3B8', fontSize: 11 }}
                />
                <YAxis
                  domain={[0, 1]}
                  tick={{ fill: '#94A3B8', fontSize: 11, fontFamily: 'monospace' }}
                  label={{ value: 'True Positive Rate (TPR)', angle: -90, position: 'insideLeft', fill: '#94A3B8', fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F14', borderColor: '#334155', borderRadius: '8px', color: '#F8FAFC', fontFamily: 'monospace', fontSize: '11px' }}
                />
                {/* Chance diagonal */}
                <Line
                  type="monotone"
                  dataKey="baseline"
                  stroke="#475569"
                  strokeDasharray="4 4"
                  dot={false}
                  name="Chance (0.50)"
                />
                {/* Pixel Diff */}
                <Line
                  type="monotone"
                  dataKey="pixelDiff"
                  stroke="#F43F5E"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 3, fill: '#F43F5E' }}
                  name="Pixel Diff"
                />
                {/* CX Mirror */}
                <Line
                  type="monotone"
                  dataKey="cxMirror"
                  stroke="#38BDF8"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#38BDF8' }}
                  name="CX Mirror"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Col: Confusion Matrix & Key Metrics */}
        <div className="space-y-6">
          {/* Key Metric Highlights */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#182330] p-4 rounded-xl border border-[#1E293B]">
              <div className="text-[10px] font-mono text-forensicSlate uppercase">CX Mirror AUC</div>
              <div className="text-2xl font-mono font-extrabold text-cyan-400 mt-1">
                {benchmarkData?.cx_mirror_auc?.toFixed(4) || '—'}
              </div>
              <div className="text-[10px] text-emerald-400 font-mono mt-0.5">Target: &ge; 0.98</div>
            </div>

            <div className="bg-[#182330] p-4 rounded-xl border border-[#1E293B]">
              <div className="text-[10px] font-mono text-forensicSlate uppercase">Pixel Diff AUC</div>
              <div className="text-2xl font-mono font-extrabold text-rose-400 mt-1">
                {benchmarkData?.pixel_diff_auc?.toFixed(4) || '—'}
              </div>
              <div className="text-[10px] text-slate-400 font-mono mt-0.5">Expected: ~0.61</div>
            </div>

            <div className="bg-[#182330] p-4 rounded-xl border border-[#1E293B]">
              <div className="text-[10px] font-mono text-forensicSlate uppercase">Precision</div>
              <div className="text-xl font-mono font-bold text-white mt-1">
                {benchmarkData?.precision ? `${(benchmarkData.precision * 100).toFixed(1)}%` : '—'}
              </div>
            </div>

            <div className="bg-[#182330] p-4 rounded-xl border border-[#1E293B]">
              <div className="text-[10px] font-mono text-forensicSlate uppercase">Recall</div>
              <div className="text-xl font-mono font-bold text-white mt-1">
                {benchmarkData?.recall ? `${(benchmarkData.recall * 100).toFixed(1)}%` : '—'}
              </div>
            </div>
          </div>

          {/* CX Mirror Confusion Matrix */}
          <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
            <div className="text-[11px] font-mono text-forensicSlate uppercase mb-3">
              CX Mirror Confusion Matrix (N = 60)
            </div>
            <div className="grid grid-cols-2 gap-2 text-center font-mono text-xs">
              <div className="bg-emerald-950/60 border border-emerald-600/40 p-3 rounded-lg">
                <div className="text-[10px] text-emerald-400 uppercase">True Positive (TP)</div>
                <div className="text-xl font-bold text-white mt-1">
                  {benchmarkData?.cx_confusion_matrix?.true_positive ?? '—'}
                </div>
                <div className="text-[10px] text-slate-400">Defects Caught</div>
              </div>

              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg">
                <div className="text-[10px] text-slate-400 uppercase">False Positive (FP)</div>
                <div className="text-xl font-bold text-white mt-1">
                  {benchmarkData?.cx_confusion_matrix?.false_positive ?? '—'}
                </div>
                <div className="text-[10px] text-slate-400">False Alarms</div>
              </div>

              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg">
                <div className="text-[10px] text-slate-400 uppercase">False Negative (FN)</div>
                <div className="text-xl font-bold text-white mt-1">
                  {benchmarkData?.cx_confusion_matrix?.false_negative ?? '—'}
                </div>
                <div className="text-[10px] text-slate-400">Defects Missed</div>
              </div>

              <div className="bg-emerald-950/60 border border-emerald-600/40 p-3 rounded-lg">
                <div className="text-[10px] text-emerald-400 uppercase">True Negative (TN)</div>
                <div className="text-xl font-bold text-white mt-1">
                  {benchmarkData?.cx_confusion_matrix?.true_negative ?? '—'}
                </div>
                <div className="text-[10px] text-slate-400">Valid Dynamic Pass</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Composition Breakdown */}
      <div className="bg-[#111923] border border-[#1E293B] rounded-xl p-5 shadow-xl">
        <h3 className="text-sm font-bold text-white mb-3">
          60-Scenario Composition (Seed 42)
        </h3>
        <div className="grid grid-cols-5 gap-3 text-center font-mono text-xs">
          <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
            <div className="text-emerald-400 font-bold text-lg">15</div>
            <div className="text-[10px] text-forensicSlate mt-1">Legitimate Dynamic Variations</div>
            <div className="text-[9px] text-emerald-500 font-semibold mt-0.5">Label: 0 (PASS)</div>
          </div>
          <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
            <div className="text-cyan-400 font-bold text-lg">15</div>
            <div className="text-[10px] text-forensicSlate mt-1">Geometry Shifts & Overlaps</div>
            <div className="text-[9px] text-rose-400 font-semibold mt-0.5">Label: 1 (FAIL)</div>
          </div>
          <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
            <div className="text-amber-400 font-bold text-lg">10</div>
            <div className="text-[10px] text-forensicSlate mt-1">Typography & Color Drifts</div>
            <div className="text-[9px] text-rose-400 font-semibold mt-0.5">Label: 1 (FAIL)</div>
          </div>
          <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
            <div className="text-rose-400 font-bold text-lg">10</div>
            <div className="text-[10px] text-forensicSlate mt-1">Price SKU Contract Defects</div>
            <div className="text-[9px] text-rose-400 font-semibold mt-0.5">Label: 1 (FAIL)</div>
          </div>
          <div className="bg-[#182330] p-3 rounded-lg border border-[#1E293B]">
            <div className="text-purple-400 font-bold text-lg">10</div>
            <div className="text-[10px] text-forensicSlate mt-1">Legal Disclaimer Defects</div>
            <div className="text-[9px] text-rose-400 font-semibold mt-0.5">Label: 1 (FAIL)</div>
          </div>
        </div>
      </div>
    </div>
  );
}

