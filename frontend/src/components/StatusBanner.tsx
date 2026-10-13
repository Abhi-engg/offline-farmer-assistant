import React from 'react';
import { WifiOff, Cpu, Database } from 'lucide-react';
import type { SystemStatus } from '../types';

interface StatusBannerProps {
  status: SystemStatus | null;
}

export const StatusBanner: React.FC<StatusBannerProps> = ({ status }) => {
  return (
    <div className="w-full bg-slate-900/90 text-white rounded-2xl px-4 py-3 shadow-sm border border-slate-800 mb-6 flex flex-wrap items-center justify-between gap-3 text-xs">
      <div className="flex items-center gap-2">
        <span className="flex h-2.5 w-2.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <div className="flex items-center gap-1 font-semibold text-emerald-400">
          <WifiOff className="w-4 h-4 text-emerald-400" />
          <span>100% ऑफ़लाइन सक्षम (Offline Ready)</span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-slate-300">
        <div className="flex items-center gap-1.5" title="Local Inference Engine">
          <Cpu className="w-3.5 h-3.5 text-amber-400" />
          <span>
            मॉडल: <strong className="text-white">{status?.llm_engine || 'Local Grounded Engine'}</strong>
          </span>
        </div>

        <div className="flex items-center gap-1.5" title="Verified Agricultural Knowledge Documents">
          <Database className="w-3.5 h-3.5 text-blue-400" />
          <span>
            ज्ञानकोष: <strong className="text-white">{status?.knowledge_documents_count ?? 10} दस्तावेज़</strong>
          </span>
        </div>
      </div>
    </div>
  );
};
