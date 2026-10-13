export interface Language {
  code: string;
  name: string;
  native_name: string;
  status: string;
  regions: string;
}

export interface ConversationTurn {
  id: string;
  timestamp: string;
  query: string;
  answer: string;
  language: string;
  sources?: string[];
  audio_url?: string;
  metrics?: {
    asr_latency?: number;
    rag_latency?: number;
    llm_latency?: number;
    tts_latency?: number;
    total_latency?: number;
  };
}

export interface SystemStatus {
  status: string;
  offline_ready: boolean;
  asr_ready: boolean;
  llm_engine: string;
  ollama_connected: boolean;
  knowledge_documents_count: number;
  tts_ready: boolean;
}
