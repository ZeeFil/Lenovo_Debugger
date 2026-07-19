import os

app_path = '/home/zfil/Lenovo_Smarthome_Hub/src/App.tsx'

with open(app_path, 'r') as f:
    content = f.read()

# 1. Imports
imports_old = """import { collection, addDoc, serverTimestamp } from 'firebase/firestore';"""
imports_new = """import { collection, addDoc, serverTimestamp, doc, onSnapshot, setDoc } from 'firebase/firestore';"""
content = content.replace(imports_old, imports_new)

# 2. State
state_old = """  const [isConfiguring, setIsConfiguring] = useState(false);"""
state_new = """  const [isConfiguring, setIsConfiguring] = useState(false);
  const [connectionMode, setConnectionMode] = useState<'usb' | 'cloud'>('usb');"""
content = content.replace(state_old, state_new)


# 3. fetchSwayConfig and applySwayConfig
func_old = """  const fetchSwayConfig = async () => {
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
  };"""

func_new = """  const fetchSwayConfig = async () => {
    if (connectionMode === 'usb') {
      if (!writerRef.current) return setErrorMsg("USB not connected.");
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
    } else {
      setSwayConfig("Requesting config via Cloud Relay...");
      const targetRef = doc(db, 'device_sync', 'target');
      await setDoc(targetRef, {
        command: "cat ~/.config/sway/config",
        status: "PENDING",
        timestamp: Date.now(),
        output: ""
      });
      
      const unsubscribe = onSnapshot(targetRef, (snapshot) => {
        const data = snapshot.data();
        if (data && data.status === 'COMPLETED' && data.command === "cat ~/.config/sway/config") {
          setSwayConfig(data.output || "");
          unsubscribe();
        }
      });

      setTimeout(() => {
        unsubscribe();
        setSwayConfig((prev) => prev.startsWith("Requesting") ? "Timeout reading config via Cloud Relay. Is the tablet_agent.py running?" : prev);
      }, 10000);
    }
  };

  const applySwayConfig = async () => {
    if (!swayConfig) return;
    const cmd = `cat << 'EOF' > ~/.config/sway/config\\n${swayConfig}\\nEOF\\nswaymsg reload`;
    
    if (connectionMode === 'usb') {
      if (!writerRef.current) return;
      const encoder = new TextEncoder();
      await writerRef.current.write(encoder.encode(cmd + "\\r\\n"));
    } else {
      const targetRef = doc(db, 'device_sync', 'target');
      await setDoc(targetRef, {
        command: cmd,
        status: "PENDING",
        timestamp: Date.now(),
        output: ""
      });
    }
  };"""

content = content.replace(func_old, func_new)

# 4. Connection UI Toggle
ui_old = """          {/* Gemini API Key Section */}
          <div className="p-4 border-b border-neutral-800 bg-neutral-950/50">"""
ui_new = """          {/* Connection Mode Toggle */}
          <div className="p-4 border-b border-neutral-800 bg-neutral-900">
             <label className="text-xs text-neutral-400 mb-2 block">Connection Mode</label>
             <div className="flex bg-neutral-950 rounded p-1">
                <button 
                  onClick={() => setConnectionMode('usb')}
                  className={`flex-1 text-xs py-1.5 rounded transition-colors ${connectionMode === 'usb' ? 'bg-neutral-800 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
                >
                  USB Serial
                </button>
                <button 
                  onClick={() => setConnectionMode('cloud')}
                  className={`flex-1 text-xs py-1.5 rounded transition-colors ${connectionMode === 'cloud' ? 'bg-neutral-800 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
                >
                  Cloud Relay
                </button>
             </div>
          </div>

          {/* Gemini API Key Section */}
          <div className="p-4 border-b border-neutral-800 bg-neutral-950/50">"""

content = content.replace(ui_old, ui_new)

# 5. Fix disabled state for Cloud Relay in Sway tab
ui_disabled_old = """                <button
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
                </button>"""

ui_disabled_new = """                <button
                  onClick={fetchSwayConfig}
                  disabled={connectionMode === 'usb' && !connected}
                  className="flex-1 flex items-center justify-center gap-1 bg-neutral-800 hover:bg-neutral-700 disabled:opacity-50 text-white text-xs font-medium py-2 rounded transition-colors"
                >
                  <Download className="w-3 h-3" /> Read Config
                </button>
                <button
                  onClick={applySwayConfig}
                  disabled={(connectionMode === 'usb' && !connected) || !swayConfig || swayConfig.startsWith('Reading') || swayConfig.startsWith('Requesting')}
                  className="flex-1 flex items-center justify-center gap-1 bg-emerald-600/20 text-emerald-500 hover:bg-emerald-600/30 disabled:opacity-50 text-xs font-medium py-2 rounded transition-colors"
                >
                  <Upload className="w-3 h-3" /> Apply Config
                </button>"""
content = content.replace(ui_disabled_old, ui_disabled_new)

with open(app_path, 'w') as f:
    f.write(content)
