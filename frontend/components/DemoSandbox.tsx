'use client';

import React, { useState } from 'react';
import { Send, Terminal, Sparkles, AlertCircle, CornerDownLeft } from 'lucide-react';
import { sendTestPrompt } from '@/lib/api';
import { SendPromptResult } from '@/types';

interface DemoSandboxProps {
  onPromptSent?: () => void;
}

export default function DemoSandbox({ onPromptSent }: DemoSandboxProps) {
  const [prompt, setPrompt] = useState('How do I request PTO or time off in Workday?');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SendPromptResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const samplePrompts = [
    'How do I request PTO or time off in Workday?',
    'What is the procedure for booking vacation days in Workday?',
    'How do I setup global VPN access on my laptop?',
    'What is the corporate Wi-Fi password?',
  ];

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!prompt.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await sendTestPrompt(prompt);
      setResult(res);
      if (onPromptSent) onPromptSent();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to communicate with proxy.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-5 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <h3 className="text-sm font-medium text-zinc-200 tracking-tight">Interactive Proxy Workbench</h3>
          </div>
          <span className="text-[11px] font-mono text-zinc-500">POST /v1/chat/completions</span>
        </div>
        <p className="text-xs text-zinc-400 mb-4">
          Test semantic retrieval live. Reusing similar intent triggers sub-15ms cache lookups.
        </p>

        <div className="flex flex-wrap gap-1.5 mb-4">
          {samplePrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => setPrompt(p)}
              className="text-[11px] bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 px-2.5 py-1 rounded border border-zinc-800 transition-colors text-left"
            >
              "{p}"
            </button>
          ))}
        </div>

        <form onSubmit={handleSend} className="relative mb-4">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Send a test prompt..."
            className="w-full bg-zinc-950 border border-zinc-800 focus:border-zinc-600 rounded-lg pl-3 pr-12 py-2.5 text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none transition-colors font-mono"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute right-1.5 top-1.5 bottom-1.5 px-3 bg-zinc-100 hover:bg-white text-zinc-950 font-medium rounded text-xs flex items-center gap-1.5 transition-colors disabled:opacity-50 cursor-pointer"
          >
            {loading ? '...' : <><CornerDownLeft className="w-3.5 h-3.5" /></>}
          </button>
        </form>

        {error && (
          <div className="p-3 bg-red-950/30 border border-red-900/50 text-red-400 rounded-lg text-xs flex items-center gap-2 mb-4 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}
      </div>

      {result && (
        <div className="bg-zinc-950 border border-zinc-800/80 rounded-lg p-3.5 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-zinc-900 pb-2 mb-2.5 text-[11px]">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-zinc-500" /> Response Headers
            </span>
            <div className="flex gap-3">
              <span>
                Hit:{' '}
                <strong className={result.headers['x-firewall-cache-hit'] === 'true' ? 'text-emerald-400' : 'text-amber-400'}>
                  {result.headers['x-firewall-cache-hit'] || 'false'}
                </strong>
              </span>
              <span className="text-zinc-400">
                {result.headers['x-latency-ms']}ms
              </span>
            </div>
          </div>
          <p className="text-zinc-300 whitespace-pre-wrap leading-relaxed text-[11px]">
            {result.data.choices?.[0]?.message?.content}
          </p>
        </div>
      )}
    </div>
  );
}