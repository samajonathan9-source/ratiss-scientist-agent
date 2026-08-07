# RATISS MINI CERVEAU - SECTEUR 7 (ÉDITION PORTABLE)

**PROPRIÉTÉ INTELLECTUELLE : JOHNKING0**

Ce dossier contient une version allégée, portable et standalone du moteur RATISS CYPHER ODV.
Il a été conçu pour permettre à un comité d'évaluation externe de tester la logique, l'identité et le système anti-hallucination de RATISS en dehors de sa sandbox d'origine.

## STRUCTURE
- `/backend` : Un serveur Node.js léger faisant office de proxy sécurisé vers OpenRouter. Il contient le `ratiss_mini_core.js` qui implémente la compression topologique simulée et la garde factuelle (ex: Anti-Hallucination Nobel).
- `/frontend` : Une interface React/Vite minimaliste avec le design RATISS (sombre, badges ZK).

## LANCEMENT RAPIDE

### Backend
```bash
cd backend
npm install
# Copiez .env.example vers .env et ajoutez votre clé OpenRouter
npm start
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
