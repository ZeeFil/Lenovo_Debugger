import os

# 1. Update Sidebar.tsx
sidebar_path = '/home/zfil/Lenovo_Debugger/src/components/Sidebar.tsx'
with open(sidebar_path, 'r') as f:
    sidebar_content = f.read()

sidebar_imports_old = """import { Key, ShieldAlert, LogOut, Github } from 'lucide-react';"""
sidebar_imports_new = """import { Key, ShieldAlert, LogOut, Github, Activity, Wifi, WifiOff } from 'lucide-react';"""
sidebar_content = sidebar_content.replace(sidebar_imports_old, sidebar_imports_new)

sidebar_props_old = """interface SidebarProps {
  user: User | null;
  geminiKey: string;
  setGeminiKey: (key: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, geminiKey, setGeminiKey }) => {"""
sidebar_props_new = """interface SidebarProps {
  user: User | null;
  geminiKey: string;
  setGeminiKey: (key: string) => void;
  isConnected: boolean;
  isChecking: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, geminiKey, setGeminiKey, isConnected, isChecking }) => {"""
sidebar_content = sidebar_content.replace(sidebar_props_old, sidebar_props_new)

sidebar_settings_old = """      {/* Settings Section */}
      <div className="p-6">"""
sidebar_settings_new = """      {/* Connection Status Section */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-5 h-5 text-emerald-400" />
          <h2 className="font-semibold text-white tracking-wide">Cloud Relay</h2>
        </div>
        
        <div className="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/10">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-black/40">
            {isChecking ? (
              <div className="w-4 h-4 rounded-full border-2 border-yellow-500/30 border-t-yellow-500 animate-spin" />
            ) : isConnected ? (
              <>
                <Wifi className="w-4 h-4 text-emerald-500 relative z-10" />
                <div className="absolute inset-0 bg-emerald-500/20 rounded-full animate-ping" />
              </>
            ) : (
              <WifiOff className="w-4 h-4 text-red-500" />
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">
              {isChecking ? 'Pinging device...' : isConnected ? 'Connected (Listening)' : 'Disconnected'}
            </p>
            <p className="text-xs text-neutral-400">
              {isConnected ? 'Tablet agent is running' : 'Run agent.py on tablet'}
            </p>
          </div>
        </div>
      </div>

      {/* Settings Section */}
      <div className="p-6">"""
sidebar_content = sidebar_content.replace(sidebar_settings_old, sidebar_settings_new)

with open(sidebar_path, 'w') as f:
    f.write(sidebar_content)


# 2. Update SwayEditor.tsx
editor_path = '/home/zfil/Lenovo_Debugger/src/components/SwayEditor.tsx'
with open(editor_path, 'r') as f:
    editor_content = f.read()

editor_props_old = """interface SwayEditorProps {
  user: User | null;
  geminiKey: string;
}

export const SwayEditor: React.FC<SwayEditorProps> = ({ user, geminiKey }) => {"""
editor_props_new = """interface SwayEditorProps {
  user: User | null;
  geminiKey: string;
  isConnected: boolean;
}

export const SwayEditor: React.FC<SwayEditorProps> = ({ user, geminiKey, isConnected }) => {"""
editor_content = editor_content.replace(editor_props_old, editor_props_new)

editor_read_old = """  const handleRead = async () => {
    if (!user) return setStatusMsg('Please sign in first.');"""
editor_read_new = """  const handleRead = async () => {
    if (!user) return setStatusMsg('Please sign in first.');
    if (!isConnected) return setStatusMsg('Device is disconnected. Cannot read config.');"""
editor_content = editor_content.replace(editor_read_old, editor_read_new)

editor_apply_old = """  const handleApply = async () => {
    if (!user) return setStatusMsg('Please sign in first.');
    if (!config) return;"""
editor_apply_new = """  const handleApply = async () => {
    if (!user) return setStatusMsg('Please sign in first.');
    if (!isConnected) return setStatusMsg('Device is disconnected. Cannot apply config.');
    if (!config) return;"""
editor_content = editor_content.replace(editor_apply_old, editor_apply_new)

with open(editor_path, 'w') as f:
    f.write(editor_content)


# 3. Update App.tsx
app_path = '/home/zfil/Lenovo_Debugger/src/App.tsx'
with open(app_path, 'r') as f:
    app_content = f.read()

app_imports_old = """import { Sidebar } from './components/Sidebar';
import { SwayEditor } from './components/SwayEditor';"""
app_imports_new = """import { Sidebar } from './components/Sidebar';
import { SwayEditor } from './components/SwayEditor';
import { pingDevice } from './services/cloudRelay';"""
app_content = app_content.replace(app_imports_old, app_imports_new)

app_state_old = """  const [user, setUser] = useState<User | null>(null);
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [isInitializing, setIsInitializing] = useState(true);"""
app_state_new = """  const [user, setUser] = useState<User | null>(null);
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [isInitializing, setIsInitializing] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);"""
app_content = app_content.replace(app_state_old, app_state_new)

app_effect_old = """  useEffect(() => {
    localStorage.setItem('gemini_api_key', geminiKey);
  }, [geminiKey]);"""
app_effect_new = """  useEffect(() => {
    localStorage.setItem('gemini_api_key', geminiKey);
  }, [geminiKey]);

  useEffect(() => {
    let isMounted = true;
    
    const checkConnection = async () => {
      setIsChecking(true);
      const active = await pingDevice();
      if (isMounted) {
        setIsConnected(active);
        setIsChecking(false);
      }
    };

    // Check immediately, then every 15 seconds
    checkConnection();
    const interval = setInterval(checkConnection, 15000);
    
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);"""
app_content = app_content.replace(app_effect_old, app_effect_new)

app_render_old = """          <div className="flex-1 relative">
            <SwayEditor user={user} geminiKey={geminiKey} />
          </div>
        </div>

        {/* Sidebar Panel */}
        <Sidebar user={user} geminiKey={geminiKey} setGeminiKey={setGeminiKey} />"""
app_render_new = """          <div className="flex-1 relative">
            <SwayEditor user={user} geminiKey={geminiKey} isConnected={isConnected} />
          </div>
        </div>

        {/* Sidebar Panel */}
        <Sidebar user={user} geminiKey={geminiKey} setGeminiKey={setGeminiKey} isConnected={isConnected} isChecking={isChecking} />"""
app_content = app_content.replace(app_render_old, app_render_new)

with open(app_path, 'w') as f:
    f.write(app_content)
