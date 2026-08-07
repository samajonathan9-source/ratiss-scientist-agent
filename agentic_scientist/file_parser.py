#!/usr/bin/env python3
"""
RATISS V9 AEON PRIME — Universal File Ingestion & Parsing Engine
Handles deep inspection of Images, PDFs, Spreadsheets, Molecular/CIF/PDB data, and Code/Text files.
"""

import sys
import os
import json
import base64
import hashlib

def parse_file(file_path):
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(filename)[1].lower()

    # Calculate Hashes
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)

    res = {
        "status": "success",
        "file_info": {
            "name": filename,
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024.0, 2),
            "extension": ext,
            "md5": md5_hash.hexdigest(),
            "sha256": sha256_hash.hexdigest()
        },
        "file_type": "unknown",
        "parsed_data": {},
        "summary": ""
    }

    # 1. IMAGE PARSING (PIL/Pillow)
    if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff']:
        res["file_type"] = "image"
        try:
            from PIL import Image, ExifTags
            with Image.open(file_path) as img:
                w, h = img.size
                mode = img.mode
                img_format = img.format
                
                exif_data = {}
                try:
                    raw_exif = img._getexif()
                    if raw_exif:
                        for tag, val in raw_exif.items():
                            tag_name = ExifTags.TAGS.get(tag, tag)
                            if isinstance(val, (str, int, float)):
                                exif_data[str(tag_name)] = str(val)
                except Exception:
                    pass

                # Convert small thumbnail to base64 for vision preview
                thumb = img.copy()
                thumb.thumbnail((800, 800))
                import io
                buf = io.BytesIO()
                save_fmt = "JPEG" if img_format in ["JPEG", "JPG"] else "PNG"
                thumb.save(buf, format=save_fmt)
                b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

                res["parsed_data"] = {
                    "width": w,
                    "height": h,
                    "aspect_ratio": round(w / float(h), 2) if h > 0 else 1.0,
                    "mode": mode,
                    "format": img_format,
                    "exif": exif_data,
                    "base64_preview": f"data:image/{save_fmt.lower()};base64,{b64_str}"
                }
                res["summary"] = f"📷 **Image {img_format}** ({w}x{h} px, Mode {mode})\n"
                if exif_data:
                    res["summary"] += f"  - Métadonnées EXIF : {len(exif_data)} champs extraits\n"
        except Exception as e:
            res["parsed_data"]["error"] = str(e)
            res["summary"] = f"📷 Image ({ext}) - Erreur de lecture Pillow: {e}"

    # 2. PDF PARSING (pypdf or fitz)
    elif ext == '.pdf':
        res["file_type"] = "pdf"
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            num_pages = len(reader.pages)
            meta = reader.metadata or {}
            
            extracted_text = []
            for i in range(min(num_pages, 10)):
                page_text = reader.pages[i].extract_text() or ""
                if page_text.strip():
                    extracted_text.append(f"--- Page {i+1} ---\n" + page_text.strip()[:1000])

            full_extracted = "\n\n".join(extracted_text)
            res["parsed_data"] = {
                "num_pages": num_pages,
                "author": str(meta.get('/Author', 'Inconnu')),
                "title": str(meta.get('/Title', 'Sans titre')),
                "creator": str(meta.get('/Creator', 'Inconnu')),
                "extracted_text_preview": full_extracted[:4000]
            }
            res["summary"] = f"📄 **Document PDF** ({num_pages} pages)\n"
            if full_extracted:
                res["summary"] += f"\n**Aperçu du contenu texte :**\n```\n{full_extracted[:1500]}\n```"
        except Exception as e:
            res["parsed_data"]["error"] = str(e)
            res["summary"] = f"📄 Document PDF - Analyse brute"

    # 3. EXCEL / CSV SPREADSHEETS
    elif ext in ['.csv', '.tsv', '.xlsx', '.xls']:
        res["file_type"] = "spreadsheet"
        try:
            import pandas as pd
            if ext == '.csv':
                df = pd.read_csv(file_path, nrows=50)
            elif ext == '.tsv':
                df = pd.read_csv(file_path, sep='\t', nrows=50)
            else:
                df = pd.read_excel(file_path, nrows=50)

            cols = list(df.columns)
            shape = df.shape
            summary_table = df.head(10).to_markdown()

            res["parsed_data"] = {
                "rows": shape[0],
                "columns": cols,
                "num_columns": len(cols),
                "markdown_preview": summary_table
            }
            res["summary"] = f"📊 **Tableau de données {ext.upper()}** ({shape[0]} lignes x {len(cols)} colonnes)\n"
            res["summary"] += f"  - **Colonnes :** `{', '.join(cols[:10])}`\n\n"
            res["summary"] += f"**Aperçu des données :**\n{summary_table}"
        except Exception as e:
            res["parsed_data"]["error"] = str(e)
            res["summary"] = f"📊 Fichier Tableur ({ext})"

    # 4. MOLECULAR / CIF / PDB DATA
    elif ext in ['.cif', '.pdb', '.ent', '.mol', '.sdf']:
        res["file_type"] = "bio_structure"
        try:
            import Bio.PDB
            parser = Bio.PDB.MMCIFParser(QUIET=True) if ext == '.cif' else Bio.PDB.PDBParser(QUIET=True)
            structure = parser.get_structure("uploaded", file_path)
            num_models = len(structure)
            atoms = list(structure.get_atoms())
            residues = list(structure.get_residues())
            
            res["parsed_data"] = {
                "models": num_models,
                "total_atoms": len(atoms),
                "total_residues": len(residues)
            }
            res["summary"] = f"🧬 **Structure Macromoléculaire ({ext.upper()})**\n  - Modèles : {num_models}\n  - Résidus/Acides aminés : {len(residues)}\n  - Atomes 3D : {len(atoms)}"
        except Exception as e:
            res["parsed_data"]["error"] = str(e)
            res["summary"] = f"🧬 Structure biologique ({ext})"

    # 5. TEXT / CODE FILES
    else:
        res["file_type"] = "text_or_binary"
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(30000)
            lines = content.splitlines()
            res["parsed_data"] = {
                "line_count": len(lines),
                "text_preview": content[:3000]
            }
            res["summary"] = f"📁 **Fichier Texte/Code** ({len(lines)} lignes)\n```\n{content[:1200]}\n```"
        except Exception as e:
            res["parsed_data"]["error"] = str(e)

    return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        out = parse_file(target)
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"error": "No file path provided"}))
