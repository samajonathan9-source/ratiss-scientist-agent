import React, { useState, useRef, useEffect } from 'react';
import { Send, Cpu, CheckCircle2, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ChatView() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'INITIALISATION RATISS TERMINÉE. Moteur cognitif allégé en ligne.', isVerified: true }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response || data.error,
        isVerified: data.proof === 'ZK-CPU-PASSED',
        isRejected: data.proof === 'ZK-CPU-REJECTED'
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Erreur de connexion au noyau RATISS.', isRejected: true }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col p-4 max-w-4xl mx-auto w-full">
      <div className="flex-1 overflow-y-auto space-y-4 p-4 scrollbar-hide">
        {messages.map((msg, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={i} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] rounded-xl p-4 ${msg.role === 'user' ? 'bg-blue-600/20 border border-blue-500/30 text-blue-50' : 'bg-white/5 border border-white/10 text-slate-300'}`}>
              <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</div>
              
              {msg.role === 'assistant' && msg.isVerified && (
                <div className="mt-2 flex items-center gap-1.5 text-xs font-mono text-green-400/80 bg-green-900/20 px-2 py-1 rounded w-fit border border-green-500/20">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>PREUVE ZK-CPU : VALIDE</span>
                </div>
              )}
              {msg.role === 'assistant' && msg.isRejected && (
                <div className="mt-2 flex items-center gap-1.5 text-xs font-mono text-red-400/80 bg-red-900/20 px-2 py-1 rounded w-fit border border-red-500/20">
                  <XCircle className="w-3 h-3" />
                  <span>INTERCEPTION TOPOZK : REJETÉ</span>
                </div>
              )}
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-slate-500 font-mono text-sm">
            <Cpu className="w-4 h-4 animate-pulse" /> Traitement topologique...
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Interrogez le noyau RATISS..."
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-colors"
        />
        <button 
          type="submit" 
          disabled={loading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-lg transition-colors flex items-center justify-center"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}
