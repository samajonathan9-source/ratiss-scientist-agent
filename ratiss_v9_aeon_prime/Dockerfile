# Utiliser une image de base Python propre et légère
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système requises pour psutil et le calcul scientifique
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt .

# Installer les modules Python requis
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier la totalité des modules RATISS V9 Aeon Prime
COPY . .

# Exposer le port de service d'API REST
EXPOSE 3000

# Commande de démarrage par défaut (lance le serveur REST d'orchestration)
CMD ["python3", "run.py"]
