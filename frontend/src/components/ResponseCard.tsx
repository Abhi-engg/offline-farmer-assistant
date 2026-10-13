import React, { useRef, useState, useEffect } from 'react';
import { Volume2, VolumeX, BookOpen, Clock, User, Bot, AlertTriangle, ThumbsUp, ThumbsDown, Check } from 'lucide-react';
import type { ConversationTurn } from '../types';
import { apiService } from '../services/api';

interface ResponseCardProps {
  turn: ConversationTurn;
  autoPlayAudio?: boolean;
}

export const ResponseCard: React.FC<ResponseCardProps> = ({ turn, autoPlayAudio = true }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<'helpful' | 'unhelpful' | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleFeedback = (rating: 'helpful' | 'unhelpful') => {
    setFeedbackGiven(rating);
    apiService.sendFeedback(turn.query, turn.language || 'hi', rating);
  };

  useEffect(() => {
    if (turn.audio_url && autoPlayAudio) {
      playAudio();
    }
  }, [turn.audio_url]);

  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current
        .play()
        .then(() => setIsPlaying(true))
        .catch((err) => console.log('Audio autoplay prevented or error:', err));
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return (
    <div className="w-full bg-white rounded-3xl p-6 shadow-md border border-emerald-100/80 mb-6 transition-all duration-300">
      {/* Hidden Audio Element */}
      {turn.audio_url && (
        <audio
          ref={audioRef}
          src={turn.audio_url}
          onEnded={() => setIsPlaying(false)}
          onError={() => setIsPlaying(false)}
        />
      )}

      {/* Farmer Query Section */}
      <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
        <div className="p-2.5 rounded-2xl bg-amber-100 text-amber-800 shrink-0">
          <User className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
            किसान का सवाल (Farmer's Question)
          </span>
          <p className="text-lg font-medium text-slate-800 mt-0.5 leading-snug">{turn.query}</p>
        </div>
      </div>

      {/* AI Assistant Answer Section */}
      <div className="flex items-start gap-3.5 pt-4">
        <div className="p-2.5 rounded-2xl bg-emerald-100 text-emerald-800 shrink-0 mt-1">
          <Bot className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">
              सहायक का जवाब (AI Assistant Response)
            </span>

            {/* Audio Controls */}
            {turn.audio_url && (
              <div className="flex items-center gap-2">
                {isPlaying ? (
                  <button
                    type="button"
                    onClick={stopAudio}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-100 text-red-700 hover:bg-red-200 text-xs font-bold transition-colors cursor-pointer"
                  >
                    <VolumeX className="w-4 h-4" />
                    <span>आवाज़ रोकें (Stop)</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={playAudio}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-600 text-white hover:bg-emerald-700 text-xs font-bold shadow-sm transition-colors cursor-pointer"
                  >
                    <Volume2 className="w-4 h-4" />
                    <span>पुनः सुनें (Replay)</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Formatted Answer Text */}
          <div className="text-base sm:text-lg text-slate-800 mt-2.5 leading-relaxed whitespace-pre-line font-normal">
            {turn.answer}
          </div>

          {/* Sources / Agricultural Grounding */}
          {turn.sources && turn.sources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
                प्रमाणित स्रोत (Verified Source):
              </span>
              {turn.sources.map((src, i) => (
                <span
                  key={i}
                  className="inline-block bg-emerald-50 text-emerald-800 text-xs px-2.5 py-1 rounded-lg border border-emerald-200/60 font-medium"
                >
                  {src}
                </span>
              ))}
            </div>
          )}

          {/* Offline Agricultural Safety Disclaimer */}
          <div className="mt-3.5 flex items-start gap-1.5 text-xs text-amber-800/80 bg-amber-50/60 rounded-xl p-2.5 border border-amber-200/50">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p>
              यह सलाह ऑफ़लाइन कृषि ज्ञानकोष पर आधारित है। रासायनिक छिड़काव या गंभीर नुकसान की स्थिति में नजदीकी कृषि विज्ञान केंद्र (KVK) के विशेषज्ञ से अवश्य परामर्श करें।
            </p>
          </div>

          {/* Farmer Feedback & Quality Rating */}
          <div className="mt-3.5 flex items-center justify-between pt-2.5 border-t border-slate-100/80">
            <span className="text-xs text-slate-500 font-medium">क्या यह सलाह उपयोगी थी? (Helpful?)</span>
            {feedbackGiven ? (
              <span className="inline-flex items-center gap-1 text-xs text-emerald-600 font-medium bg-emerald-50 px-2 py-0.5 rounded-md">
                <Check className="w-3.5 h-3.5" /> धन्यवाद, प्रतिक्रिया दर्ज हुई
              </span>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleFeedback('helpful')}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs text-slate-600 hover:text-emerald-700 bg-slate-50 hover:bg-emerald-50 rounded-lg transition-colors border border-slate-200/60 font-medium"
                  title="मददगार रहा"
                >
                  <ThumbsUp className="w-3.5 h-3.5" /> हाँ (Yes)
                </button>
                <button
                  onClick={() => handleFeedback('unhelpful')}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs text-slate-600 hover:text-rose-700 bg-slate-50 hover:bg-rose-50 rounded-lg transition-colors border border-slate-200/60 font-medium"
                  title="सुधार की जरूरत"
                >
                  <ThumbsDown className="w-3.5 h-3.5" /> नहीं (No)
                </button>
              </div>
            )}
          </div>

          {/* Pipeline Latency Metrics */}
          {turn.metrics && (
            <div className="mt-3 flex items-center gap-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                कुल समय: {turn.metrics.total_latency}s
              </span>
              {turn.metrics.asr_latency !== undefined && (
                <span>• ASR: {turn.metrics.asr_latency}s</span>
              )}
              {turn.metrics.rag_latency !== undefined && (
                <span>• RAG: {turn.metrics.rag_latency}s</span>
              )}
              {turn.metrics.tts_latency !== undefined && (
                <span>• TTS: {turn.metrics.tts_latency}s</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
