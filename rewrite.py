import os

app_path = '/home/zfil/Lenovo_Smarthome_Hub/src/App.tsx'

with open(app_path, 'r') as f:
    content = f.read()

# 1. Imports
imports_old = """import { useEffect, useRef, useState } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from '@xterm/addon-fit';
import 'xterm/css/xterm.css';
import { auth, db } from './firebase';
import { signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged, User } from 'firebase/auth';
import { collection, addDoc, serverTimestamp, query, orderBy, limit, getDocs } from 'firebase/firestore';
import { 
  Terminal as TerminalIcon, 
  MonitorSmartphone, 
  Cpu, 
  LogOut, 
  ShieldAlert, 
  Play, 
  Loader2,
  Github
} from 'lucide-react';"""

imports_new = """import { useEffect, useRef, useState } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from '@xterm/addon-fit';
import 'xterm/css/xterm.css';
import { auth, db } from './firebase';
import { signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged, User } from 'firebase/auth';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { GoogleGenAI } from "@google/genai";
import { 
  Terminal as TerminalIcon, 
  MonitorSmartphone, 
  Cpu, 
  LogOut, 
  ShieldAlert, 
  Play, 
  Loader2,
  Github,
  Key,
  Settings,
  Download,
  Upload,
  Sparkles,
  Layout
} from 'lucide-react';"""

content = content.replace(imports_old, imports_new)

# 2. State
state_old = """  const [diagnosing, setDiagnosing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");"""

state_new = """  const [diagnosing, setDiagnosing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [activeTab, setActiveTab] = useState<'diagnostics' | 'sway'>('diagnostics');
  const [swayConfig, setSwayConfig] = useState('');
  const [swayPrompt, setSwayPrompt] = useState('');
  const [isConfiguring, setIsConfiguring] = useState(false);

  useEffect(() => {
    localStorage.setItem('gemini_api_key', geminiKey);
  }, [geminiKey]);"""

content = content.replace(state_old, state_new)

# 3. Serial Port Request
port_old = "const p = await navigator.serial.requestPort();"
port_new = """const p = await navigator.serial.requestPort({
        filters: [
          { usbVendorId: 0x18d1 }, // Google
          { usbVendorId: 0x1d6b }  // Linux Foundation
        ]
      });"""

content = content.replace(port_old, port_new)

# 4. runDiagnostics and Sway logic
diag_old = """  const runDiagnostics = async () => {
    if (!logsBuffer.current) {
      setErrorMsg("No terminal output to diagnose.");
      return;
    }
    setDiagnosing(true);
    setErrorMsg("");
    setDiagnosisResult(null);

    try {
      const res = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ logs: logsBuffer.current }),
      });
      const data = await res.json();
      if (res.ok) {
        setDiagnosisResult(data.analysis);
        if (user) {
          await addDoc(collection(db, "diagnostics"), {
            analysis: data.analysis,
            timestamp: serverTimestamp(),
            uid: user.uid,
          });
        }
      } else {
        throw new Error(data.error);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to run diagnostics.');
    } finally {
      setDiagnosing(false);
    }
  };"""

