import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { doc, setDoc } from 'firebase/firestore';
import { db } from '../firebase';
import { executeCloudCommand } from '../services/cloudRelay';
import { 
  Lightbulb, 
  Lock, 
  Unlock, 
  Video,
  VideoOff,
  Plug,
  Wifi,
  WifiOff,
  Plus,
  X,
  Server,
  Battery,
  BatteryCharging,
  Sun,
  ShieldAlert,
  Settings,
  RefreshCw
} from 'lucide-react';

interface SmartDevice {
  id: string;
  name: string;
  ipAddress: string;
  type: string;
  token?: string;
  on: boolean;
  connected: boolean;
}

export const SmartHomeControl: React.FC = () => {
  const [devices, setDevices] = useState<SmartDevice[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);

  // New device form state
  const [newDeviceName, setNewDeviceName] = useState('');
  const [newDeviceIp, setNewDeviceIp] = useState('');
  const [newDeviceType, setNewDeviceType] = useState('tasmota');
  const [newDeviceToken, setNewDeviceToken] = useState('');

  // Tablet integration state
  const [tabletIp, setTabletIp] = useState('lenovo-hub.local'); // 15. Default to mDNS hostname
  const [hardwareStats, setHardwareStats] = useState<any>(null);
  const [tabletConnected, setTabletConnected] = useState<boolean>(false);
  
  // Camera state
  const [cameraError, setCameraError] = useState<boolean>(false);
  const [cameraRetryKey, setCameraRetryKey] = useState<number>(0);

  // Refs
  const failCountRef = useRef(0);
  const wasOfflineRef = useRef(true);

  // Load from local storage on mount
  useEffect(() => {
    const savedDevices = localStorage.getItem('smarthome_devices');
    if (savedDevices) {
      try {
        setDevices(JSON.parse(savedDevices));
      } catch (e) {
        console.error("Failed to parse saved devices", e);
      }
    }

    const savedIp = localStorage.getItem('tablet_ip');
    if (savedIp) {
      setTabletIp(savedIp);
    }
  }, []);

  // Save devices to local storage when they change
  useEffect(() => {
    localStorage.setItem('smarthome_devices', JSON.stringify(devices));
  }, [devices]);

  // Save IP to local storage
  useEffect(() => {
    localStorage.setItem('tablet_ip', tabletIp);
    setCameraRetryKey(k => k + 1); // Retry camera on IP change
    setCameraError(false);
  }, [tabletIp]);

  // 12. Sequential Poll pattern (instead of overlapping intervals)
  useEffect(() => {
    if (!tabletIp) return;
    
    let isMounted = true;
    let pollTimer: NodeJS.Timeout;
    
    const fetchHardware = async () => {
      // 11. Strict 5-second fetch timeout
      const abortController = new AbortController();
      const timeoutId = setTimeout(() => abortController.abort(), 5000);
      
      try {
        const res = await fetch(`http://${tabletIp}:5000/api/hardware`, {
          signal: abortController.signal
        });
        clearTimeout(timeoutId);
        
        if (res.ok) {
          // 17. Safe JSON Parsing
          let data;
          try {
            data = await res.json();
          } catch (jsonErr) {
            throw new Error('Malformed JSON');
          }

          if (isMounted) {
            setHardwareStats(data);
            
            // 14. MJPEG Stream Recovery
            if (wasOfflineRef.current) {
               // If we just came back online, aggressively force camera stream reload
               setCameraError(false);
               setCameraRetryKey(k => k + 1);
               wasOfflineRef.current = false;
            }
            
            setTabletConnected(true);
            failCountRef.current = 0; // Reset fail counter
          }
        } else {
          throw new Error('API returned non-200');
        }
      } catch (err: any) {
        clearTimeout(timeoutId);
        
        if (isMounted) {
          failCountRef.current += 1;
          // 19. Offline / Stale State Handling
          if (failCountRef.current >= 2) {
            setTabletConnected(false);
            wasOfflineRef.current = true;
          }
        }
      }

      // Schedule next poll only after this one completes or fails
      if (isMounted) {
        pollTimer = setTimeout(fetchHardware, 5000);
      }
    };
    
    // Initial call
    fetchHardware();
    
    return () => {
      // 18. Cleanup Unmounted Leaks
      isMounted = false;
      clearTimeout(pollTimer);
    };
  }, [tabletIp]);

  const togglePlug = async (id: string) => {
    // Save original state for revert
    const plug = devices.find(d => d.id === id);
    if (!plug) return;
    const originalState = plug.on;
    const newState = !originalState;

    // 13. Optimistic UI Reversion setup
    // Optimistically update
    setDevices(prev => prev.map(dev => 
      dev.id === id ? { ...dev, on: newState } : dev
    ));

    try {
      const targetRef = doc(db, 'device_sync', 'target');
      const command = `/home/zfil/Lenovo_Smarthome_Hub/control_device.sh ${plug.ipAddress} ${plug.type} ${newState ? 'on' : 'off'} ${plug.token || 'none'}`;
      
      await setDoc(targetRef, {
        command: command,
        status: "PENDING",
        timestamp: Date.now(),
        output: ""
      });
    } catch (e) {
      console.error("Failed to sync to Firebase, reverting UI state:", e);
      // Revert on failure
      setDevices(prev => prev.map(dev => 
        dev.id === id ? { ...dev, on: originalState } : dev
      ));
    }
  };

  const handleRegisterDevice = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDeviceName || !newDeviceIp) return;

    const newDevice: SmartDevice = {
      id: Math.random().toString(36).substring(7),
      name: newDeviceName,
      ipAddress: newDeviceIp,
      type: newDeviceType,
      token: newDeviceToken,
      on: false,
      connected: true
    };

    setDevices([...devices, newDevice]);
    
    setNewDeviceName('');
    setNewDeviceIp('');
    setNewDeviceType('tasmota');
    setNewDeviceToken('');
    setShowAddModal(false);
  };

  const handleRemoveDevice = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDevices(devices.filter(d => d.id !== id));
  };

  const handleToggleStream = async () => {
    if (isCameraActive) {
      setIsCameraActive(false);
      try {
        await executeCloudCommand("pkill -f mjpeg_screen_server.py");
      } catch (e) {
        console.error("Failed to stop stream", e);
      }
    } else {
      setIsCameraActive(true);
      try {
        // Run the python script in background using nohup or just background
        await executeCloudCommand("nohup python3 mjpeg_screen_server.py > /dev/null 2>&1 &", 3000);
      } catch (e) {
        console.error("Error starting stream", e);
      }
    }
  };

  return (
    <div className="w-full h-full p-6 lg:p-10 overflow-y-auto custom-scrollbar relative">
      <div className="absolute top-[10%] left-[20%] w-[30%] h-[30%] rounded-full bg-blue-500/10 blur-[100px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-[20%] right-[10%] w-[40%] h-[40%] rounded-full bg-emerald-500/10 blur-[120px] pointer-events-none mix-blend-screen" />
      
      <div className="max-w-7xl mx-auto space-y-8 relative z-10 pb-20">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <motion.h2 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl font-bold tracking-tight text-white mb-2"
            >
              My Home
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-neutral-400"
            >
              Security & Monitoring Active
            </motion.p>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSettingsModal(true)}
              className="p-2.5 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-colors text-neutral-300 relative"
              title="Tablet Settings"
            >
              <Settings className="w-5 h-5" />
              {!tabletConnected && (
                <div className="absolute top-0 right-0 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-[#111]" />
              )}
            </button>
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center gap-3 bg-white/5 border border-white/10 px-4 py-2 rounded-full backdrop-blur-md"
            >
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-sm font-medium text-emerald-400">Hub Online</span>
            </motion.div>
          </div>
        </div>

        {/* Cameras Section */}
        <div className="grid grid-cols-1 gap-6 mb-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-black/60 border border-white/10 rounded-3xl p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <Video className="w-5 h-5 text-neutral-400" /> Lenovo Tablet Webcam
              </h3>
              <button
                onClick={handleToggleStream}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors border ${
                  isCameraActive 
                    ? 'bg-rose-500/20 text-rose-400 border-rose-500/30 hover:bg-rose-500/30' 
                    : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/30'
                }`}
              >
                {isCameraActive ? 'Stop Stream' : 'Start Stream'}
              </button>
            </div>
            
            <div className="relative w-full h-96 bg-neutral-900 rounded-2xl overflow-hidden flex items-center justify-center border border-white/5">
              {isCameraActive ? (
                <>
                  {!cameraError && tabletConnected ? (
                    <img 
                      key={cameraRetryKey}
                      src={`http://${tabletIp}:8080/?action=stream`}
                      onError={() => setCameraError(true)}
                      alt="Tablet Webcam Stream" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex flex-col items-center justify-center gap-3 text-neutral-500">
                      <VideoOff className="w-10 h-10 mb-2" />
                      <p className="text-base font-medium">Camera Stream Offline</p>
                      <button 
                        onClick={() => {
                          setCameraError(false);
                          setCameraRetryKey(k => k + 1);
                        }}
                        className="flex items-center gap-2 text-sm bg-white/10 px-4 py-2 rounded-full hover:bg-white/20 text-white transition-colors"
                      >
                        <RefreshCw className="w-4 h-4" /> Retry Connection
                      </button>
                    </div>
                  )}
                  {!cameraError && tabletConnected && (
                    <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                      <span className="text-xs font-medium text-white tracking-wide">LIVE</span>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center justify-center gap-3 text-neutral-500">
                  <Video className="w-10 h-10 mb-2 opacity-50" />
                  <p className="text-base font-medium">Camera Stream Inactive</p>
                  <p className="text-sm opacity-70">Click "Start Stream" to view the live feed.</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Bottom Grid: Hardware & Plugs */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Left Column */}
          <div className="flex flex-col gap-6">
            
            {/* Tablet Hardware Telemetry */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="bg-white/5 border border-white/10 rounded-3xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">Tablet Telemetry</h3>
                <div className={`flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-md ${tabletConnected ? 'text-emerald-400 bg-emerald-500/10' : 'text-red-400 bg-red-500/10'}`}>
                  {tabletConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                  {tabletConnected ? 'Connected' : 'Offline'}
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                {/* Battery Status */}
                <div className={`bg-black/40 rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 border border-white/5 transition-all ${!tabletConnected && 'opacity-50 grayscale'}`}>
                  <div className={`p-2.5 rounded-full ${hardwareStats?.battery?.status === 'Charging' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'}`}>
                    <Battery className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-white">
                      {!tabletConnected ? 'STALE' : (hardwareStats?.battery?.capacity != null ? `${hardwareStats.battery.capacity}%` : 'N/A')}
                    </div>
                    <div className="text-[10px] text-neutral-500 uppercase tracking-wider">
                      {!tabletConnected ? 'WAITING...' : (hardwareStats?.battery?.status || 'Unknown')}
                    </div>
                  </div>
                </div>

                {/* Light Sensor */}
                <div className={`bg-black/40 rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 border border-white/5 transition-all ${!tabletConnected && 'opacity-50 grayscale'}`}>
                  <div className="p-2.5 rounded-full bg-yellow-500/20 text-yellow-400">
                    <Sun className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-white">
                      {!tabletConnected ? 'STALE' : (hardwareStats?.light_level != null ? `${hardwareStats.light_level} lx` : 'N/A')}
                    </div>
                    <div className="text-[10px] text-neutral-500 uppercase tracking-wider">Ambient Light</div>
                  </div>
                </div>

                {/* Tamper Alert */}
                <div className={`bg-black/40 rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 border border-white/5 transition-all ${!tabletConnected && 'opacity-50 grayscale'}`}>
                  <div className={`p-2.5 rounded-full ${hardwareStats?.security?.status === 'Tamper Detected' ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <div className={`text-sm font-medium ${hardwareStats?.security?.status === 'Tamper Detected' ? 'text-red-500' : 'text-white'}`}>
                      {!tabletConnected ? 'STALE' : (hardwareStats?.security?.status || 'Unknown')}
                    </div>
                    <div className="text-[10px] text-neutral-500 uppercase tracking-wider">Accelerometer</div>
                  </div>
                </div>
              </div>
            </motion.div>

          </div>

          {/* Right Column: Smart Devices & Security */}
          <div className="flex flex-col gap-6">
            
            {/* Registered Devices */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="flex flex-col gap-4"
            >
              <div className="flex items-center justify-between pl-2">
                <h3 className="text-lg font-medium text-white">Local Smart Devices</h3>
                <button 
                  onClick={() => setShowAddModal(true)}
                  className="flex items-center gap-1.5 text-xs font-medium bg-blue-500/20 text-blue-400 px-3 py-1.5 rounded-full hover:bg-blue-500/30 transition-colors"
                >
                  <Plus className="w-3 h-3" />
                  Add Device
                </button>
              </div>
              
              {devices.length === 0 ? (
                <div className="bg-white/5 border border-white/10 border-dashed rounded-3xl p-8 flex flex-col items-center justify-center text-center gap-3">
                  <Server className="w-8 h-8 text-neutral-500" />
                  <div>
                    <h4 className="text-neutral-300 font-medium mb-1">No Devices Registered</h4>
                    <p className="text-neutral-500 text-sm">Register a local smart plug or relay to control it via API.</p>
                  </div>
                  <button 
                    onClick={() => setShowAddModal(true)}
                    className="mt-2 bg-white text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-neutral-200 transition-colors"
                  >
                    Register & Connect
                  </button>
                </div>
              ) : (
                devices.map((plug) => (
                  <div 
                    key={plug.id}
                    className={`bg-white/5 border relative group ${plug.on ? 'border-purple-500/30 shadow-[0_0_20px_rgba(168,85,247,0.1)]' : 'border-white/10'} p-5 rounded-3xl flex flex-col gap-4 transition-all duration-300`}
                  >
                    <button
                      onClick={(e) => handleRemoveDevice(plug.id, e)}
                      className="absolute top-3 right-3 p-1.5 bg-black/40 text-neutral-400 rounded-full opacity-0 group-hover:opacity-100 hover:text-red-400 hover:bg-red-500/20 transition-all"
                    >
                      <X className="w-3 h-3" />
                    </button>
                    
                    <div className="flex items-center justify-between pr-8">
                      <div className="flex items-center gap-3">
                        <div className={`p-3 rounded-full ${plug.on ? 'bg-purple-500/20 text-purple-400' : 'bg-white/10 text-neutral-400'}`}>
                          <Plug className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white">{plug.name}</h4>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-[10px] bg-white/10 text-neutral-400 px-1.5 py-0.5 rounded font-mono uppercase tracking-wider">{plug.type}</span>
                            <span className="text-[10px] text-neutral-500 font-mono">{plug.ipAddress}</span>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => togglePlug(plug.id)}
                        className={`w-12 h-6 rounded-full p-1 transition-colors ${plug.on ? 'bg-purple-500' : 'bg-neutral-600'}`}
                      >
                        <motion.div 
                          layout
                          className={`w-4 h-4 rounded-full bg-white shadow-sm ${plug.on ? 'ml-auto' : 'mr-auto'}`}
                        />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </motion.div>

          </div>
        </div>
      </div>

      {/* Settings Modal */}
      <AnimatePresence>
        {showSettingsModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowSettingsModal(false)}
            />
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-[#111] border border-white/10 rounded-3xl p-6 w-full max-w-md relative z-10 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Tablet Connection</h3>
                <button onClick={() => setShowSettingsModal(false)} className="text-neutral-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-400 mb-1.5">Lenovo Tablet Hostname / IP</label>
                  <input 
                    type="text"
                    value={tabletIp}
                    onChange={e => setTabletIp(e.target.value)}
                    placeholder="e.g. lenovo-hub.local or 192.168.1.100"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-neutral-600 focus:outline-none focus:border-blue-500 transition-colors font-mono text-sm"
                  />
                  <p className="text-xs text-neutral-500 mt-2">
                    Default is <span className="font-mono bg-white/10 px-1 rounded">lenovo-hub.local</span>. If mDNS fails, type the specific IP address.
                  </p>
                </div>
                
                <div className="pt-2">
                  <button 
                    onClick={() => setShowSettingsModal(false)}
                    className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-neutral-200 transition-colors"
                  >
                    Save & Close
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Add Device Modal */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowAddModal(false)}
            />
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-[#111] border border-white/10 rounded-3xl p-6 w-full max-w-md relative z-10 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Register & Connect</h3>
                <button onClick={() => setShowAddModal(false)} className="text-neutral-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <form onSubmit={handleRegisterDevice} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-400 mb-1.5">Device Name</label>
                  <input 
                    type="text"
                    required
                    value={newDeviceName}
                    onChange={e => setNewDeviceName(e.target.value)}
                    placeholder="e.g. Living Room Lamp"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-neutral-600 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-400 mb-1.5">IP Address on Local Network</label>
                  <input 
                    type="text"
                    required
                    value={newDeviceIp}
                    onChange={e => setNewDeviceIp(e.target.value)}
                    placeholder="e.g. 192.168.1.150"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-neutral-600 focus:outline-none focus:border-blue-500 transition-colors font-mono text-sm"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-400 mb-1.5">Device Ecosystem / Firmware</label>
                  <select
                    value={newDeviceType}
                    onChange={e => setNewDeviceType(e.target.value)}
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-blue-500 transition-colors appearance-none"
                  >
                    <option value="tasmota">Tasmota (Athom/Pre-flashed)</option>
                    <option value="esphome">ESPHome</option>
                    <option value="shelly">Shelly Local API</option>
                    <option value="broadlink">BroadLink Local</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-400 mb-1.5">Security Password / API Key (Optional)</label>
                  <input 
                    type="password"
                    value={newDeviceToken}
                    onChange={e => setNewDeviceToken(e.target.value)}
                    placeholder="Leave blank if open"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-neutral-600 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
                
                <div className="pt-2">
                  <button 
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-colors shadow-[0_0_15px_rgba(37,99,235,0.3)]"
                  >
                    Register Device
                  </button>
                  <p className="text-center text-xs text-neutral-500 mt-3">
                    This will connect to the device locally via the Smarthome Hub.
                  </p>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};
