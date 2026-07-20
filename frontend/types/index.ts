export interface DashboardMetrics {
  total_requests: number;
  cache_hits: number;
  cache_misses: number;
  hit_rate_percentage: number;
  total_cost_spent_usd: number;
  total_cost_saved_usd: number;
  avg_latency_hit_ms: number;
  avg_latency_miss_ms: number;
  cache_size_vectors: number;
  total_tokens_saved: number;
}

export interface AuditLog {
  request_id: string;
  prompt_text: string;
  model_requested: string;
  cache_hit: boolean;
  similarity_score: number | null;
  latency_ms: number;
  cost_usd: number;
  cost_saved_usd: number;
  created_at: string;
}

export interface ProxyResponseHeader {
  'x-firewall-cache-hit'?: string;
  'x-latency-ms'?: string;
  [key: string]: string | undefined;
}

export interface SendPromptResult {
  data: {
    choices?: Array<{
      message?: {
        content?: string;
      };
    }>;
  };
  headers: ProxyResponseHeader;
}