diag_new = """  const runDiagnostics = async () => {
    if (!logsBuffer.current) {
      return setErrorMsg("No terminal output to diagnose.");
    }
    if (!geminiKey) {
      return setErrorMsg("Please enter your Gemini API Key first.");
    }
    setDiagnosing(true);
    setErrorMsg("");
    setDiagnosisResult(null);

    try {
      const ai = new GoogleGenAI({ apiKey: geminiKey });
      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: `You are an expert Linux system administrator (specifically postmarketOS sway edition on a Lenovo Duet 2 tablet). Analyze the following terminal output/logs and provide a brief, actionable diagnostic summary and suggest any commands to fix potential issues. Keep it concise.\\n\\nTerminal Logs:\\n${logsBuffer.current}`,
      });
      const analysis = response.text || "No analysis generated.";
      setDiagnosisResult(analysis);
      if (user) {
        await addDoc(collection(db, "diagnostics"), {
          analysis,
          timestamp: serverTimestamp(),
          uid: user.uid,
        });
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to run diagnostics.');
    } finally {
      setDiagnosing(false);
    }
  };

  const fetchSwayConfig = async () => {
    if (!writerRef.current) return;
    logsBuffer.current = "";
    const encoder = new TextEncoder();
    await writerRef.current.write(encoder.encode("echo '---START_CONFIG---' && cat ~/.config/sway/config && echo '---END_CONFIG---'\\r\\n"));
    
    setSwayConfig("Reading config from device...");
    let attempts = 0;
    const interval = setInterval(() => {
      const logs = logsBuffer.current;
      if (logs.includes('---START_CONFIG---') && logs.includes('---END_CONFIG---')) {
        clearInterval(interval);
        const start = logs.indexOf('---START_CONFIG---') + '---START_CONFIG---'.length;
        const end = logs.indexOf('---END_CONFIG---');
        const configContent = logs.substring(start, end).trim();
        setSwayConfig(configContent);
      }
      attempts++;
      if (attempts > 30) {
        clearInterval(interval);
        setSwayConfig((prev) => prev === "Reading config from device..." ? "Timeout reading config." : prev);
      }
    }, 500);
  };

  const applySwayConfig = async () => {
    if (!writerRef.current || !swayConfig) return;
    const encoder = new TextEncoder();
    const cmd = `cat << 'EOF' > ~/.config/sway/config\\n${swayConfig}\\nEOF\\r\\nswaymsg reload\\r\\n`;
    await writerRef.current.write(encoder.encode(cmd));
  };

  const modifySwayConfig = async () => {
    if (!geminiKey) return setErrorMsg("API key required");
    if (!swayConfig || swayConfig.startsWith("Reading")) return setErrorMsg("Read config first");
    setIsConfiguring(true);
    try {
      const ai = new GoogleGenAI({ apiKey: geminiKey });
      const prompt = `You are configuring sway for a Lenovo Duet 2. Current config:\\n\\n${swayConfig}\\n\\nUser request: ${swayPrompt}\\n\\nReturn ONLY the new full valid configuration file text. Do not include markdown formatting backticks if possible, just the raw config.`;
      const response = await ai.models.generateContent({
         model: "gemini-3.5-flash",
         contents: prompt
      });
      let newConfig = response.text || "";
      newConfig = newConfig.replace(/^\\s*```[a-z]*\\n/im, '').replace(/\\n```\\s*$/im, '').trim();
      setSwayConfig(newConfig);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
    setIsConfiguring(false);
  };"""

content = content.replace(diag_old, diag_new)

# 5. UI Updates
ui_old = """        {/* AI Diagnostics Sidebar */}
        <div className="w-full lg:w-96 h-80 lg:h-auto border-t lg:border-t-0 lg:border-l border-neutral-800 bg-neutral-900 flex flex-col shrink-0">
          <div className="p-4 sm:p-6 border-b border-neutral-800 shrink-0">
            <div className="flex items-center gap-2 text-white mb-2">
              <Cpu className="w-5 h-5 text-purple-400" />
              <h2 className="font-medium">AI Diagnostics</h2>
            </div>
            <p className="text-sm text-neutral-400 mb-4">
              Analyze terminal output to debug system errors instantly using local processing context.
            </p>
            <button
              onClick={runDiagnostics}
              disabled={!connected || diagnosing}
              className="w-full flex items-center justify-center gap-2 bg-neutral-800 hover:bg-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 px-4 rounded-lg transition-colors border border-neutral-700"
            >
              {diagnosing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              <span>{diagnosing ? 'Analyzing...' : 'Run Diagnostics'}</span>
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 text-sm text-neutral-300">
            {diagnosisResult ? (
              <div className="prose prose-invert prose-sm max-w-none">
                <div className="whitespace-pre-wrap">{diagnosisResult}</div>
              </div>
            ) : (
              <div className="text-neutral-500 text-center mt-10">
                Run diagnostics to analyze system state.
              </div>
            )}
          </div>
        </div>"""

