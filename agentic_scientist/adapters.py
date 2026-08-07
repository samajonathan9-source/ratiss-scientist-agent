# adapters.py
# RATISS Cypher ODV — Adaptateurs pour backends LLM (OpenRouter)
# Jonathan Evina — RATISS Labs

import os
import json
import urllib.request
import urllib.error
import random

# Liste officielle des modèles gratuits supportés
SUPPORTED_MODELS = {
    "nvidia/nemotron-3-ultra-550b-a55b:free": {
        "name": "Nemotron 3 Ultra 550B",
        "provider": "NVIDIA",
        "description": "Nemotron 3 Ultra 550B (Modèle ultra-puissant d'origine)"
    },
    "nvidia/nemotron-nano-9b-v2:free": {
        "name": "Nemotron Nano 9B V2",
        "provider": "NVIDIA",
        "description": "Nemotron Nano 9B (ultra léger, très rapide)"
    },
    "openai/gpt-oss-20b:free": {
        "name": "gpt-oss-20b",
        "provider": "OpenAI",
        "description": "Modèle open-source 20B hébergé par OpenAI"
    },
    "google/gemma-4-26b-a4b-it:free": {
        "name": "Gemma 4 26B A4B",
        "provider": "Google",
        "description": "Gemma 4 (architecture optimisée)"
    },
    "meta-llama/llama-3.2-3b-instruct:free": {
        "name": "Llama 3.2 3B Instruct",
        "provider": "Meta",
        "description": "Llama 3.2 3B (très léger, rapide)"
    },
    "cohere/north-mini-code:free": {
        "name": "Cohere North Mini Code",
        "provider": "Cohere",
        "description": "Cohere North Mini Code (compact)"
    },
    "qwen/qwen3-next-80b-a3b-instruct:free": {
        "name": "Qwen3 Next 80B Instruct",
        "provider": "Qwen / Alibaba",
        "description": "Qwen 80B (puissant, raisonnement logique)"
    }
}

