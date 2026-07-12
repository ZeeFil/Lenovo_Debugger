import { useEffect, useRef, useState } from 'react';
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
} from 'lucide-react';

const ALLOWED_EMAIL = "zlatan.filipovic92@gmail.com";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [port, setPort] = useState<SerialPort | null>(null);
  const [connected, setConnected] = useState(false);
  const [diagnosing, setDiagnosing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [activeTab, setActiveTab] = useState<'diagnostics' | 'sway'>('diagnostics');
  const [swayConfig, setSwayConfig] = useState('');
  const [swayPrompt, setSwayPrompt] = useState('');
  const [isConfiguring, setIsConfiguring] = useState(false);

  useEffect(() => {
    localStorage.setItem('gemini_api_key', geminiKey);
  }, [geminiKey]);

  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const writerRef = useRef<WritableStreamDefaultWriter<Uint8Array> | null>(null);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);
  const logsBuffer = useRef<string>("");

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      if (u) {
        if (u.email === ALLOWED_EMAIL) {
          setUser(u);
        } else {
          signOut(auth);
          setErrorMsg("Access Denied: Unauthorized email.");
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleLogin = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleLogout = () => {
    signOut(auth);
  };

  const initTerminal = () => {
    if (!terminalRef.current) return;
    if (xtermRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: {
        background: '#0a0a0a',
        foreground: '#f3f4f6',
      },
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: 14,
    });
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    term.onData((data) => {
      if (writerRef.current) {
        const encoder = new TextEncoder();
        writerRef.current.write(encoder.encode(data));
      }
    });

    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    const resizeObserver = new ResizeObserver(() => {
      fitAddon.fit();
    });
    resizeObserver.observe(terminalRef.current);
  };

  useEffect(() => {
    if (user && connected) {
      initTerminal();
    }
    return () => {
      // cleanup on dismount
    };
  }, [user, connected]);

  const push2FA = async (writer: WritableStreamDefaultWriter<Uint8Array>) => {
    // Generate a random code
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    alert(`2FA Code for Tablet: ${code}\nThis would pop up on the tablet.`);
    
    // Attempt to run a command on the tablet to show a notification
    const cmd = `notify-send "Auth Code: ${code}" || swaynag -m "Auth Code: ${code}"\r\n`;
    const encoder = new TextEncoder();
    await writer.write(encoder.encode(cmd));
  };

  const connectUSB = async () => {
    try {
      if (!('serial' in navigator)) {
        throw new Error('Web Serial API not supported in this browser.');
      }
      const p = await navigator.serial.requestPort({
        filters: [
          { usbVendorId: 0x18d1 }, // Google
          { usbVendorId: 0x1d6b }  // Linux Foundation
        ]
      });
      await p.open({ baudRate: 115200 });
      setPort(p);
      setConnected(true);
      setErrorMsg("");

      // Delay terminal init slightly to ensure DOM is ready
      setTimeout(() => initTerminal(), 100);

      const textDecoder = new TextDecoderStream();
      const readableStreamClosed = p.readable.pipeTo(textDecoder.writable);
      const reader = textDecoder.readable.getReader();
      readerRef.current = reader;

      const writer = p.writable.getWriter();
      writerRef.current = writer;

      await push2FA(writer);

      readLoop(reader);
    } catch (err: any) {
      console.error(err);
      if (err.message && err.message.includes('permissions policy')) {
        setErrorMsg('Web Serial is blocked in this view. Please open the app in a new tab (using the button in the top right) to connect to your device.');
      } else {
        setErrorMsg(err.message || 'Failed to connect to device.');
      }
    }
  };

  const disconnectUSB = async () => {
    try {
      if (readerRef.current) {
        await readerRef.current.cancel();
        readerRef.current = null;
      }
      if (writerRef.current) {
        writerRef.current.releaseLock();
        writerRef.current = null;
      }
      if (port) {
        await port.close();
        setPort(null);
      }
      setConnected(false);
      xtermRef.current?.clear();
      logsBuffer.current = "";
    } catch (err) {
      console.error("Failed to disconnect USB:", err);
    }
  };

  const readLoop = async (reader: ReadableStreamDefaultReader<string>) => {
    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (value) {
          xtermRef.current?.write(value);
          logsBuffer.current += value;
          if (logsBuffer.current.length > 10000) {
            logsBuffer.current = logsBuffer.current.slice(-10000);
          }
        }
      }
    } catch (error) {
      console.error("Read loop error", error);
    } finally {
      reader.releaseLock();
    }
  };

  const runDiagnostics = async () => {
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
        contents: `You are an expert Linux system administrator (specifically postmarketOS sway edition on a Lenovo Duet 2 tablet). Analyze the following terminal output/logs and provide a brief, actionable diagnostic summary and suggest any commands to fix potential issues. Keep it concise.\n\nTerminal Logs:\n${logsBuffer.current}`,
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
    await writerRef.current.write(encoder.encode("echo '---START_CONFIG---' && cat ~/.config/sway/config && echo '---END_CONFIG---'\r\n"));
    
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
    const cmd = `cat << 'EOF' > ~/.config/sway/config\n${swayConfig}\nEOF\r\nswaymsg reload\r\n`;
    await writerRef.current.write(encoder.encode(cmd));
  };

  const modifySwayConfig = async () => {
    if (!geminiKey) return setErrorMsg("API key required");
    if (!swayConfig || swayConfig.startsWith("Reading")) return setErrorMsg("Read config first");
    setIsConfiguring(true);
    try {
      const ai = new GoogleGenAI({ apiKey: geminiKey });
      const prompt = `You are configuring sway for a Lenovo Duet 2. Current config:\n\n${swayConfig}\n\nUser request: ${swayPrompt}\n\nReturn ONLY the new full valid configuration file text. Do not include markdown formatting backticks if possible, just the raw config.`;
      const response = await ai.models.generateContent({
         model: "gemini-3.5-flash",
         contents: prompt
      });
      let newConfig = response.text || "";
      newConfig = newConfig.replace(/^\s*```[a-z]*\n/im, '').replace(/\n```\s*$/im, '').trim();
      setSwayConfig(newConfig);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
    setIsConfiguring(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-neutral-400 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-neutral-950 flex flex-col items-center justify-center p-4">
        <div className="max-w-md w-full bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-2xl">
          <div className="flex justify-center mb-6">
            <MonitorSmartphone className="w-12 h-12 text-blue-500" />
          </div>
          <h1 className="text-2xl font-semibold text-white text-center mb-2">Remote Debug Console</h1>
          <p className="text-neutral-400 text-center mb-8">
            Connect and debug your Lenovo Duet 2 tablet running postmarketOS.
          </p>
          
          {errorMsg && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-3 rounded-lg flex items-start gap-2 mb-6">
              <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0" />
              <p>{errorMsg}</p>
            </div>
          )}

          <button
            onClick={handleLogin}
            className="w-full bg-white hover:bg-neutral-200 text-black font-medium py-3 px-4 rounded-xl transition-colors"
          >
            Sign in with Google
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 flex flex-col font-sans">
      <header className="border-b border-neutral-800 bg-neutral-950 flex flex-col sm:flex-row items-center justify-between px-4 sm:px-6 py-4 gap-4 sm:gap-0 shrink-0">
        <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-start">
          <div className="flex items-center gap-3">
            <TerminalIcon className="w-6 h-6 text-blue-500" />
            <h1 className="text-base sm:text-lg font-medium text-white tracking-tight truncate max-w-[200px] sm:max-w-none">Lenovo Duet 2 Debugger</h1>
          </div>
          <span className="text-xs font-mono text-neutral-500 bg-neutral-900 px-2 py-1 rounded">
            postmarketOS
          </span>
          <div className="flex items-center gap-2 ml-2 bg-neutral-900/50 px-3 py-1 rounded-full border border-neutral-800">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-neutral-600'}`}></div>
            <span className={`text-xs font-medium ${connected ? 'text-emerald-400' : 'text-neutral-500'}`}>
              {connected ? 'Active & Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4 w-full sm:w-auto justify-end">
          <a href="https://github.com/new" target="_blank" rel="noreferrer" className="flex items-center gap-2 text-sm text-neutral-400 hover:text-white transition-colors">
            <Github className="w-4 h-4" />
            <span className="hidden sm:inline">GitHub Repository</span>
          </a>
          <div className="h-4 w-px bg-neutral-800"></div>
          {connected && (
            <button
              onClick={disconnectUSB}
              className="text-sm text-red-400 hover:text-red-300 flex items-center gap-2 transition-colors mr-4"
            >
              <span>Disconnect USB</span>
            </button>
          )}
          <button
            onClick={handleLogout}
            className="text-sm text-neutral-400 hover:text-white flex items-center gap-2 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </header>

      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Terminal Area */}
        <div className="flex-1 flex flex-col bg-neutral-950 relative min-h-[50vh] lg:min-h-0">
          {!connected ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-neutral-950/80 backdrop-blur-sm p-6 overflow-y-auto">
              <MonitorSmartphone className="w-16 h-16 text-neutral-600 mb-6" />
              <h2 className="text-2xl font-semibold text-white mb-2">Connect Your Device</h2>
              <p className="text-neutral-400 mb-8 max-w-lg text-center">
                Follow these steps to establish a secure remote shell session with your Lenovo Duet 2 tablet running postmarketOS.
              </p>
              
              <div className="w-full max-w-md bg-neutral-900 border border-neutral-800 rounded-xl p-6 mb-8 text-left">
                <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-sm">1</span>
                  Prepare the Tablet
                </h3>
                <p className="text-neutral-400 text-sm mb-4 pl-8">
                  Ensure the Lenovo Duet 2 is powered on and booting into postmarketOS sway edition.
                </p>

                <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-sm">2</span>
                  Connect USB Cable
                </h3>
                <p className="text-neutral-400 text-sm mb-4 pl-8">
                  Connect the tablet to this device using a reliable USB-C data cable.
                </p>

                <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-sm">3</span>
                  Authorize Connection
                </h3>
                <p className="text-neutral-400 text-sm pl-8">
                  Click the connect button below and select the tablet from the browser's device list. A 2FA pop-up will appear on the tablet to verify your identity.
                </p>
              </div>

              <button
                onClick={connectUSB}
                className="bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-8 rounded-xl transition-colors shadow-lg shadow-blue-500/20 text-lg flex items-center gap-2"
              >
                <TerminalIcon className="w-5 h-5" />
                Connect via Web Serial
              </button>
              {errorMsg && (
                <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-3 rounded-lg flex items-start gap-2 mt-6 max-w-md">
                  <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0" />
                  <p>{errorMsg}</p>
                </div>
              )}
            </div>
          ) : null}
          <div ref={terminalRef} className="flex-1 p-4 bg-[#0a0a0a]"></div>
        </div>

        {/* AI Sidebar */}
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
        </div>
      </main>
    </div>
  );
}
