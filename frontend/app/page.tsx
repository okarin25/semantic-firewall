'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Shield, RefreshCw } from 'lucide-react';
import MetricCards from '@/components/MetricCards';
import LatencyChart from '@/components/LatencyChart';
import RequestFeed from '@/components/RequestFeed';
import DemoSandbox from '@/components/DemoSandbox';
import { getDashboardMetrics, getRecentLogs } from '@/lib/api';
import { DashboardMetrics, AuditLog } from '@/types';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshData = useCallback(async () => {
    try {
      const [m, l] = await Promise.all([
        getDashboardMetrics(),
        getRecentLogs(20),
      ]);
      setMetrics(m);
      setLogs(l);
    } catch (err) {
      console.error('Failed to poll analytics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 5000);
    return () => clearInterval(interval);
  }, [refreshData]);

  return (
    <div className="max-w-7xl mx-auto p-6 md:p-10">
      {/* Header Bar */}
      <header className="flex items-center justify-between pb-6 mb-8 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-600/20 border border-indigo-500/30 rounded-xl">
            <Shield className="w-7 h-7 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">Semantic Firewall</h1>
            <p className="text-xs text-slate-400">Next.js 15 + Tailwind CSS Observability Dashboard</p>
          </div>
        </div>
        <button
          onClick={refreshData}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Sync Data
        </button>
      </header>

      {/* KPI Cards */}
      <MetricCards metrics={metrics} />

      {/* Chart & Sandbox Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <LatencyChart metrics={metrics} />
        <DemoSandbox onPromptSent={refreshData} />
      </div>

      {/* Real-time Audit Stream */}
      <RequestFeed logs={logs} />
    </div>
  );
}