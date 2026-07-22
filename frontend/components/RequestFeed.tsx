'use client';

import React from 'react';
import { Terminal, Activity } from 'lucide-react';
import { AuditLog } from '@/types';

interface RequestFeedProps {
  logs: AuditLog[];
}

export default function RequestFeed({ logs }: RequestFeedProps) {
  return (
    <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-medium text-zinc-200 tracking-tight">Real-time Audit Stream</h3>
        </div>
        <span className="text-[11px] font-mono text-zinc-500">Live Proxy Events</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-500">
              <th className="pb-3 font-medium">Timestamp</th>
              <th className="pb-3 font-medium">Prompt</th>
              <th className="pb-3 font-medium">Provider</th>
              <th className="pb-3 font-medium">Cache Status</th>
              <th className="pb-3 font-medium text-right">Latency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-900">
            {logs && logs.length > 0 ? (
              logs.map((log, index) => (
                <tr key={index} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="py-3 text-zinc-400 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-3 text-zinc-200 max-w-xs truncate" title={log.prompt_text}>
                    {log.prompt_text}
                  </td>
                  <td className="py-3 text-zinc-400 uppercase">{log.provider}</td>
                  <td className="py-3">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                        log.cache_hit
                          ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-900/50'
                          : 'bg-amber-950/60 text-amber-400 border border-amber-900/50'
                      }`}
                    >
                      {log.cache_hit ? 'HIT' : 'MISS'}
                    </span>
                  </td>
                  <td className="py-3 text-right text-zinc-400">{log.latency_ms}ms</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="py-6 text-center text-zinc-500">
                  No request logs recorded yet. Send a test prompt above to populate the feed.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}