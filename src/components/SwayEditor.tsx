import React, { useState } from 'react';
import { Download, Upload, Sparkles, Loader2, LayoutTemplate } from 'lucide-react';
import { fetchSwayConfig, applySwayConfig } from '../services/cloudRelay';
import { generateSwayConfig } from '../services/ai';
import { User } from 'firebase/auth';

interface SwayEditorProps {
  user: User | null;
  geminiKey: string;
  isConnected: boolean;
}

export const SwayEditor: React.FC<SwayEditorProps> = ({ user, geminiKey, isConnected }) => {
  const [config, setConfig] = useState('');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  const handleRead = async () => {
    if (!user) return setStatusMsg('Please sign in first.');
    if (!isConnected) return setStatusMsg('Device is disconnected. Cannot read config.');
    setIsLoading(true);
    setStatusMsg('Reading config from Cloud Relay...');
    try {
      const data = await fetchSwayConfig();
      setConfig(data);
      setStatusMsg('Config loaded successfully.');
    } catch (err: any) {
      setStatusMsg(err.message || 'Failed to read config.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApply = async () => {
    if (!user) return setStatusMsg('Please sign in first.');
    if (!isConnected) return setStatusMsg('Device is disconnected. Cannot apply config.');
    if (!config) return;
    setIsLoading(true);
    setStatusMsg('Applying config via Cloud Relay...');
    try {
      await applySwayConfig(config);
      setStatusMsg('Config applied and Sway reloaded!');
    } catch (err: any) {
      setStatusMsg(err.message || 'Failed to apply config.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAI = async () => {
    if (!geminiKey) return setStatusMsg('Please enter your Gemini API Key in the sidebar.');
    if (!config) return setStatusMsg('Please read the current config first.');
    if (!prompt) return setStatusMsg('Please enter an AI prompt.');
    
    setIsLoading(true);
    setStatusMsg('AI is generating new config...');
    try {
      const newConfig = await generateSwayConfig(geminiKey, config, prompt);
      setConfig(newConfig);
      setStatusMsg('AI generation complete. Review and apply!');
    } catch (err: any) {
      setStatusMsg(err.message || 'AI generation failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/40 backdrop-blur-3xl border border-purple-500/30 rounded-2xl overflow-hidden shadow-2xl relative">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <LayoutTemplate className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="font-semibold text-white tracking-wide">Sway Configurator</h2>
            <p className="text-xs text-neutral-400">Cloud Relay Active</p>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleRead}
            disabled={isLoading}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-all border border-white/10"
          >
            {isLoading && statusMsg.includes('Reading') ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Read Config
          </button>
          <button
            onClick={handleApply}
            disabled={isLoading || !config}
            className="flex items-center gap-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 disabled:opacity-50 text-sm font-medium px-4 py-2 rounded-lg transition-all border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]"
          >
            {isLoading && statusMsg.includes('Applying') ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            Apply Changes
          </button>
        </div>
      </div>

      {/* AI Prompt Area */}
      <div className="p-4 bg-gradient-to-b from-white/5 to-transparent border-b border-white/10">
        <div className="flex flex-col gap-3 bg-black/50 border border-white/10 rounded-xl p-3 focus-within:border-purple-500/50 focus-within:ring-1 focus-within:ring-purple-500/50 transition-all">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want to change (e.g., 'Change the background color to solid black and set terminal to alacritty')"
            className="w-full bg-transparent border-none text-sm text-white focus:outline-none placeholder:text-neutral-600 min-h-[60px] resize-none"
          />
          <div className="flex justify-end">
            <button
              onClick={handleAI}
              disabled={isLoading || !config || !prompt}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-all shadow-[0_0_20px_rgba(147,51,234,0.3)]"
            >
              {isLoading && statusMsg.includes('AI') ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Generate
            </button>
          </div>
        </div>
        {statusMsg && (
          <p className="text-xs text-purple-300 mt-3 flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-pulse"></span>
            {statusMsg}
          </p>
        )}
      </div>

      {/* Editor Area */}
      <div className="flex-1 p-4 overflow-hidden bg-[#0A0A0A]">
        <textarea
          value={config}
          onChange={(e) => setConfig(e.target.value)}
          className="w-full h-full bg-transparent border-none font-mono text-[13px] leading-relaxed text-neutral-300 focus:outline-none resize-none"
          placeholder="Sway config will appear here..."
          spellCheck="false"
        />
      </div>
    </div>
  );
};
