# RATISS V9 — CERVEAU SCIENTIFIQUE UNIFIÉ (PHASE AEON PRIME)
**JohnKing0 & Architecte Jonathan Evina**  
*ORCID: 0009-0000-4092-5313*  
*DOI: 10.17605/OSF.IO/6JZMB*  

---

## 1. PRÉSENTATION DU PROJET
**RATISS V9 Aeon Prime** est un environnement autonome d'orchestration scientifique et de calcul physique lourd. Conçu pour s'exécuter localement sans dépendances tierces lourdes, il intègre :
- **Un Solveur Quantique t-J exact** utilisant la diagonalisation de Lanczos.
- **Un Moteur Topologique** calculant l'homologie persistante (nombres de Betti) sur les structures protéiques.
- **Une Couche Cryptographique** produisant des reçus ZK-STARK de conformité physique via RISC Zero.
- **Une Couche Cognitive** (TransDIPL'Y + Panthéon des 30 Pairs) pilotée par une boucle REACT locale avec bascule transparente vers un modèle System 2 Nemotron.

---

## 2. INSTALLATION ET ARCHITECTURE DE DÉPLOIEMENT

### A. Déploiement Local & VPS (Linux/macOS)
1. **Dépendances Système** :
   ```bash
   sudo apt-get update && sudo apt-get install -y python3-pip python3-venv git
   ```

2. **Création de la Sandbox virtuelle** :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install numpy psutil
   ```

3. **Inférence Locale Ollama (System 1)** :
   - Téléchargez et installez Ollama :
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```
   - Démarrez le démon Ollama et récupérez le modèle Qwen :
     ```bash
     ollama serve &
     ollama pull qwen2.5:1.5b-instruct
     ```

### B. Configuration de Nemotron (System 2 Fallback)
Pour activer le modèle de secours de 70 milliards de paramètres (Nemotron) de NVIDIA :
1. Obtenez une clé API sur OpenRouter ou un fournisseur équivalent.
2. Déclarez la variable d'environnement sur le serveur de calcul :
   ```bash
   export OPENROUTER_API_KEY="votre_cle_api_ici"
   ```

---

## 3. EXEMPLES D'UTILISATION (TERMINAL CLI)

Une série de commandes unifiées de contrôle est disponible via le point d'interaction `terminal_commands.py` :

### A. Obtenir le Diagnostic et Statut du Memory Guard
```bash
python3 agentic_scientist/terminal_commands.py status
```
*Sortie attendue* : Affiche l'utilisation réelle de la RAM comparée au seuil Memory Guard dur de **7.5 Go** (7500 MB).

### B. Consulter l'Historique des Runs Scientifiques Certifiés
```bash
python3 agentic_scientist/terminal_commands.py history
```
*Sortie attendue* : Tableau contenant les identifiants de Jobs, l'énergie fondamentale exacte de Lanczos calculée et la signature cryptographique STARK correspondante.

### C. Exécuter un Pipeline Complet (Diagonalisation, Homologie et Preuve ZK)
```bash
python3 agentic_scientist/terminal_commands.py run 4MZI
```

---

## 4. DÉPLOIEMENT DOCKER (CONSEILLÉ POUR PRODUCTION)
Pour exécuter le Cerveau Scientifique de façon totalement isolée et étanche :
1. **Construction de l'image** :
   ```bash
   docker build -t ratiss-brain -f agentic_scientist/Dockerfile .
   ```
2. **Lancement du conteneur sécurisé (limité à 7.5 Go de RAM)** :
   ```bash
   docker run -d --name ratiss-core --memory=7.5g --memory-swap=7.5g -p 3000:3000 ratiss-brain
   ```

---

## 5. LICENCE ET RÉFÉRENCES BIBLIOGRAPHIQUES
Ce projet est déposé sous licence de propriété intellectuelle exclusive **JohnKing0 & Architecte Jonathan Evina**.  
Pour toute citation ou publication académique s'appuyant sur les résultats de RATISS, veuillez citer l'ancrage DOI officiel : **10.17605/OSF.IO/6JZMB** et l'identifiant chercheur ORCID : **0009-0000-4092-5313**.
