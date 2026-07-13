import React from 'react';
import { Key, ShieldAlert, LogOut } from 'lucide-react';
import { auth } from '../firebase';
import { signOut, User } from 'firebase/auth';

interface SidebarProps {
  user: User | null;
  geminiKey: string;
  setGeminiKey: (key: string) => void;
  isConnected: boolean;
  isChecking: boolean;
  onCheckConnection: () => void;
  debugMsg?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, geminiKey, setGeminiKey, isConnected, isChecking, onCheckConnection, debugMsg }) => {


  const logout = () => signOut(auth);

  return (
    <div className="w-full lg:w-80 h-auto lg:h-full flex flex-col shrink-0 bg-white/5 border-l border-white/10 backdrop-blur-xl">
      
      {/* Auth Section */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3 mb-4">
          <ShieldAlert className="w-5 h-5 text-purple-400" />
          <h2 className="font-semibold text-white tracking-wide">Access Control</h2>
        </div>
        
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/10">
            {user?.photoURL && (
              <img src={user.photoURL} alt="Profile" className="w-8 h-8 rounded-full border border-white/20" />
            )}
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium text-white truncate">{user?.displayName}</p>
              <p className="text-xs text-neutral-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 py-2 rounded-lg transition-all duration-300 border border-red-500/20"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </div>



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
