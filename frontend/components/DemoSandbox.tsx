'use client';

import React, { useState } from 'react';
import { Send, Terminal, Sparkles, AlertCircle } from 'lucide-react';
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
    <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" /> Interactive Proxy Sandbox
        </h3>
        <p className="text-xs text-slate-400">
          Fire live prompts to test semantic caching. Try similar phrasing to trigger a sub-15ms cache hit!
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {samplePrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => setPrompt(p)}
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
          >
            "{p}"
          </button>
        ))}
      </div>

      <form onSubmit={handleSend} className="flex gap-2 mb-4">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Type an enterprise prompt..."
          className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-lg text-sm flex items-center gap-2 transition-colors disabled:opacity-50"
        >
          {loading ? 'Processing...' : <><Send className="w-4 h-4" /> Execute</>}
        </button>
      </form>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-xs flex items-center gap-2 mb-4">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {result && (
        <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs text-slate-300">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <span className="flex items-center gap-2 font-semibold text-slate-200">
              <Terminal className="w-4 h-4 text-emerald-400" /> Proxy Execution Headers
            </span>
            <div className="flex gap-3">
              <span className="text-slate-400">
                Cache Hit:{' '}
                <strong className={result.headers['x-firewall-cache-hit'] === 'true' ? 'text-emerald-400' : 'text-amber-400'}>
                  {result.headers['x-firewall-cache-hit'] || 'false'}
                </strong>
              </span>
              <span className="text-slate-400">
                Latency: <strong className="text-cyan-400">{result.headers['x-latency-ms']} ms</strong>
              </span>
            </div>
          </div>
          <p className="text-slate-300 whitespace-pre-wrap">
            {result.data.choices?.[0]?.message?.content}
          </p>
        </div>
      )}
    </div>
  );
}