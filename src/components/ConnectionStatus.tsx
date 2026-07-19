import React from 'react';
import { Activity, Wifi, WifiOff, RefreshCw } from 'lucide-react';

interface ConnectionStatusProps {
  isConnected: boolean;
  isChecking: boolean;
  onCheckConnection: () => void;
  debugMsg?: string;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ isConnected, isChecking, onCheckConnection, debugMsg }) => {
  return (
    <div className="flex items-center gap-4 bg-white/5 border border-purple-500/30 rounded-xl p-3 backdrop-blur-md">
      <div className="flex items-center gap-2">
        {isConnected ? (
          <Wifi className="w-5 h-5 text-emerald-400" />
        ) : (
          <WifiOff className="w-5 h-5 text-rose-500" />
        )}
        <div className="flex flex-col">
          <span className="text-sm font-medium text-white leading-tight">
            {isConnected ? 'Cloud Relay Connected' : 'Disconnected'}
          </span>
          <span className="text-[10px] text-neutral-400">
            {isConnected ? 'Syncing active' : 'Run tablet_agent.py on tablet'}
          </span>
        </div>
      </div>

      <div className="w-px h-8 bg-white/10 mx-2"></div>

      <button 
        onClick={onCheckConnection} 
        disabled={isChecking}
        title="Ping Device"
        className="p-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
      >
        <RefreshCw className={`w-4 h-4 text-neutral-400 ${isChecking ? 'animate-spin' : ''}`} />
      </button>

      {/* Optional: Show debug message in a tooltip or small text if needed, but since it's in the header, maybe keep it minimal */}
      {/* {debugMsg && (
        <div className="hidden group-hover:block absolute top-full right-0 mt-2 w-64 text-[10px] font-mono text-neutral-500 break-words bg-black/90 border border-white/10 p-2 rounded z-50">
          {debugMsg}
        </div>
      )} */}
    </div>
  );
};
