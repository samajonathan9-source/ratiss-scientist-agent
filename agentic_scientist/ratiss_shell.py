# ratiss_shell.py
# RATISS Cypher ODV — Shell de démonstration interactif
# Jonathan Evina — RATISS Labs

import os
import sys
import io
import time
from logger import RatissLogger
from adapters import OpenRouterAdapter, SUPPORTED_MODELS

class ExecutionSandbox:
    """Mini-environnement encapsulé pour l'exécution de code."""
    def __init__(self):
        self.code_history = []
        self.execution_logs = []
        self.allow_imports = ['math', 'random', 'collections', 'itertools']
        self.timeout = 5  # secondes

    def run_code(self, code: str) -> dict:
        """Exécute du code Python dans un environnement contrôlé."""
        self.code_history.append(code)
        
        # Sauvegarde des flux standards
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        redirected_error = io.StringIO()
        sys.stdout = redirected_output
        sys.stderr = redirected_error
        
        # Préparer un environnement de builtins restreint et sécurisé
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'chr': chr, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
            'filter': filter, 'float': float, 'format': format, 'hash': hash,
            'hex': hex, 'id': id, 'int': int, 'isinstance': isinstance,
            'issubclass': issubclass, 'iter': iter, 'len': len, 'list': list,
            'map': map, 'max': max, 'min': min, 'next': next, 'oct': oct,
            'ord': ord, 'pow': pow, 'print': print, 'range': range,
            'repr': repr, 'reversed': reversed, 'round': round, 'set': set,
            'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
            'tuple': tuple, 'type': type, 'zip': zip
        }
        
        globals_env = {
            '__builtins__': safe_builtins
        }
        
        # Injecter uniquement les imports autorisés
        for mod_name in self.allow_imports:
            try:
                globals_env[mod_name] = __import__(mod_name)
            except Exception as e:
                pass
                
        error = None
        try:
            # Exécution du code
            exec(code, globals_env)
        except Exception as e:
            error = str(e)
        finally:
            # Restauration des flux standards
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        stdout_val = redirected_output.getvalue()
        stderr_val = redirected_error.getvalue()
        
        result_log = {
            "stdout": stdout_val,
            "stderr": stderr_val or (error if error else ""),
            "success": error is None
        }
        self.execution_logs.append(result_log)
        return result_log


