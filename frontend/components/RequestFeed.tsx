'use client';

import React from 'react';
import { ShieldCheck, ShieldAlert, Clock } from 'lucide-react';
import { AuditLog } from '@/types';

interface RequestFeedProps {
  logs: AuditLog[];
}

export default function RequestFeed({ logs }: RequestFeedProps) {
  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">Real-Time Audit Feed</h3>
          <p className="text-xs text-slate-400">Stream of intercepted API transactions and caching decisions.</p>
        </div>
        <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md">
          {logs.length} Transactions
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-800/50 text-xs uppercase text-slate-400 border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Prompt</th>
              <th className="py-3 px-4">Model</th>
              <th className="py-3 px-4">Similarity</th>
              <th className="py-3 px-4">Latency</th>
              <th className="py-3 px-4">Cost / Saved</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No transaction logs found. Send a prompt in the sandbox below to start testing.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.request_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4">
                    {log.cache_hit ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <ShieldCheck className="w-3.5 h-3.5" /> HIT
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        <ShieldAlert className="w-3.5 h-3.5" /> MISS
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 max-w-xs truncate font-mono text-xs text-slate-200">
                    {log.prompt_text}
                  </td>
                  <td className="py-3 px-4 text-xs text-slate-400">{log.model_requested}</td>
                  <td className="py-3 px-4 text-xs font-mono">
                    {log.similarity_score !== null ? (
                      <span className="text-emerald-400 font-semibold">
                        {(log.similarity_score * 100).toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-xs font-mono text-slate-300">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {log.latency_ms.toFixed(1)} ms
                    </span>
                  </td>
                  <td className="py-3 px-4 text-xs font-mono">
                    {log.cache_hit ? (
                      <span className="text-emerald-400">+${log.cost_saved_usd.toFixed(5)}</span>
                    ) : (
                      <span className="text-slate-400">-${log.cost_usd.toFixed(5)}</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}