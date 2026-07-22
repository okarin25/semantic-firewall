import axios from 'axios';
import { DashboardMetrics, AuditLog, SendPromptResult } from '@/types';

const client = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const response = await client.get<DashboardMetrics>('/api/analytics/dashboard');
  return response.data;
};

export const getRecentLogs = async (limit: number = 50): Promise<AuditLog[]> => {
  const response = await client.get<AuditLog[]>(`/api/analytics/logs?limit=${limit}`);
  return response.data;
};

export const sendTestPrompt = async (promptText: string): Promise<SendPromptResult> => {
  const payload = {
    provider: 'groq',
    model: 'llama-3.3-70b-versatile',
    messages: [{ role: 'user', content: promptText }],
    user_id: 'nextjs-sandbox-user',
    session_id: 'sandbox-session-01',
  };

  const response = await client.post('/v1/chat/completions', payload);
  return {
    data: response.data,
    headers: response.headers as SendPromptResult['headers'],
  };
};