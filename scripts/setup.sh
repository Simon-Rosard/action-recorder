#!/bin/bash

# Script de configuration pour Action Recorder

echo "=== Configuration d'Action Recorder ==="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
echo "❌ Python 3 n'est pas installé"
exit 1
fi

echo "✅ Python 3 détecté"

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le dossier recordings
mkdir -p recordings

# Vérifier les permissions (Linux/macOS)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
echo "🐧 Système Linux détecté"
echo "⚠️  Assurez-vous que votre utilisateur fait partie du groupe 'input':"
echo "   sudo usermod -a -G input $USER"
echo "   Puis redémarrez votre session"
elif [[ "$OSTYPE" == "darwin"* ]]; then
echo "🍎 Système macOS détecté"
echo "⚠️  Autorisations nécessaires :"
echo "   - Aller dans Préférences Système > Sécurité et confidentialité"
echo "   - Onglet 'Confidentialité' > 'Accessibilité'"
echo "   - Ajouter Terminal ou votre IDE à la liste"
fi

echo ""
echo "✅ Configuration terminée !"
echo ""
echo "🚀 Pour démarrer le service :"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "📖 Documentation : http://localhost:19000/docs"
