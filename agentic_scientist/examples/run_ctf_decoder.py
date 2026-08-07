#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATISS Cypher ODV — CTF Auto-Base-Detector
Exemple d'utilisation pratique et démonstration
Jonathan Evina — RATISS Labs
"""

import os
import sys
import shutil

# Assurer l'accès au répertoire parent pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ctf_base_detector import detect_encoding, decode_file, batch_decode

import base64

def create_mock_challenges(demo_dir):
    """Crée des fichiers d'exemples encodés pour illustrer le fonctionnement."""
    os.makedirs(demo_dir, exist_ok=True)
    
    # 1. Base64 Standard
    b64_content = b"Q2hlciBKaW1teSwgbGUgZmxhZyBlc3QgOiBSQVRJU1N7N3BfMHBfMW5mMF9kM3QzY3QwcjN9"
    with open(os.path.join(demo_dir, "challenge_1_b64.txt"), "wb") as f:
        f.write(b64_content)
        
    # 2. Hexadécimal pur
    hex_content = b"5241544953537b6865785f616e616c797a65725f766f6c747d"
    with open(os.path.join(demo_dir, "challenge_2_hex.txt"), "wb") as f:
        f.write(hex_content)
        
    # 3. Base64 Inversée (Reversed Base64)
    # Original: "RATISS{reverse_engineering_master_class}" -> "UkFUSVNTe3JldmVyc2VfZW5naW5lZXJpbmdfbWFzdGVyX2NsYXNzfQ=="
    original_text = b"RATISS{reverse_engineering_master_class}"
    b64_encoded = base64.b64encode(original_text)
    b64_reversed = b64_encoded[::-1]
    with open(os.path.join(demo_dir, "challenge_3_reversed_b64.txt"), "wb") as f:
        f.write(b64_reversed)

def main():
    print("=" * 65)
    print("  RATISS Labs — CTF Auto-Base-Detector Demonstration")
    print("=" * 65)
    
    demo_dir = "ctf_demo_challenges"
    output_dir = "ctf_demo_decoded"
    
    print(f"[*] Génération de faux fichiers de CTF encodés dans '{demo_dir}'...")
    create_mock_challenges(demo_dir)
    print("[+] Fichiers d'exemples créés avec succès.\n")
    
    # Test 1 : Détection d'encodage sur flux brut
    print("[*] TEST 1 : Analyse directe de flux d'octets")
    test_bytes = b"==fXNzYWxjX3JldHNhbV9ncmllZW5pZ25lX2VzcmV2ZXJ9eVNTVVRBRlR"
    analysis = detect_encoding(test_bytes)
    print(f"  - Flux analysé : {test_bytes[:30].decode()}...")
    print(f"  - Encodage estimé : {analysis['encoding'].upper()}")
    print(f"  - Score de confiance : {analysis['confidence']}%")
    print(f"  - Inversion détectée : {analysis['is_reversed']}")
    print(f"  - Entropie spectrale : {analysis['entropy']:.4f}\n")
    
    # Test 2 : Décodage individuel de fichiers
    print("[*] TEST 2 : Décodage individuel de fichiers physiques")
    files_to_test = [
        "challenge_1_b64.txt",
        "challenge_2_hex.txt",
        "challenge_3_reversed_b64.txt"
    ]
    
    for filename in files_to_test:
        filepath = os.path.join(demo_dir, filename)
        print(f"  -> Analyse et décodage de : {filename}")
        decoded_text = decode_file(filepath, output_dir=output_dir)
        print(f"     Résultat décodé : {decoded_text.strip()}\n")
        
    # Test 3 : Traitement en Batch (Dossier entier en parallèle)
    print("[*] TEST 3 : Traitement global du dossier (Batch)")
    results = batch_decode(demo_dir, output_dir=output_dir, max_workers=2)
    
    print("\n[+] Résultats du traitement en Batch :")
    for filename, data in results.items():
        if data['status'] == 'success':
            print(f"  - {filename} : [SUCCÈS] -> {data['result'].strip()}")
        else:
            print(f"  - {filename} : [ERREUR] -> {data['error']}")
            
    print("\n[+] Tous les fichiers décodés ont été stockés dans le dossier :", output_dir)
    print("=" * 65)

if __name__ == "__main__":
    main()