ui_new = """        {/* AI Sidebar */}
        <div className="w-full lg:w-96 h-80 lg:h-auto border-t lg:border-t-0 lg:border-l border-neutral-800 bg-neutral-900 flex flex-col shrink-0">
          
          {/* Gemini API Key Section */}
          <div className="p-4 border-b border-neutral-800 bg-neutral-950/50">
            <label className="text-xs text-neutral-400 mb-1 flex items-center gap-1">
              <Key className="w-3 h-3" /> Gemini API Key
            </label>
            <input 
              type="password" 
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full bg-neutral-900 border border-neutral-700 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Tabs */}
          <div className="flex border-b border-neutral-800 shrink-0">
            <button 
              onClick={() => setActiveTab('diagnostics')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'diagnostics' ? 'text-blue-400 border-b-2 border-blue-400 bg-blue-400/5' : 'text-neutral-500 hover:text-neutral-300'}`}
            >
              <Cpu className="w-4 h-4" /> Diagnostics
            </button>
            <button 
              onClick={() => setActiveTab('sway')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'sway' ? 'text-blue-400 border-b-2 border-blue-400 bg-blue-400/5' : 'text-neutral-500 hover:text-neutral-300'}`}
            >
              <Layout className="w-4 h-4" /> Sway Config
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'diagnostics' && (
            <>
              <div className="p-4 sm:p-6 border-b border-neutral-800 shrink-0">
                <p className="text-sm text-neutral-400 mb-4">
                  Analyze terminal output to debug system errors instantly using local processing context.
                </p>
                <button
                  onClick={runDiagnostics}
                  disabled={!connected || diagnosing}
                  className="w-full flex items-center justify-center gap-2 bg-neutral-800 hover:bg-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 px-4 rounded-lg transition-colors border border-neutral-700"
                >
                  {diagnosing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                  <span>{diagnosing ? 'Analyzing...' : 'Run Diagnostics'}</span>
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-6 text-sm text-neutral-300">
                {diagnosisResult ? (
                  <div className="prose prose-invert prose-sm max-w-none">
                    <div className="whitespace-pre-wrap">{diagnosisResult}</div>
                  </div>
                ) : (
                  <div className="text-neutral-500 text-center mt-10">
                    Run diagnostics to analyze system state.
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'sway' && (
            <div className="flex flex-col h-full overflow-hidden">
              <div className="p-4 border-b border-neutral-800 shrink-0 flex gap-2">
                <button
                  onClick={fetchSwayConfig}
                  disabled={!connected}
                  className="flex-1 flex items-center justify-center gap-1 bg-neutral-800 hover:bg-neutral-700 disabled:opacity-50 text-white text-xs font-medium py-2 rounded transition-colors"
                >
                  <Download className="w-3 h-3" /> Read Config
                </button>
                <button
                  onClick={applySwayConfig}
                  disabled={!connected || !swayConfig || swayConfig.startsWith('Reading')}
                  className="flex-1 flex items-center justify-center gap-1 bg-emerald-600/20 text-emerald-500 hover:bg-emerald-600/30 disabled:opacity-50 text-xs font-medium py-2 rounded transition-colors"
                >
                  <Upload className="w-3 h-3" /> Apply Config
                </button>
              </div>

              <div className="p-4 shrink-0 border-b border-neutral-800">
                <label className="text-xs text-neutral-400 mb-1 block">AI Config Editor Prompt</label>
                <textarea
                  value={swayPrompt}
                  onChange={(e) => setSwayPrompt(e.target.value)}
                  placeholder="e.g. Change terminal to alacritty and background to #000000..."
                  className="w-full bg-neutral-900 border border-neutral-700 rounded p-2 text-sm text-white focus:outline-none focus:border-blue-500 min-h-[60px] resize-none"
                />
                <button
                  onClick={modifySwayConfig}
                  disabled={!swayConfig || swayConfig.startsWith('Reading') || isConfiguring}
                  className="w-full mt-2 flex items-center justify-center gap-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium py-2 rounded transition-colors shadow-lg shadow-blue-500/20"
                >
                  {isConfiguring ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                  {isConfiguring ? 'Generating...' : 'Generate with AI'}
                </button>
              </div>

              <div className="flex-1 overflow-hidden p-2">
                <textarea
                  value={swayConfig}
                  onChange={(e) => setSwayConfig(e.target.value)}
                  className="w-full h-full bg-[#0a0a0a] border border-neutral-800 rounded font-mono text-[11px] p-2 text-neutral-300 focus:outline-none focus:border-neutral-600 resize-none"
                  placeholder="Sway config will appear here..."
                />
              </div>
            </div>
          )}
        </div>"""

content = content.replace(ui_old, ui_new)

with open(app_path, 'w') as f:
    f.write(content)
