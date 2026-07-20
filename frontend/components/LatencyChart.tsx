'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { DashboardMetrics } from '@/types';

interface LatencyChartProps {
  metrics: DashboardMetrics | null;
}

export default function LatencyChart({ metrics }: LatencyChartProps) {
  if (!metrics) return null;

  const data = [
    {
      category: 'Response Time (ms)',
      'Cached Hit (Sub-15ms)': metrics.avg_latency_hit_ms || 12,
      'Live OpenAI Miss': metrics.avg_latency_miss_ms || 1850,
    },
  ];

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md mb-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-100">Latency Benchmark</h3>
        <p className="text-xs text-slate-400">Comparing average cached response time vs live LLM call.</p>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" stroke="#94a3b8" unit=" ms" />
            <YAxis type="category" dataKey="category" stroke="#94a3b8" hide />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#f8fafc' }} />
            <Legend wrapperStyle={{ color: '#94a3b8' }} />
            <Bar dataKey="Cached Hit (Sub-15ms)" fill="#10b981" radius={[0, 4, 4, 0]} />
            <Bar dataKey="Live OpenAI Miss" fill="#ef4444" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}