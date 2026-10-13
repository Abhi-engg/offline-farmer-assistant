import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2, Sparkles } from 'lucide-react';

interface VoiceRecordButtonProps {
  onAudioRecorded: (blob: Blob) => void;
  isProcessing: boolean;
  selectedLanguage: string;
}

export const VoiceRecordButton: React.FC<VoiceRecordButtonProps> = ({
  onAudioRecorded,
  isProcessing,
  selectedLanguage
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordDuration, setRecordDuration] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRecording = async () => {
    audioChunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        onAudioRecorded(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordDuration(0);

      timerRef.current = window.setInterval(() => {
        setRecordDuration((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('Microphone access error:', err);
      alert('माइक्रोफ़ोन की अनुमति नहीं मिली। कृपया ब्राउज़र सेटिंग्स में माइक्रोफ़ोन की अनुमति दें।');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const getPromptText = () => {
    if (isProcessing) return 'उत्तर तैयार हो रहा है... (AI is reasoning)';
    if (isRecording) return `बोलिए, हम सुन रहे हैं... (${formatTime(recordDuration)})`;
    switch (selectedLanguage) {
      case 'mr':
        return 'माईक दाबा आणि प्रश्न विचारा';
      case 'te':
        return 'మైక్ నొక్కండి మరియు ప్రశ్న అడగండి';
      case 'bn':
        return 'মাইক টিপে আপনার প্রশ্ন করুন';
      default:
        return 'माइक दबाकर अपना सवाल पूछें';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center my-6">
      <div className="relative flex items-center justify-center">
        {/* Pulsing indicator when recording */}
        {isRecording && (
          <div className="absolute w-36 h-36 rounded-full bg-red-500/30 recording-pulse" />
        )}

        {/* Central Giant Microphone Button */}
        <button
          type="button"
          disabled={isProcessing}
          onClick={isRecording ? stopRecording : startRecording}
          className={`relative z-10 w-28 h-28 sm:w-32 sm:h-32 rounded-full flex flex-col items-center justify-center shadow-xl transition-all duration-300 transform active:scale-95 cursor-pointer ${
            isProcessing
              ? 'bg-amber-500 text-white shadow-amber-500/30 ring-8 ring-amber-100 cursor-wait'
              : isRecording
              ? 'bg-red-600 text-white shadow-red-600/40 ring-8 ring-red-100 scale-105'
              : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-700/30 ring-8 ring-emerald-100/80 hover:ring-emerald-200'
          }`}
          title={isRecording ? 'रोकें (Stop)' : 'बोलें (Speak)'}
        >
          {isProcessing ? (
            <Loader2 className="w-12 h-12 animate-spin" />
          ) : isRecording ? (
            <Square className="w-10 h-10 fill-current" />
          ) : (
            <Mic className="w-12 h-12 stroke-[2.5]" />
          )}

          <span className="text-xs font-semibold uppercase tracking-wider mt-1.5">
            {isProcessing ? 'सोच रहे हैं' : isRecording ? 'रोकें' : 'बोलें'}
          </span>
        </button>
      </div>

      {/* Clear instruction label */}
      <div className="mt-4 flex items-center gap-2 text-center">
        {!isProcessing && !isRecording && (
          <Sparkles className="w-5 h-5 text-emerald-600 animate-pulse" />
        )}
        <p
          className={`text-base sm:text-lg font-medium ${
            isRecording ? 'text-red-600 font-bold' : isProcessing ? 'text-amber-700' : 'text-slate-800'
          }`}
        >
          {getPromptText()}
        </p>
      </div>
    </div>
  );
};
