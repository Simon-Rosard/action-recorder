FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-xlib \
    libx11-dev \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    xvfb \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer le répertoire pour les enregistrements
RUN mkdir -p /app/recordings

# Exposer le port
EXPOSE 19000

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PORT=19000

# Commande de démarrage
CMD ["python", "main.py"]