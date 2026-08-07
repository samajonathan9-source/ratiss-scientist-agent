<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# RATISS Cypher ODV — Système Souverain d'Analyse (V9 Aeon Prime)

RATISS Cypher ODV est une architecture d'élite conçue par Jonathan Evina pour l'analyse de complexité, le routage sémantique, la simulation quantique et la génération de preuves cryptographiques Zero-Knowledge.

## ⚛️ Solveur Quantique Hybride & Moteur ZK RISC Zero (V9 AEON PRIME)

RATISS V9 intègre un moteur de calcul quantique hybride et un générateur de preuve ZK-STARK certifié :
- **Convergence t-J + Quirk** (`solve_quantum_hybrid`) : Couplage direct entre le simulateur de circuit de qubits (Quirk) et la résolution exacte par Lanczos float32 du modèle t-J ($E_0$, énergie par site, gap de spin $\Delta_s$, appariement $d$-wave).
- **Prover Bridge ZK RISC Zero** (`prover_bridge.py`) : Génération binaire de reçu cryptographique (`.receipt` B64, `zk_commitment`) vérifiable en <1ms pour certifier les invariants d'énergie, l'entropie de von Neumann et l'empreinte BLAKE3/SHA256 du vecteur d'état $\psi_0$.
- **Banque Macromoléculaire PDB Local** : Intégration directe des structures cristallographiques CIF/PDB (`2OCJ`, `1TUP`, `3KMD`, etc.) dans `ratiss_v9_real/data/pdb/`.

## 🛡️ Framework de Red-Teaming P vs NP

Le cœur de RATISS intègre désormais un module de **Red-Teaming** avancé pour attaquer les hypothèses algorithmiques et de complexité.

### Fonctionnalités
- **Oracles & Complexité** : Évaluation déterministe via Oracle B (Bennett-Gill).
- **Natural Proofs** : Détection automatique des barrières de Razborov-Rudich pour les bornes inférieures de circuits.
- **TSP Fuzzing** : Attaque d'algorithmes sur des instances adverses (Held-Karp gap, expanders à haute largeur d'arborescence).
- **Orchestration V8-OMEGA** : Intégration directe dans le flux de réflexion Cypher ODV.

### Utilisation
Pour lancer un benchmark complet sur vos hypothèses actuelles, utilisez la commande suivante dans le chat :
```bash
/redteam
```

## 🚀 Installation & Déploiement

**Prerequisites:** Node.js (v18+) & Python 3.10+

1. **Installation des dépendances :**
   `npm install`
2. **Configuration :**
   Configurez vos clés `GEMINI_API_KEY` et `OPENROUTER_API_KEY` dans votre environnement.
3. **Lancement :**
   `npm run dev`

View your app in AI Studio: https://ai.studio/apps/2dd37dec-48a3-41ef-b12c-b4f4f080ed0e
