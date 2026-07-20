'use client';

import React from 'react';
import { DollarSign, Zap, Activity, Database, TrendingUp } from 'lucide-react';
import { DashboardMetrics } from '@/types';

interface MetricCardsProps {
  metrics: DashboardMetrics | null;
}

export default function MetricCards({ metrics }: MetricCardsProps) {
  if (!metrics) return null;

  const cards = [
    {
      title: 'Total Spend Saved',
      value: `$${metrics.total_cost_saved_usd.toFixed(4)}`,
      subtext: `$${metrics.total_cost_spent_usd.toFixed(4)} total spend`,
      icon: DollarSign,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
    },
    {
      title: 'Cache Hit Rate',
      value: `${metrics.hit_rate_percentage.toFixed(1)}%`,
      subtext: `${metrics.cache_hits} hits / ${metrics.total_requests} requests`,
      icon: Zap,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
    },
    {
      title: 'Avg Latency Drop',
      value: `${metrics.avg_latency_hit_ms.toFixed(0)} ms`,
      subtext: `vs. ${metrics.avg_latency_miss_ms.toFixed(0)} ms on miss`,
      icon: Activity,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      border: 'border-cyan-500/20',
    },
    {
      title: 'Cached Vectors',
      value: metrics.cache_size_vectors.toLocaleString(),
      subtext: `${metrics.total_tokens_saved.toLocaleString()} tokens saved`,
      icon: Database,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => {
        const IconComponent = card.icon;
        return (
          <div
            key={idx}
            className={`p-5 rounded-xl border bg-slate-900/60 backdrop-blur-md ${card.border}`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-slate-400">{card.title}</span>
              <div className={`p-2 rounded-lg ${card.bg}`}>
                <IconComponent className={`w-5 h-5 ${card.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-100">{card.value}</div>
            <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-slate-500" />
              {card.subtext}
            </div>
          </div>
        );
      })}
    </div>
  );
}