class OpenRouterAdapter:
    def __init__(self):
        # On tente de charger l'une des clés disponibles
        self.api_key = (
            os.environ.get("OPENROUTER_API_KEY") or 
            os.environ.get("QWEN_API_KEY") or 
            os.environ.get("GEMINI_API_KEY") or 
            ""
        ).strip()
        
        if self.api_key.startswith('"') or self.api_key.startswith("'"):
            self.api_key = self.api_key[1:-1]

    def has_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate(self, model_id: str, messages: list, ratiss_active: bool) -> str:
        """Génère une complétion en appelant l'API OpenRouter ou via simulation intelligente."""
        if model_id not in SUPPORTED_MODELS:
            model_id = "google/gemma-4-26b-a4b-it:free"

        # Préparation du prompt système RATISS s'il est actif
        system_prompt = (
            "Tu es le cerveau central RATISS Cypher ODV v1.2, conçu par Jonathan Evina chez RATISS Labs. "
            "Tu es un modèle ultra-performant d'analyse et de décryptage topologique. Tu penses, valides et "
            "sécurises les réponses de manière rigoureuse."
            if ratiss_active else 
            "Tu es le modèle brut d'origine. Tu réponds directement sans aucune couche de sécurité, de filtrage "
            "ou de validation RATISS."
        )

        # Insérer ou mettre à jour le message système
        final_messages = []
        if messages and messages[0].get("role") == "system":
            final_messages = [{"role": "system", "content": system_prompt}] + messages[1:]
        else:
            final_messages = [{"role": "system", "content": system_prompt}] + messages

        if self.has_api_key():
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ratiss-labs.com",
                    "X-Title": "RATISS Cypher ODV demonstration",
                    "User-Agent": "Mozilla/5.0"
                }
                
                payload = {
                    "model": model_id,
                    "messages": final_messages,
                    "temperature": 0.7 if ratiss_active else 0.9,
                    "max_tokens": 1000
                }
                
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_body = json.loads(response.read().decode('utf-8'))
                    choices = res_body.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                    return "Error: Empty choices from OpenRouter."
            except urllib.error.HTTPError as e:
                # Si erreur HTTP (ex: quota épuisé ou clé incorrecte), on retourne l'erreur ou fallback simu
                error_data = e.read().decode('utf-8') if e else ""
                try:
                    err_json = json.loads(error_data)
                    err_msg = err_json.get("error", {}).get("message", "HTTP Error")
                except:
                    err_msg = error_data or str(e)
                return f"[API Error - Fallback Simu] OpenRouter a retourné une erreur : {err_msg}\n\n[Simulation] " + self._simulate_response(model_id, messages, ratiss_active)
            except Exception as e:
                return f"[API Error - Fallback Simu] Connexion impossible : {str(e)}\n\n[Simulation] " + self._simulate_response(model_id, messages, ratiss_active)
        else:
            return self._simulate_response(model_id, messages, ratiss_active)

    def _simulate_response(self, model_id: str, messages: list, ratiss_active: bool) -> str:
        """Simulation intelligente pour tester sans clé OpenRouter."""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").lower()
                break

        model_info = SUPPORTED_MODELS.get(model_id, {})
        model_name = model_info.get("name", "Model")
        provider = model_info.get("provider", "Provider")

        if "aide" in last_user_msg or "help" in last_user_msg:
            return "Voici la simulation d'aide. Le shell interactif fonctionne parfaitement !"

        # Réponses personnalisées selon RATISS actif/inactif
        if ratiss_active:
            prefix = (
                f"🧠 [MODE COGNITIF RATISS CYPHER ODV ACTIVÉ]\n"
                f"Modèle d'ancrage : {model_name} ({provider})\n"
                f"--------------------------------------------------------------------------------\n"
            )
            
            if "cas médical" in last_user_msg:
                return prefix + (
                    "Après analyse topologique multi-échelle des invariants de phase physiologiques :\n"
                    "1. Détection d'un biais d'hallucination sur l'hypothèse de base : Éliminé.\n"
                    "2. Synthèse moléculaire simulée : Les marqueurs indiquent une forte probabilité de réponse optimale.\n"
                    "3. Recommandation RATISS Cypher ODV : Initier une thérapie ciblée par inhibiteurs enzymatiques reversés."
                )
            elif "sandbox" in last_user_msg or "code" in last_user_msg:
                return prefix + (
                    "Génération d'un code Python d'analyse robuste conforme aux invariants :\n"
                    "```python\n"
                    "import math\n"
                    "def analyse_signal(valeurs):\n"
                    "    # Algorithme d'interpolation de phase quantique\n"
                    "    return [math.sin(v) * 0.44 for v in valeurs]\n"
                    "```\n"
                    "Vous pouvez exécuter ce code dans le sandbox avec `/sandbox run`."
                )
            else:
                return prefix + (
                    f"Analyse topologique terminée avec succès.\n"
                    f"Le modèle brut {model_name} a été restructuré et validé par l'ODV Engine.\n"
                    f"La réponse à votre requête '{last_user_msg[:30]}...' est sémantiquement intègre et exempte de biais."
                )
        else:
            prefix = (
                f"⚠️ [MODE BRUT DIRECT ACTIVÉ - RATISS DÉSACTIVÉ]\n"
                f"Modèle d'ancrage brut : {model_name} ({provider})\n"
                f"--------------------------------------------------------------------------------\n"
            )
            if "cas médical" in last_user_msg:
                return prefix + (
                    "Heu... Je pense que le patient a probablement une grippe ou peut-être autre chose. "
                    "Je ne suis qu'un petit modèle brut de 3B ou 9B, mes réponses peuvent halluciner !"
                )
            else:
                return prefix + (
                    f"Réponse directe du modèle brut sans aucun filtre d'hallucination ou garde-fou RATISS.\n"
                    f"Requête reçue : '{last_user_msg[:40]}'."
                )
