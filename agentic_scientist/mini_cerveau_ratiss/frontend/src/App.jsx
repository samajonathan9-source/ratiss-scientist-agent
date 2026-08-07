import React, { useState } from 'react';
import ChatView from './components/ChatView';
import About from './components/About';
import { Terminal, Info } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-white/10 bg-black/40 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="text-blue-500" />
          <h1 className="font-mono font-bold tracking-wider">RATISS MINI-CORE</h1>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => setActiveTab('chat')}
            className={`font-mono text-sm uppercase tracking-wider px-3 py-1 rounded transition-colors ${activeTab === 'chat' ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Terminal
          </button>
          <button 
            onClick={() => setActiveTab('about')}
            className={`font-mono text-sm uppercase tracking-wider px-3 py-1 rounded transition-colors ${activeTab === 'about' ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            A propos
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-hidden relative">
        {activeTab === 'chat' ? <ChatView /> : <About />}
      </main>
    </div>
  );
}

export default App;
