'use client';

import React from 'react';
import { DollarSign, Zap, Activity, Database, ArrowUpRight } from 'lucide-react';
import { DashboardMetrics } from '@/types';

interface MetricCardsProps {
  metrics: DashboardMetrics | null;
}

export default function MetricCards({ metrics }: MetricCardsProps) {
  if (!metrics) return null;

  const cards = [
    {
      title: 'Cost Saved',
      value: `$${metrics.total_cost_saved_usd.toFixed(4)}`,
      subtext: `Spent: $${metrics.total_cost_spent_usd.toFixed(4)}`,
      icon: DollarSign,
      trend: '+12.3%',
    },
    {
      title: 'Cache Hit Rate',
      value: `${metrics.hit_rate_percentage.toFixed(1)}%`,
      subtext: `${metrics.cache_hits} of ${metrics.total_requests} requests`,
      icon: Zap,
      trend: 'Optimal',
    },
    {
      title: 'Avg Latency Drop',
      value: `${metrics.avg_latency_hit_ms.toFixed(0)} ms`,
      subtext: `vs ${metrics.avg_latency_miss_ms.toFixed(0)} ms miss`,
      icon: Activity,
      trend: '99.4% faster',
    },
    {
      title: 'Cached Vectors',
      value: metrics.cache_size_vectors.toLocaleString(),
      subtext: `${metrics.total_tokens_saved.toLocaleString()} tokens saved`,
      icon: Database,
      trend: 'Synced',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="group relative bg-zinc-900/40 hover:bg-zinc-900/80 border border-zinc-800/80 hover:border-zinc-700 transition-all rounded-lg p-4 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-zinc-400 tracking-wide uppercase">
                {card.title}
              </span>
              <div className="text-zinc-500 group-hover:text-zinc-300 transition-colors">
                <Icon className="w-4 h-4" />
              </div>
            </div>
            
            <div>
              <div className="text-2xl font-semibold font-mono tracking-tight text-zinc-100">
                {card.value}
              </div>
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-zinc-800/50 text-xs text-zinc-500">
                <span>{card.subtext}</span>
                <span className="font-mono text-[10px] text-zinc-400 bg-zinc-800/60 px-1.5 py-0.5 rounded">
                  {card.trend}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}