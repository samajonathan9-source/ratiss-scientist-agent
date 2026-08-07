import React from 'react';

export default function About() {
  return (
    <div className="p-8 max-w-3xl mx-auto h-full overflow-y-auto text-slate-300 space-y-8">
      <div>
        <h2 className="text-2xl font-mono text-white font-bold tracking-widest mb-4 border-b border-white/10 pb-2">MANIFESTE JOHNKING0</h2>
        <p className="leading-relaxed text-sm">
          RATISS (Réseau Artificiel Topologique d'Intégration Systémique Souverain) n'est pas un LLM de plus. 
          C'est un moteur cognitif d'ordonnancement, un "cortex préfrontal" externe, qui contraint et vérifie la logique d'un LLM sous-jacent à travers la compression topologique et des preuves Zero-Knowledge sur CPU.
        </p>
      </div>

      <div>
        <h2 className="text-xl font-mono text-white font-bold tracking-widest mb-4">LES 7 SECTEURS</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { id: 1, name: "Reconnaissance Cognitive" },
            { id: 2, name: "Intégration et Architecture" },
            { id: 3, name: "Traitement Topologique" },
            { id: 4, name: "Déploiement Stratégique" },
            { id: 5, name: "Gouvernance et Sécurité" },
            { id: 6, name: "Supervision (Cypher ODV)" },
            { id: 7, name: "Cœur Souverain & P vs NP" }
          ].map(s => (
            <div key={s.id} className="bg-white/5 border border-white/10 p-4 rounded-lg flex items-center gap-4">
              <div className="text-blue-500 font-mono font-bold text-lg">0{s.id}</div>
              <div className="text-sm uppercase tracking-wider">{s.name}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
