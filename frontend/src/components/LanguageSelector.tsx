import React from 'react';
import { Languages, Check } from 'lucide-react';
import type { Language } from '../types';

interface LanguageSelectorProps {
  languages: Language[];
  selectedLanguage: string;
  onSelectLanguage: (code: string) => void;
  disabled?: boolean;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  languages,
  selectedLanguage,
  onSelectLanguage,
  disabled
}) => {
  return (
    <div className="w-full bg-white/90 backdrop-blur-md rounded-2xl p-4 shadow-sm border border-emerald-100 mb-6">
      <div className="flex items-center gap-2 mb-3 text-emerald-900 font-semibold text-lg">
        <Languages className="w-6 h-6 text-emerald-700" />
        <span>अपनी भाषा चुनें / आपली भाषा निवडा (Select Language)</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {languages.map((lang) => {
          const isSelected = selectedLanguage === lang.code;
          return (
            <button
              key={lang.code}
              type="button"
              disabled={disabled}
              onClick={() => onSelectLanguage(lang.code)}
              className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
                isSelected
                  ? 'border-emerald-600 bg-emerald-50 text-emerald-950 shadow-md ring-2 ring-emerald-500/20'
                  : 'border-slate-200 bg-white hover:border-emerald-300 text-slate-700 hover:bg-slate-50'
              } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-bold tracking-wide">{lang.native_name}</span>
                {isSelected && <Check className="w-5 h-5 text-emerald-600 stroke-[3]" />}
              </div>
              <span className="text-xs text-slate-500 mt-0.5">{lang.name}</span>
              <span className="text-[10px] text-slate-400 text-center truncate max-w-full px-1">
                {lang.regions.split(',')[0]}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
