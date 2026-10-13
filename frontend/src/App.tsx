import React, { useState, useEffect } from 'react';
import { Sprout, RotateCcw, Volume2, Send, HelpCircle, MessageSquare } from 'lucide-react';
import type { Language, ConversationTurn, SystemStatus } from './types';
import { apiService } from './services/api';
import { LanguageSelector } from './components/LanguageSelector';
import { VoiceRecordButton } from './components/VoiceRecordButton';
import { ResponseCard } from './components/ResponseCard';
import { StatusBanner } from './components/StatusBanner';

export const App: React.FC = () => {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('hi');
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [autoPlayAudio, setAutoPlayAudio] = useState<boolean>(true);
  const [sessionId, setSessionId] = useState<string>(() => 'farmer_session_' + Math.random().toString(36).substring(2, 9));
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [textInput, setTextInput] = useState<string>('');

  useEffect(() => {
    // Initial fetch of language capabilities and local health
    apiService.getLanguages().then(setLanguages);
    apiService.getStatus().then(setStatus);
  }, []);

  const handleAudioRecorded = async (blob: Blob) => {
    setIsProcessing(true);
    try {
      const res = await apiService.sendVoiceQuery(blob, selectedLanguage, sessionId);
      if (res && res.status === 'success') {
        const newTurn: ConversationTurn = {
          id: String(Date.now()),
          timestamp: new Date().toLocaleTimeString(),
          query: res.query,
          answer: res.answer,
          language: res.language,
          sources: res.sources,
          audio_url: res.audio_url,
          metrics: res.metrics
        };
        setTurns((prev) => [newTurn, ...prev]);
      } else if (res && res.status === 'empty_input') {
        alert(res.answer || 'कोई आवाज़ सुनाई नहीं दी।');
      }
    } catch (err) {
      console.error('Voice query error:', err);
      alert('सर्वर त्रुटि: कृपया सुनिश्चित करें कि बैकएंड चल रहा है।');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendText = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!textInput.trim() || isProcessing) return;

    const query = textInput.trim();
    setTextInput('');
    setIsProcessing(true);

    try {
      const res = await apiService.sendTextQuery(query, selectedLanguage, sessionId);
      if (res && res.status === 'success') {
        const newTurn: ConversationTurn = {
          id: String(Date.now()),
          timestamp: new Date().toLocaleTimeString(),
          query: res.query,
          answer: res.answer,
          language: res.language,
          sources: res.sources,
          audio_url: res.audio_url,
          metrics: res.metrics
        };
        setTurns((prev) => [newTurn, ...prev]);
      }
    } catch (err) {
      console.error('Text query error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleResetConversation = async () => {
    try {
      await apiService.clearHistory(sessionId);
    } catch (e) {
      // ignore
    }
    setTurns([]);
    setSessionId('farmer_session_' + Math.random().toString(36).substring(2, 9));
  };

  const sampleQuestions: Record<string, string[]> = {
    hi: [
      "मेरी गेहूँ की फसल के पत्ते पीले हो रहे हैं, मुझे क्या करना चाहिए?",
      "प्रधानमंत्री किसान सम्मान निधि योजना की किस्त के नियम क्या हैं?",
      "नैनो यूरिया का सही छिड़काव कैसे करें?"
    ],
    mr: [
      "कापसावरील गुलाबी बोंडअळीचे नियंत्रण कसे करावे?",
      "सोयाबीनच्या पानांवर पिवळे चट्टे पडत आहेत, काय उपाय आहे?",
      "ठिबक सिंचन पद्धतीचे काय फायदे आहेत?"
    ],
    te: [
      "వరిలో కాండం తొలిచే పురుగు నివారణ చర్యలు ఏమిటి?"
    ],
    bn: [
      "আলুর নাবি ধসা রোগের প্রতিকার কি?"
    ]
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50/60 via-slate-50 to-emerald-100/30 text-slate-900 pb-16">
      {/* Header */}
      <header className="bg-emerald-800 text-white shadow-md sticky top-0 z-30">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-inner">
              <Sprout className="w-6 h-6 text-emerald-100" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">किसान आवाज़ (Kisan Vaani)</h1>
              <p className="text-xs text-emerald-200">ऑफ़लाइन भारतीय किसान AI आवाज़ सहायक</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setAutoPlayAudio(!autoPlayAudio)}
              className={`p-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer ${
                autoPlayAudio ? 'bg-emerald-700 text-white ring-1 ring-emerald-500' : 'bg-emerald-900/60 text-emerald-300'
              }`}
              title="स्वचालित आवाज़ बोलें (Auto-play Speech)"
            >
              <Volume2 className="w-4 h-4" />
              <span className="hidden sm:inline">आवाज़: {autoPlayAudio ? 'चालू' : 'बंद'}</span>
            </button>

            {turns.length > 0 && (
              <button
                type="button"
                onClick={handleResetConversation}
                className="p-2 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-xs font-semibold text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                title="नया सवाल पूछें (Ask Fresh Question)"
              >
                <RotateCcw className="w-4 h-4" />
                <span className="hidden sm:inline">नया सवाल</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-3xl mx-auto px-4 pt-6">
        {/* Offline Status */}
        <StatusBanner status={status} />

        {/* 1. Farmer Language Selection */}
        <LanguageSelector
          languages={languages}
          selectedLanguage={selectedLanguage}
          onSelectLanguage={setSelectedLanguage}
          disabled={isProcessing}
        />

        {/* 2. Large Central Voice Interaction */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-emerald-100 flex flex-col items-center mb-6">
          <VoiceRecordButton
            onAudioRecorded={handleAudioRecorded}
            isProcessing={isProcessing}
            selectedLanguage={selectedLanguage}
          />

          {/* Quick Example Questions */}
          <div className="w-full mt-2 pt-4 border-t border-slate-100">
            <span className="text-xs font-semibold text-slate-400 block mb-2 flex items-center gap-1">
              <HelpCircle className="w-3.5 h-3.5 text-emerald-600" />
              अक्सर पूछे जाने वाले सवाल (Click to Ask):
            </span>
            <div className="flex flex-col gap-1.5">
              {(sampleQuestions[selectedLanguage] || sampleQuestions['hi']).map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  disabled={isProcessing}
                  onClick={() => {
                    setTextInput(q);
                    setTimeout(() => handleSendText(), 50);
                  }}
                  className="text-left text-xs sm:text-sm bg-emerald-50/70 hover:bg-emerald-100/80 text-emerald-900 rounded-xl px-3.5 py-2 transition-colors cursor-pointer border border-emerald-200/50"
                >
                  🌾 {q}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Optional Text Input Fallback */}
        <div className="bg-white rounded-2xl p-2 px-3 shadow-sm border border-slate-200 flex items-center gap-2 mb-8">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendText()}
            placeholder="यदि चाहें तो यहाँ लिखकर भी पूछ सकते हैं..."
            className="flex-1 bg-transparent px-2 py-1 text-sm outline-none text-slate-800"
          />
          <button
            type="button"
            disabled={!textInput.trim() || isProcessing}
            onClick={() => handleSendText()}
            className="p-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-40 transition-colors cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* 3. Conversation & Response History */}
        {turns.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2 px-1">
              <h2 className="text-sm font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                <MessageSquare className="w-4 h-4 text-emerald-700" />
                बातचीत (Conversation History)
              </h2>
              <span className="text-xs text-slate-400">{turns.length} उत्तर</span>
            </div>

            {turns.map((turn) => (
              <ResponseCard key={turn.id} turn={turn} autoPlayAudio={autoPlayAudio} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
