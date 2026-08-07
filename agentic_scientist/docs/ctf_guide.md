# RATISS Cypher ODV — CTF Auto-Base-Detector
## Guide d'Utilisation & Spécifications Topologiques

### Introduction
Le module `ctf_base_detector.py` est un outil d'analyse et de décodage automatisé conçu spécialement pour les épreuves de type **Capture The Flag (CTF)**. Intégré à la suite logicielle souveraine **RATISS Cypher ODV**, il applique des principes d'entropie sémantique et de distribution statistique de caractères pour détecter, nettoyer, désinverser et décoder des flux d'informations encodés de façon non triviale.

---

### Fonctionnalités Clés
1. **Analyse de Distribution Spectrale** : Évalue le dictionnaire et l'alphabet probabiliste du flux d'entrée (ratio de caractères base64, base85, base32, hex, etc.).
2. **Évaluation d'Entropie de Shannon** : Identifie l'énergie informationnelle globale pour classifier les données entre texte brut, binaire pur, ou flux encodé à haute densité de compression.
3. **Détection Automatique d'Inversion (Reversed Data)** : Repère les indices de flux écrits de droite à gauche (comme les paddings `==` en tête de chaîne ou les structures d'encadrement inversées comme `}FTC{`).
4. **Décapsulage Parallélisé en Batch** : Parcourt récursivement des répertoires entiers pour analyser et décoder des dizaines de fichiers simultanément via un moteur de threads multi-cœurs.

---

### Architecture & API Python

#### 1. `detect_encoding(data: bytes) -> dict`
Analyse le spectre sémantique des données binaires et en extrait un diagnostic de phase complet.

**Structure du Retour :**
```python
{
    'encoding': 'base64' | 'base85' | 'base32' | 'hex' | 'binary' | 'text' | 'empty',
    'confidence': int (0 - 100),
    'is_reversed': bool,
    'entropy': float,
    'suggested_decoding': function
}
```

#### 2. `decode_file(filepath: str, output_dir: str = None) -> str`
Lit un fichier, en extrait la signature topologique, applique les corrections d'inversion nécessaires, effectue le décodage et écrit le résultat si un répertoire de sortie est spécifié.

#### 3. `batch_decode(input_dir: str, output_dir: str = None, max_workers: int = 4) -> dict`
Utilise un `ThreadPoolExecutor` pour exécuter le pipeline de décodage en parallèle sur une collection de fichiers.

---

### Exemples d'Utilisation

#### Utilisation en Ligne de Commande
Pour analyser et décoder un unique fichier mystère :
```bash
python3 src/ctf_base_detector.py chemin/vers/le/fichier_mystere.txt
```

Pour traiter tout un dossier de challenges CTF en batch :
```bash
python3 src/ctf_base_detector.py chemin/vers/le/dossier_ctf/
```

#### Exemple d'Intégration Programmatrice
```python
from src.ctf_base_detector import detect_encoding, decode_file

# Données brutes
raw_data = b"==gMyV2bgI2bgI2b"  # Base64 inversée
info = detect_encoding(raw_data)

print(f"Encodage détecté : {info['encoding']} (Confiance : {info['confidence']}%)")
print(f"Inversé : {info['is_reversed']}")

# Décoder le fichier directement
decoded_text = decode_file("secret.enc", output_dir="results")
print(decoded_text)
```

---
*Jonathan Evina — RATISS Labs*
*Version 1.0.0 — Juil 2026*
