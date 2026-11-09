import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DemoPresetBar from './components/DemoPresetBar';
import Dashboard from './pages/Dashboard';
import Workbench from './pages/Workbench';
import BenchmarkPage from './pages/BenchmarkPage';
import ContractCard from './components/ContractCard';
import { runAnalysis, fetchHealth, fetchReferenceData } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('workbench'); // Start in workbench for instant demo
  const [activePreset, setActivePreset] = useState('clean');
  const [threshold, setThreshold] = useState(95.0);
  const [mockupFile, setMockupFile] = useState(null);

  const [analysis, setAnalysis] = useState(null);
  const [referenceData, setReferenceData] = useState([]);
  const [healthStatus, setHealthStatus] = useState('offline');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize health check and reference contracts
  useEffect(() => {
    fetchHealth()
      .then((h) => setHealthStatus(h.status))
      .catch(() => setHealthStatus('offline'));

    fetchReferenceData()
      .then((data) => setReferenceData(data.contracts || []))
      .catch((err) => console.error('Failed to load reference contracts:', err));
  }, []);

  // Execute verification analysis
  const executeAnalysis = async (presetToRun = activePreset) => {
    setLoading(true);
    setError(null);
    try {
      const res = await runAnalysis({
        mockupFile,
        preset: presetToRun,
        threshold: threshold,
      });
      setAnalysis(res);
      setActivePreset(presetToRun);
    } catch (err) {
      setError(err.message || 'Verification execution failed');
    } finally {
      setLoading(false);
    }
  };

  // Run clean baseline on initial mount
  useEffect(() => {
    executeAnalysis('clean');
  }, []);

  const handleSelectPreset = (presetId) => {
    setActivePreset(presetId);
    executeAnalysis(presetId);
  };

  return (
    <div className="min-h-screen bg-[#0B0F14] text-[#F8FAFC] flex flex-col font-sans">
      {/* Top Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthStatus={healthStatus}
      />

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
        {/* Preset Bar always available for instant judge testing */}
        <DemoPresetBar
          activePreset={activePreset}
          onSelectPreset={handleSelectPreset}
          onRunAnalysis={executeAnalysis}
          loading={loading}
        />

        {/* Tab 1: Overview Dashboard */}
        {activeTab === 'dashboard' && (
          <Dashboard
            analysis={analysis}
            onNavigateTab={setActiveTab}
            onSelectPreset={handleSelectPreset}
            activePreset={activePreset}
          />
        )}

        {/* Tab 2: Forensic Workbench */}
        {activeTab === 'workbench' && (
          <Workbench
            analysis={analysis}
            loading={loading}
            error={error}
            threshold={threshold}
            setThreshold={setThreshold}
            activePreset={activePreset}
            onRunAnalysis={executeAnalysis}
            mockupFile={mockupFile}
            setMockupFile={setMockupFile}
          />
        )}

        {/* Tab 3: Benchmark Lab */}
        {activeTab === 'benchmark' && <BenchmarkPage />}

        {/* Tab 4: Reference Contracts */}
        {activeTab === 'contracts' && (
          <ContractCard contracts={referenceData} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1E293B] py-4 bg-[#0B0F14] text-center text-xs font-mono text-forensicSlate">
        CX MIRROR &bull; HackStellar PS-18 &bull; Built on Google Antigravity v2.28+ &bull;
        "Your Design. Your Experience. Mathematically Verified."
      </footer>
    </div>
  );
}

