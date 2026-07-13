import React from 'react';
import { Key } from 'lucide-react';
import { User } from 'firebase/auth';

interface SidebarProps {
  user: User | null;
  geminiKey: string;
  setGeminiKey: (key: string) => void;
  isConnected: boolean;
  isChecking: boolean;
  onCheckConnection: () => void;
  debugMsg?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ geminiKey, setGeminiKey }) => {

  return (
    <div className="w-full lg:w-80 h-auto lg:h-full flex flex-col shrink-0 bg-white/5 border-l border-white/10 backdrop-blur-xl">

      {/* Settings Section */}
      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <Key className="w-5 h-5 text-blue-400" />
          <h2 className="font-semibold text-white tracking-wide">AI Configuration</h2>
        </div>
        <p className="text-xs text-neutral-400 mb-3">
          Enter your Gemini API key to enable AI-powered Sway configuration. This key is stored securely in your browser.
        </p>
        <input 
          type="password" 
          value={geminiKey}
          onChange={(e) => setGeminiKey(e.target.value)}
          placeholder="AIzaSy..."
          className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-neutral-600"
        />
      </div>

    </div>
  );
};
