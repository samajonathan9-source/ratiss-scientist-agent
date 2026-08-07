#!/usr/bin/env python3
import sys
import base64
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="RATISS Parse Bridge - Décodage de payloads IA (Hex/Base64)")
    parser.add_argument("input", help="Fichier d'entrée contenant le dump texte (Hex ou Base64)")
    parser.add_argument("output", help="Fichier binaire de sortie")
    parser.add_argument("--format", choices=["hex", "b64", "auto"], default="auto", help="Format d'encodage (défaut: auto-détection)")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[-] Erreur: Le fichier d'entrée '{args.input}' n'existe pas.")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Nettoyage de la chaîne de caractères (retirer les retours à la ligne, espaces, backticks markdown, etc.)
    content = content.replace("`", "").replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    
    # Nettoyage préfixe si existant
    if content.lower().startswith("hex:"):
        content = content[4:]
    elif content.lower().startswith("0x"):
        content = content[2:]
    elif content.lower().startswith("base64:") or content.lower().startswith("b64:"):
        content = content[content.index(":") + 1:]

    decoded_bytes = None
    fmt = args.format

    if fmt == "auto":
        # Tentative en Hexadécimal d'abord
        try:
            decoded_bytes = bytes.fromhex(content)
            fmt = "hex"
            print("[+] Format hexadécimal détecté et décodé automatiquement.")
        except ValueError:
            # Sinon tentative en Base64
            try:
                # Ajout de padding si manquant
                missing_padding = len(content) % 4
                if missing_padding:
                    content += '=' * (4 - missing_padding)
                decoded_bytes = base64.b64decode(content)
                fmt = "b64"
                print("[+] Format Base64 détecté et décodé automatiquement.")
              except Exception:
                print("[-] Erreur: Impossible de décoder le contenu (ni Hex ni Base64 valide).")
                sys.exit(1)
    elif fmt == "hex":
        try:
            decoded_bytes = bytes.fromhex(content)
            print("[+] Décodage Hex réussi.")
        except ValueError as e:
            print(f"[-] Erreur de décodage Hex: {e}")
            sys.exit(1)
    elif fmt == "b64":
        try:
            missing_padding = len(content) % 4
            if missing_padding:
                content += '=' * (4 - missing_padding)
            decoded_bytes = base64.b64decode(content)
            print("[+] Décodage Base64 réussi.")
        except Exception as e:
            print(f"[-] Erreur de décodage Base64: {e}")
            sys.exit(1)

    if decoded_bytes:
        try:
            with open(args.output, "wb") as f:
                f.write(decoded_bytes)
            print(f"[+] Succès! Payload binaire généré : {args.output} ({len(decoded_bytes)} octets)")
        except Exception as e:
            print(f"[-] Erreur d'écriture dans le fichier de sortie: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
