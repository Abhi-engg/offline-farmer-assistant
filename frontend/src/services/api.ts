import type { Language, SystemStatus } from '../types';

const API_BASE = '/api';

export const apiService = {
  async getLanguages(): Promise<Language[]> {
    try {
      const res = await fetch(`${API_BASE}/languages`);
      const data = await res.json();
      return data.languages || [];
    } catch (e) {
      console.error('Failed to fetch languages:', e);
      return [
        { code: 'hi', name: 'Hindi', native_name: 'हिन्दी', status: 'ready', regions: 'UP, MP, Bihar' },
        { code: 'mr', name: 'Marathi', native_name: 'मराठी', status: 'ready', regions: 'Maharashtra' },
        { code: 'te', name: 'Telugu', native_name: 'తెలుగు', status: 'ready', regions: 'AP, Telangana' },
        { code: 'bn', name: 'Bengali', native_name: 'বাংলা', status: 'ready', regions: 'West Bengal' }
      ];
    }
  },

  async getStatus(): Promise<SystemStatus> {
    try {
      const res = await fetch(`${API_BASE}/status`);
      return await res.json();
    } catch (e) {
      return {
        status: 'offline',
        offline_ready: true,
        asr_ready: true,
        llm_engine: 'local_grounded_rag_engine',
        ollama_connected: false,
        knowledge_documents_count: 10,
        tts_ready: true
      };
    }
  },

  async sendVoiceQuery(audioBlob: Blob, language: string, sessionId?: string) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'farmer_voice.webm');
    formData.append('language', language);
    if (sessionId) formData.append('session_id', sessionId);

    const res = await fetch(`${API_BASE}/chat/voice`, {
      method: 'POST',
      body: formData
    });
    return await res.json();
  },

  async sendTextQuery(query: string, language: string, sessionId?: string) {
    const res = await fetch(`${API_BASE}/chat/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, language, session_id: sessionId })
    });
    return await res.json();
  },

  async clearHistory(sessionId: string) {
    const res = await fetch(`${API_BASE}/history/${sessionId}`, {
      method: 'DELETE'
    });
    return await res.json();
  }
};
