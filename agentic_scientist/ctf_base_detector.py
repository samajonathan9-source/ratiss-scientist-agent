#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATISS Cypher ODV — CTF Auto-Base-Detector
Module de détection et décodage automatique pour CTF
Jonathan Evina — RATISS Labs
Version 1.0.0
"""

import os
import base64
import binascii
import codecs
import math
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, Optional, List
import json

# --- CONSTANTES ---
BASE64_ALPHABET = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
BASE85_ALPHABET = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~')
BASE32_ALPHABET = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=')
HEX_ALPHABET = set('0123456789abcdefABCDEF')

# --- FONCTIONS DE BASE ---

def shannon_entropy(data: bytes) -> float:
    """Calcule l'entropie de Shannon d'un flux binaire."""
    if not data:
        return 0.0
    freq = Counter(data)
    length = len(data)
    entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())
    return entropy

def is_base64_like(data: bytes) -> float:
    """Retourne le ratio de caractères base64."""
    if not data:
        return 0.0
    try:
        text = data.decode('ascii', errors='ignore')
    except:
        return 0.0
    count = sum(1 for c in text if c in BASE64_ALPHABET)
    return count / len(text) if text else 0.0

def is_base85_like(data: bytes) -> float:
    """Retourne le ratio de caractères base85."""
    if not data:
        return 0.0
    try:
        text = data.decode('ascii', errors='ignore')
    except:
        return 0.0
    count = sum(1 for c in text if c in BASE85_ALPHABET)
    return count / len(text) if text else 0.0

def is_base32_like(data: bytes) -> float:
    """Retourne le ratio de caractères base32."""
    if not data:
        return 0.0
    try:
        text = data.decode('ascii', errors='ignore')
    except:
        return 0.0
    count = sum(1 for c in text if c in BASE32_ALPHABET)
    return count / len(text) if text else 0.0

def is_hex_like(data: bytes) -> float:
    """Retourne le ratio de caractères hexadécimaux."""
    if not data:
        return 0.0
    try:
        text = data.decode('ascii', errors='ignore')
    except:
        return 0.0
    count = sum(1 for c in text if c in HEX_ALPHABET)
    return count / len(text) if text else 0.0

def has_padding(data: bytes) -> bool:
    """Vérifie la présence de padding '='."""
    try:
        text = data.decode('ascii', errors='ignore')
        return '=' in text
    except:
        return False

def is_printable_utf8(decoded: bytes) -> Tuple[bool, float]:
    """Détermine si les octets décodés représentent du texte UTF-8 imprimable."""
    if not decoded:
        return True, 1.0
    try:
        text = decoded.decode('utf-8')
        printable = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
        ratio = printable / len(text) if text else 0.0
        return True, ratio
    except:
        try:
            text = decoded.decode('latin-1', errors='replace')
            printable = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
            ratio = printable / len(text) if text else 0.0
            return False, ratio * 0.5  # Pénaliser car ce n'est pas de l'UTF-8 valide
        except:
            return False, 0.0

def detect_encoding(data: bytes) -> Dict:
    """
    Détecte le type d'encodage d'un flux binaire.
    Retourne : dict avec 'encoding', 'confidence', 'is_reversed', 'entropy', 'suggested_decoding'
    """
    if not data:
        return {'encoding': 'empty', 'confidence': 100, 'is_reversed': False, 'entropy': 0.0, 'suggested_decoding': None}

    # Nettoyer les espaces blancs éventuels (courants en base64/hex)
    cleaned_data = b"".join(data.split())
    if not cleaned_data:
        cleaned_data = data

    entropy = shannon_entropy(cleaned_data)
    ratio_b64 = is_base64_like(cleaned_data)
    ratio_b85 = is_base85_like(cleaned_data)
    ratio_b32 = is_base32_like(cleaned_data)
    ratio_hex = is_hex_like(cleaned_data)

    # Détection d'inversion préliminaire
    is_reversed = False
    try:
        text = cleaned_data.decode('ascii', errors='ignore')
        if text.startswith('='):
            is_reversed = True
        elif '}' in text[:5] and '{' in text[-5:]:
            is_reversed = True
    except:
        pass

    # Définition des décodeurs possibles
    encodings = [
        ('hex', ratio_hex, binascii.unhexlify),
        ('base32', ratio_b32, base64.b32decode),
        ('base64', ratio_b64, base64.b64decode),
        ('base85', ratio_b85, lambda x: base64.b85decode(x) if hasattr(base64, 'b85decode') else None),
    ]

    best_encoding = None
    best_confidence = 0
    best_score = -1.0
    suggested_decoding = None

    # On teste dans les deux sens (normal et inversé) pour trouver le meilleur score sémantique
    for direction_reversed in [False, True]:
        current_data = cleaned_data[::-1] if direction_reversed else cleaned_data
        
        for name, ratio, decode_func in encodings:
            if ratio < 0.7:  # Doit avoir une bonne correspondance avec l'alphabet
                continue
                
            try:
                if decode_func is not None:
                    # Gérer des cas spécifiques
                    if name == 'hex':
                        # Pour hex, la longueur doit être paire
                        if len(current_data) % 2 != 0:
                            continue
                        decoded = decode_func(current_data)
                    elif name == 'base32':
                        # Ajouter du padding si nécessaire pour base32
                        missing_padding = len(current_data) % 8
                        padded = current_data
                        if missing_padding:
                            padded += b'=' * (8 - missing_padding)
                        decoded = decode_func(padded)
                    elif name == 'base64':
                        # Ajouter du padding si nécessaire pour base64
                        missing_padding = len(current_data) % 4
                        padded = current_data
                        if missing_padding:
                            padded += b'=' * (4 - missing_padding)
                        decoded = decode_func(padded)
                    else:
                        decoded = decode_func(current_data)

                    if decoded is not None:
                        is_utf8, printable_ratio = is_printable_utf8(decoded)
                        
                        # Système de score sémantique :
                        # - ratio d'alphabet (poids 0.3)
                        # - validité UTF-8 (poids 0.4)
                        # - proportion de caractères imprimables (poids 0.3)
                        score = (ratio * 0.3) + (0.4 if is_utf8 else 0.0) + (printable_ratio * 0.3)
                        
                        # Si le score sémantique est bon, on le préfère
                        if score > best_score:
                            best_score = score
                            best_encoding = name
                            best_confidence = ratio
                            is_reversed = direction_reversed
                            
            except Exception as e:
                pass

    # Si le score sémantique maximum est très bas, on n'a probablement pas d'encodage valide
    if best_score < 0.4:
        best_encoding = None

    # Si aucun encodage n'est détecté
    if best_encoding is None:
        if entropy < 4.5:
            best_encoding = 'text'
        else:
            best_encoding = 'binary'
        is_reversed = False

    # Déterminer la fonction de décodage finale
    if best_encoding == 'base64':
        def safe_b64decode(x):
            missing_padding = len(x) % 4
            if missing_padding:
                x += b'=' * (4 - missing_padding)
            return base64.b64decode(x)
        suggested_decoding = safe_b64decode
    elif best_encoding == 'base85':
        suggested_decoding = base64.b85decode if hasattr(base64, 'b85decode') else (lambda x: x)
    elif best_encoding == 'base32':
        def safe_b32decode(x):
            missing_padding = len(x) % 8
            if missing_padding:
                x += b'=' * (8 - missing_padding)
            return base64.b32decode(x)
        suggested_decoding = safe_b32decode
    elif best_encoding == 'hex':
        suggested_decoding = binascii.unhexlify
    else:
        suggested_decoding = lambda x: x

    return {
        'encoding': best_encoding,
        'confidence': int(best_confidence * 100) if best_encoding in ['base64', 'base85', 'base32', 'hex'] else 100,
        'is_reversed': is_reversed,
        'entropy': entropy,
        'suggested_decoding': suggested_decoding
    }

def decode_file(filepath: str, output_dir: Optional[str] = None) -> str:
    """
    Décode un fichier en utilisant RATISS CTF Auto-Base-Detector.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    result = detect_encoding(data)
    encoding = result['encoding']
    is_reversed = result['is_reversed']
    decode_func = result['suggested_decoding']

    if decode_func is None:
        return f"[ERROR] No decoding function found for {filepath}"

    try:
        if is_reversed:
            data = data[::-1]
        
        if encoding == 'hex':
            # Nettoyer les espaces et sauts de ligne
            clean_data = b"".join(data.split())
            decoded = decode_func(clean_data)
        else:
            decoded = decode_func(data)
        
        # Tenter de décoder en UTF-8
        try:
            result_text = decoded.decode('utf-8')
        except UnicodeDecodeError:
            result_text = decoded.decode('latin-1', errors='replace')
            result_text += "\n[WARNING] Non-UTF-8 characters replaced."
        
        # Si output_dir est fourni, écrire le fichier décodé
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            basename = os.path.basename(filepath)
            output_path = os.path.join(output_dir, f"{basename}.decoded.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result_text)
        
        return result_text
    except Exception as e:
        return f"[ERROR] Decoding failed for {filepath}: {str(e)}"

def batch_decode(input_dir: str, output_dir: Optional[str] = None, max_workers: int = 4) -> Dict[str, Dict]:
    """
    Décode tous les fichiers d'un dossier en parallèle.
    """
    if not os.path.isdir(input_dir):
        return {"error": f"Input directory '{input_dir}' not found."}

    files = []
    for root, dirs, filenames in os.walk(input_dir):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(decode_file, filepath, output_dir): filepath for filepath in files}
        for future in as_completed(future_to_file):
            filepath = future_to_file[future]
            try:
                result = future.result()
                results[os.path.basename(filepath)] = {
                    'status': 'success',
                    'result': result[:500] + '...' if len(result) > 500 else result,
                    'full_result': result
                }
            except Exception as e:
                results[os.path.basename(filepath)] = {
                    'status': 'error',
                    'error': str(e)
                }

    return results

if __name__ == "__main__":
    # Exemple d'utilisation
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ctf_base_detector.py <file_or_directory>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isfile(path):
        result = decode_file(path, "decoded")
        print(f"Decoded content:\n{result}")
    elif os.path.isdir(path):
        results = batch_decode(path, "decoded", max_workers=4)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"Error: '{path}' is not a valid file or directory.")
