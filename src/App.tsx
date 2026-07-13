import React, { useEffect, useState } from 'react';
import { auth } from './firebase';
import { onAuthStateChanged, User, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { Sidebar } from './components/Sidebar';
import { SwayEditor } from './components/SwayEditor';
import { pingDevice } from './services/cloudRelay';
import { ConnectionStatus } from './components/ConnectionStatus';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [isInitializing, setIsInitializing] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [debugMsg, setDebugMsg] = useState("");

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setIsInitializing(false);
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    localStorage.setItem('gemini_api_key', geminiKey);
  }, [geminiKey]);

  const checkConnection = async () => {
    setIsChecking(true);
    const { success, debug } = await pingDevice();
    setIsConnected(success);
    setDebugMsg(debug);
    setIsChecking(false);
  };

  useEffect(() => {
    checkConnection();
  }, []);

  const handleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error(error);
    }
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 flex flex-col items-center justify-center relative overflow-hidden font-sans">
        {/* Dynamic Background Effects */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-[20%] left-[20%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[120px] mix-blend-screen"></div>
          <div className="absolute bottom-[20%] right-[20%] w-[30%] h-[40%] rounded-full bg-purple-600/10 blur-[120px] mix-blend-screen"></div>
        </div>
        
        <div className="relative z-10 text-center px-4 max-w-lg">
          <div className="mb-8 inline-flex items-center justify-center p-6 bg-white/5 rounded-[2rem] border border-white/10 shadow-2xl backdrop-blur-xl">
             <h1 className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400">
               Lenovo Debugger
             </h1>
          </div>
          <p className="text-lg text-neutral-400 mb-10 leading-relaxed">
            Advanced Cloud Relay Configuration Interface.<br />Please sign in to securely manage your device's Sway configuration via the cloud.
          </p>
          <button
            onClick={handleLogin}
            className="flex items-center justify-center gap-3 mx-auto bg-white text-black hover:bg-neutral-200 text-sm font-medium px-8 py-3.5 rounded-xl transition-all shadow-[0_0_40px_rgba(255,255,255,0.15)]"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Sign in with Google
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 flex flex-col font-sans relative overflow-hidden">
      
      {/* Dynamic Background Effects */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-blue-600/10 blur-[120px] mix-blend-screen"></div>
        <div className="absolute top-[40%] -right-[10%] w-[40%] h-[60%] rounded-full bg-purple-600/10 blur-[120px] mix-blend-screen"></div>
        <div className="absolute -bottom-[20%] left-[20%] w-[60%] h-[40%] rounded-full bg-emerald-600/5 blur-[120px] mix-blend-screen"></div>
      </div>

      {/* Main App Container */}
      <main className="flex-1 flex flex-col lg:flex-row relative z-10 w-full max-w-[1600px] mx-auto">
        
        {/* Editor Area (Flex grows) */}
        <div className="flex-1 p-4 lg:p-8 flex flex-col min-h-[60vh] lg:min-h-0">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400">
                Lenovo Debugger
              </h1>
              <p className="text-sm text-neutral-400 mt-1">Advanced Cloud Relay Configuration Interface</p>
            </div>
            
            <ConnectionStatus 
              isConnected={isConnected} 
              isChecking={isChecking} 
              onCheckConnection={checkConnection} 
              debugMsg={debugMsg} 
            />
          </div>
          
          <div className="flex-1 relative">
            <SwayEditor user={user} geminiKey={geminiKey} isConnected={isConnected} />
          </div>
        </div>

        {/* Sidebar Panel */}
        <Sidebar user={user} geminiKey={geminiKey} setGeminiKey={setGeminiKey} isConnected={isConnected} isChecking={isChecking} onCheckConnection={checkConnection} debugMsg={debugMsg} />

      </main>
    </div>
  );
}

export default App;
