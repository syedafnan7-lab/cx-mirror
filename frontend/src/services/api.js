/**
 * CX MIRROR — Frontend API Service
 */

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchPresets() {
  const res = await fetch(`${API_BASE}/presets`);
  if (!res.ok) throw new Error('Failed to load presets');
  return res.json();
}

export async function fetchReferenceData() {
  const res = await fetch(`${API_BASE}/reference-data`);
  if (!res.ok) throw new Error('Failed to load reference contracts');
  return res.json();
}

export async function fetchROCBenchmark(seed = 42) {
  const res = await fetch(`${API_BASE}/roc-benchmark?seed=${seed}`);
  if (!res.ok) throw new Error('Failed to run ROC benchmark');
  return res.json();
}

export async function runAnalysis({
  mockupFile,
  targetUrl,
  preset = 'clean',
  threshold = 95.0,
  referenceData
}) {
  const formData = new FormData();
  if (mockupFile) {
    formData.append('mockup', mockupFile);
  }
  formData.append('target_url', targetUrl || `http://127.0.0.1:8000/sandbox?preset=${preset}`);
  formData.append('preset', preset);
  formData.append('threshold', threshold.toString());
  if (referenceData) {
    formData.append('reference_data', typeof referenceData === 'string' ? referenceData : JSON.stringify(referenceData));
  }

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis failed with status ${res.status}`);
  }

  return res.json();
}