class RatissShell:
    def __init__(self):
        self.adapter = OpenRouterAdapter()
        # Modèle par défaut : Google Gemma 4 26B
        self.backend_id = "google/gemma-4-26b-a4b-it:free"
        self.ratiss_active = True  # Bouton ON/OFF
        self.view_reasoning = True  # Affichage des logs de raisonnement
        self.sandbox = ExecutionSandbox()
        self.history = []  # [{role: user/assistant, content: str}]
        self.logger = RatissLogger(view_reasoning=self.view_reasoning)

    def draw_header(self):
        """Dessine l'en-tête dynamique du RATISS Shell."""
        model_info = SUPPORTED_MODELS.get(self.backend_id, {})
        name = model_info.get("name", "Unknown")
        provider = model_info.get("provider", "Unknown")
        
        status_ratiss = "ACTIVE ✅" if self.ratiss_active else "DEACTIVATED ❌"
        status_reasoning = "ON" if self.view_reasoning else "OFF"
        
        print("╔" + "═"*78 + "╗")
        print(f"║  RATISS Cypher ODV — Shell de démonstration                                 ║")
        print(f"║  Backend actif : {self.backend_id:<59} ║")
        print(f"║  Fournisseur  : {provider:<60} ║")
        print(f"║  RATISS        : {status_ratiss:<60} ║")
        print(f"║  Reasoning     : {status_reasoning:<60} ║")
        print(f"║  Sandbox       : READY                                                        ║")
        print("╚" + "═"*78 + "╝")

    def print_help(self):
        """Affiche les commandes du help."""
        print("\nCommandes disponibles :")
        print("  /model list               : Liste les backends disponibles avec leurs IDs")
        print("  /model use [id]           : Change le backend actif en utilisant son ID exact")
        print("  /view reasoning on/off    : Active ou désactive l'affichage des logs de raisonnement")
        print("  /ratiss pause/resume      : Active ou désactive (pause) le cerveau central RATISS")
        print("  /sandbox run [code]       : Exécute du code Python sécurisé dans la sandbox")
        print("  /sandbox show             : Affiche l'historique d'exécution et les logs de la sandbox")
        print("  /history                  : Affiche l'historique de la conversation")
        print("  /clear                    : Efface l'écran du terminal")
        print("  /help                     : Affiche ce menu d'aide")
        print("  /exit                     : Quitter le shell\n")

    def process_command(self, command: str) -> bool:
        """Traite une commande spéciale commencant par /."""
        parts = command.strip().split(" ", 2)
        base_cmd = parts[0].lower()
        
        if base_cmd == "/exit":
            print("[*] Fermeture du RATISS Shell. À bientôt !")
            sys.exit(0)
            
        elif base_cmd == "/clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            self.draw_header()
            return True
            
        elif base_cmd == "/help":
            self.print_help()
            return True
            
        elif base_cmd == "/model":
            if len(parts) < 2:
                print("Usage: /model list  OU  /model use [id]")
                return True
            sub_cmd = parts[1].lower()
            if sub_cmd == "list":
                print("\nBackends disponibles (vrais modèles OpenRouter gratuits) :")
                for i, (m_id, info) in enumerate(SUPPORTED_MODELS.items(), 1):
                    print(f"  [{i}] {info['provider']:<10} : {m_id:<45} ({info['name']})")
                print("")
            elif sub_cmd == "use":
                if len(parts) < 3:
                    print("Usage: /model use [id]")
                    return True
                target_id = parts[2].strip()
                if target_id in SUPPORTED_MODELS:
                    self.backend_id = target_id
                    print(f"[+] Backend basculé avec succès sur {SUPPORTED_MODELS[target_id]['name']}.")
                    print(f"    Model ID : {target_id}")
                else:
                    # Tenter de trouver par index (1 à 6)
                    try:
                        idx = int(target_id) - 1
                        m_ids = list(SUPPORTED_MODELS.keys())
                        if 0 <= idx < len(m_ids):
                            self.backend_id = m_ids[idx]
                            print(f"[+] Backend basculé avec succès sur {SUPPORTED_MODELS[self.backend_id]['name']}.")
                            print(f"    Model ID : {self.backend_id}")
                        else:
                            print(f"[-] Index ou ID de modèle inconnu : {target_id}")
                    except ValueError:
                        print(f"[-] ID de modèle inconnu : {target_id}")
            return True
            
        elif base_cmd == "/view":
            if len(parts) < 3 or parts[1].lower() != "reasoning":
                print("Usage: /view reasoning on/off")
                return True
            state = parts[2].lower()
            if state in ["on", "true", "1"]:
                self.view_reasoning = True
                self.logger.view_reasoning = True
                print("[+] Logs de raisonnement activés.")
            elif state in ["off", "false", "0"]:
                self.view_reasoning = False
                self.logger.view_reasoning = False
                print("[-] Logs de raisonnement désactivés.")
            else:
                print("Option invalide. Utilisez 'on' ou 'off'.")
            return True
            
        elif base_cmd == "/ratiss":
            if len(parts) < 2:
                print("Usage: /ratiss pause/resume")
                return True
            state = parts[1].lower()
            if state in ["pause", "stop", "off"]:
                self.ratiss_active = False
                print("[-] Cerveau RATISS désactivé. Le modèle brut répondra seul.")
            elif state in ["resume", "start", "on"]:
                self.ratiss_active = True
                print("[+] Cerveau RATISS réactivé. Validation et intégrité de phase actives.")
            else:
                print("Option invalide. Utilisez 'pause' ou 'resume'.")
            return True
            
        elif base_cmd == "/sandbox":
            if len(parts) < 2:
                print("Usage: /sandbox run [code]  OU  /sandbox show")
                return True
            sub_cmd = parts[1].lower()
            if sub_cmd == "run":
                if len(parts) < 3:
                    print("Usage: /sandbox run [code_python]")
                    return True
                # Extraire le code (qui peut être entouré de quotes ou de backticks)
                raw_code = parts[2].strip()
                if raw_code.startswith("`"):
                    raw_code = raw_code.strip("`").strip()
                if raw_code.startswith('"') and raw_code.endswith('"'):
                    raw_code = raw_code[1:-1]
                
                print("[*] Exécution dans la Sandbox sécurisée...")
                res = self.sandbox.run_code(raw_code)
                print(f"  - Succès : {res['success']}")
                if res['stdout']:
                    print(f"  [Stdout] :\n{res['stdout']}")
                if res['stderr']:
                    print(f"  [Stderr/Erreur] :\n{res['stderr']}")
            elif sub_cmd == "show":
                print("\n--- Historique de la Sandbox ---")
                if not self.sandbox.code_history:
                    print("Aucun code n'a été exécuté pour le moment.")
                else:
                    for i, (code, log) in enumerate(zip(self.sandbox.code_history, self.sandbox.execution_logs)):
                        print(f"[{i+1}] Code : {code}")
                        print(f"    Stdout : {log['stdout'].strip() or 'None'}")
                        if log['stderr']:
                            print(f"    Stderr : {log['stderr'].strip()}")
                        print("-" * 40)
            return True
            
        elif base_cmd == "/history":
            print("\n--- Historique de discussion ---")
            if not self.history:
                print("Aucun échange enregistré.")
            else:
                for item in self.history:
                    role = "Jonathan (User)" if item["role"] == "user" else "RATISS"
                    print(f"[{role}] : {item['content']}")
            print("")
            return True
            
        return False

    def process_prompt(self, prompt: str):
        """Traite une requête de l'utilisateur."""
        # 1. Enregistrement historique utilisateur
        self.history.append({"role": "user", "content": prompt})

        # 2. Affichage des traces si mode activé
        if self.ratiss_active and self.view_reasoning:
            self.logger.print_trace(self.backend_id, prompt)
        elif not self.ratiss_active:
            print("\n[MOTEUR BRUT DIRECT - SANS RATISS]")
            print(f"> Appel direct de {self.backend_id}...")

        # 3. Génération de la réponse
        print("\nRATISS: [Analyse en cours...]")
        response = self.adapter.generate(self.backend_id, self.history, self.ratiss_active)
        
        # 4. Enregistrement historique assistant et affichage
        self.history.append({"role": "assistant", "content": response})
        print(f"\n{response}\n")

    def run(self):
        """Boucle principale interactive."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.draw_header()
        print("Tapez /help pour voir les commandes disponibles.")
        print("Configurez la variable OPENROUTER_API_KEY pour des requêtes réelles.\n")
        
        while True:
            try:
                user_input = input(">>> ").strip()
                if not user_input:
                    continue
                
                # Traitement des commandes
                if user_input.startswith("/"):
                    self.process_command(user_input)
                else:
                    self.process_prompt(user_input)
                    
            except KeyboardInterrupt:
                print("\n[*] Interruption détectée. Tapez /exit pour quitter.")
            except Exception as e:
                print(f"[-] Erreur inattendue : {e}")

if __name__ == "__main__":
    shell = RatissShell()
    shell.run()
