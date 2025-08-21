# Action Recorder

Un service d'enregistrement et de lecture des actions utilisateur en temps réel.

## Fonctionnalités

- **Enregistrement en temps réel** : Capture automatiquement les clics, mouvements de souris, actions clavier et scroll
- **Sessions nommées** : Organisez vos enregistrements avec des noms personnalisés
- **Configuration flexible** : Activez/désactivez certains types d'actions, définissez des seuils
- **Sauvegarde persistante** : Les sessions sont automatiquement sauvegardées sur disque
- **Lecture avec contrôles** : Rejouez les sessions avec contrôle de vitesse et de plage
- **API REST complète** : Interface HTTP simple pour toutes les opérations

## Installation

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

Le service sera disponible sur `http://localhost:19000`

## Documentation API

Une fois le service lancé, consultez la documentation interactive sur :
- Swagger UI : `http://localhost:19000/docs`
- ReDoc : `http://localhost:19000/redoc`

## Utilisation

### Démarrer un enregistrement

```bash
curl -X POST "http://localhost:19000/api/recording/start" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ma session de test",
    "config": {
      "record_mouse_moves": true,
      "record_clicks": true,
      "record_keyboard": true,
      "record_scrolling": true,
      "mouse_move_threshold": 5
    }
  }'
```

### Arrêter l'enregistrement

```bash
curl -X POST "http://localhost:19000/api/recording/stop"
```

### Lister toutes les sessions

```bash
curl -X GET "http://localhost:19000/api/recording/sessions"
```

### Récupérer une session spécifique

```bash
curl -X GET "http://localhost:19000/api/recording/sessions/{session_id}"
```

### Rejouer une session

```bash
curl -X POST "http://localhost:19000/api/recording/playback" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "votre-session-id",
    "speed_multiplier": 1.0,
    "start_from_action": 0
  }'
```

### Supprimer une session

```bash
curl -X DELETE "http://localhost:19000/api/recording/sessions/{session_id}"
```

## Structure du projet

```
action-recorder/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── recording_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recording_service.py
│   │   └── playback_service.py
│   └── controller/
│       ├── __init__.py
│       └── recording_controller.py
├── recordings/                 # Dossier de sauvegarde des sessions
├── main.py
├── requirements.txt
├── start_app.sh
└── README.md
```

## Configuration

La configuration par défaut peut être modifiée lors du démarrage d'une session :

```json
{
  "record_mouse_moves": true,
  "record_clicks": true,
  "record_keyboard": true,
  "record_scrolling": true,
  "mouse_move_threshold": 5,
  "max_actions_per_session": 10000
}
```

- `record_mouse_moves` : Enregistrer les mouvements de souris
- `record_clicks` : Enregistrer les clics
- `record_keyboard` : Enregistrer les actions clavier
- `record_scrolling` : Enregistrer le scroll
- `mouse_move_threshold` : Seuil minimum de mouvement en pixels
- `max_actions_per_session` : Limite d'actions par session

## Format des données

### RecordedAction

Chaque action enregistrée contient :

```json
{
  "id": "uuid",
  "timestamp": "2024-01-01T12:00:00",
  "action_type": "click|key_press|mouse_move|scroll",
  "x": 0.5,
  "y": 0.5,
  "button": "left|right|middle",
  "key": "a",
  "scroll_direction": "up|down",
  "scroll_amount": 3,
  "screen_width": 1920,
  "screen_height": 1080
}
```

Les coordonnées `x` et `y` sont normalisées (0.0 à 1.0) pour s'adapter à différentes résolutions d'écran.

## Sécurité

⚠️ **Attention** : Ce service capture toutes les actions utilisateur, y compris les mots de passe tapés. Utilisez avec précaution et assurez-vous que :

- L'accès au service est restreint
- Les fichiers de session sont protégés
- Les sessions contenant des données sensibles sont supprimées après usage

## Limitations

- **Permissions** : Nécessite les permissions d'accessibilité sur macOS
- **Performance** : L'enregistrement des mouvements de souris peut générer beaucoup de données
- **Résolution** : La lecture peut ne pas être parfaite si la résolution d'écran a changé

## Dépannage

### Problèmes de permissions

Sur macOS, vous devrez peut-être autoriser l'application dans :
- Préférences Système > Sécurité et confidentialité > Accessibilité

Sur Linux, assurez-vous que l'utilisateur fait partie du groupe `input` :
```bash
sudo usermod -a -G input $USER
```

### Erreurs d'installation

Si vous rencontrez des problèmes avec `pynput`, installez les dépendances système :

**Ubuntu/Debian :**
```bash
sudo apt-get install python3-dev python3-xlib
```

**CentOS/RHEL :**
```bash
sudo yum install python3-devel libX11-devel
```

## Développement

### Ajouter de nouveaux types d'actions

1. Étendre l'enum `ActionType` dans `recording_models.py`
2. Ajouter la logique de capture dans `recording_service.py`
3. Ajouter la logique de lecture dans `playback_service.py`

### Tests

```bash
# Lancer les tests (à implémenter)
python -m pytest tests/
```

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.