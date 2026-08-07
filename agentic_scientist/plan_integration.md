# PLAN D'INTÉGRATION STRATÉGIQUE RATISS V9 — PHASE AEON PRIME
**JohnKing0 & Architecte Jonathan Evina**  
*ORCID: 0009-0000-4092-5313*  
*DOI: 10.17605/OSF.IO/6JZMB*  

---

## 1. STRATÉGIE DE CONTINUITÉ : FALLBACK COGNITIF NEMOTRON 3 ULTRA

La résilience est une exigence absolue de la souveraineté technologique de RATISS V9. Pour éliminer tout point de défaillance unique (Single Point of Failure) lié à l'utilisation d'Ollama local (qui peut être coupé en cas de maintenance ou de panne du démon Ollama), nous mettons en œuvre une architecture de rebond ou **fallback cognitif asymétrique**.

### A. Mécanique de Redondance
1. **Inférence Routine (System 1)** : Ollama local exécutant un modèle compact `Qwen 2.5` optimisé pour la vitesse de parsing JSON et le routage initial.
2. **Inférence Secours (System 2)** : En cas de crash, de délai dépassé (timeout) ou d'absence du service local, l'agent bascule à chaud vers l'API **Nemotron 3 Ultra** (via OpenRouter ou serveur dédié). Ce modèle hautement performant de NVIDIA fournit des capacités de raisonnement approfondies pour prendre le relais sans aucune interruption.

```
                  ┌────────────────────────┐
                  │ Requête Scientifique   │
                  └───────────┬────────────┘
                              │
                    [Tentative Inférence]
                              │
                    ┌─────────▼─────────┐  OUI   ┌───────────────────────────┐
                    │ Ollama opérationnel?├──────► Exécuter Qwen 2.5 local   │
                    └─────────┬─────────┘        └───────────────────────────┘
                              │ NON
                    ┌─────────▼─────────┐
                    │ BASCULE AUTOMATIQUE│
                    │      (FALLBACK)    │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Nemotron 3 Ultra  │
                    │ (Inférence Cloud) │
                    └───────────────────┘
```

---

## 2. COMMANDES TERMINAL CUSTOMISÉES (INTERACTIONS SANDBOX)

Pour permettre à l'utilisateur et aux agents tiers (comme Manus) de piloter et de diagnostiquer le Cerveau Scientifique en ligne de commande, nous implémentons un ensemble de commandes exclusives unifiées sous le namespace `ratiss` (via `terminal_commands.py`) :

*   `ratiss status` : Diagnostic matériel et logiciel complet. Récupération directe des statistiques de l'usage de la mémoire vive (RAM) et confirmation que le **Memory Guard** est bien configuré sous la limite dure de **7500 MB** pour éviter tout OOM.
*   `ratiss history` : Extraction tabulaire structurée des dix derniers runs scientifiques effectués par la machine, comprenant les timestamps exacts, les identifiants de Jobs, l'énergie fondamentale de Lanczos calculée et la signature cryptographique STARK.
*   `ratiss run <job_id>` : Lancement synchrone du pipeline de recherche à trois étages (Diagonalisation t-J Lanczos ED -> Homologie Persistante d'Alpha/Rips -> Génération de preuve ZK-STARK RISC Zero) pour certifier l'intégrité de la structure moléculaire cible (ex : `4MZI`, `4MZR`, `2OCJ`).

---

## 3. CADRE DE SÉCURITÉ DE LA SANDBOX ET ISOLATION DES COMMANDES

Afin d'éviter toute injection de code arbitraire et de garantir l'étanchéité du serveur, les règles de sécurité suivantes sont appliquées sur la Sandbox du terminal :

### A. Filtrage des Entrées (Input Sanitization)
Toute commande saisie par le biais du terminal interactif ou envoyée via API REST fait l'objet d'un filtrage strict contre les métacaractères d'injection de shell (`|`, `;`, `&`, `$`, `` ` ``). Seul un sous-ensemble restreint de binaires autorisés (`python3`, `neofetch`, `ls`, `cat`, `top`, `clear`) est toléré.

### B. Isolation par Containerization (Docker)
Sur le serveur de production, le Cerveau Scientifique est isolé au sein d'un conteneur Docker éphémère ne disposant que de privilèges restreints (non-root) :
*   `Read-Only File System` sur les répertoires système sensibles.
*   `Cgroup RAM Limit` fixée par Docker à **7.5 Go** en adéquation parfaite avec la configuration de notre Memory Guard applicatif.
*   Désactivation de la communication réseau externe pour les solveurs quantiques physiques afin de prévenir toute fuite de données d'études confidentielles (Zero-Knowledge Offline mode).

---

## 4. DESIGN TECHNIQUE ET CRÉDITS ACADÉMIQUES
La phase Aeon Prime respecte l'ancrage formel de RATISS au sein du patrimoine scientifique international par l'inclusion systématique de nos métadonnées de publication dans tous les reçus de preuve et les en-têtes de rapports générés :
*   **ORCID Auteur Principal** : `0009-0000-4092-5313` (Architecte Jonathan Evina)
*   **DOI de Référence** : `10.17605/OSF.IO/6JZMB`
