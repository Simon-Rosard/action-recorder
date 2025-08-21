import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pynput import mouse, keyboard
import pyautogui
import threading
import time
from app.models.recording_models import (
    RecordedAction, RecordingSession, ActionType, 
    ClickButton, RecordingConfig
)

class RecordingService:
    def __init__(self):
        self.sessions: Dict[str, RecordingSession] = {}
        self.active_session_id: Optional[str] = None
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.is_recording = False
        self.config = RecordingConfig()
        self.last_mouse_position = (0, 0)
        self.data_dir = "recordings"
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Crée le dossier de données s'il n'existe pas."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def start_recording(self, session_name: Optional[str] = None, config: Optional[RecordingConfig] = None) -> str:
        """Démarre un nouvel enregistrement."""
        if self.is_recording:
            raise ValueError("Recording is already active")
        
        session_id = str(uuid.uuid4())
        if config:
            self.config = config
        
        session = RecordingSession(
            id=session_id,
            name=session_name or f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now()
        )
        
        self.sessions[session_id] = session
        self.active_session_id = session_id
        self.is_recording = True
        
        # Démarrer les listeners
        self._start_listeners()
        
        return session_id
    
    def stop_recording(self) -> Optional[RecordingSession]:
        """Arrête l'enregistrement actuel."""
        if not self.is_recording or not self.active_session_id:
            return None
        
        session = self.sessions[self.active_session_id]
        session.end_time = datetime.now()
        session.is_active = False
        
        # Arrêter les listeners
        self._stop_listeners()
        
        # Sauvegarder la session
        self._save_session(session)
        
        self.is_recording = False
        active_session = self.sessions[self.active_session_id]
        self.active_session_id = None
        
        return active_session
    
    def _start_listeners(self):
        """Démarre les listeners pour capturer les événements."""
        if self.config.record_clicks or self.config.record_mouse_moves:
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_scroll
            )
            self.mouse_listener.start()
        
        if self.config.record_keyboard:
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
    
    def _stop_listeners(self):
        """Arrête tous les listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
    
    def _on_mouse_move(self, x, y):
        """Callback pour les mouvements de souris."""
        if not self.is_recording or not self.config.record_mouse_moves:
            return
        
        # Vérifier le seuil de mouvement
        if abs(x - self.last_mouse_position[0]) < self.config.mouse_move_threshold and \
           abs(y - self.last_mouse_position[1]) < self.config.mouse_move_threshold:
            return
        
        self.last_mouse_position = (x, y)
        screen_width, screen_height = pyautogui.size()
        
        action = RecordedAction(
            timestamp=datetime.now(),
            action_type=ActionType.mouse_move,
            x=x / screen_width,
            y=y / screen_height,
            screen_width=screen_width,
            screen_height=screen_height
        )
        
        self._add_action(action)
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Callback pour les clics de souris."""
        if not self.is_recording or not self.config.record_clicks:
            return
        
        if pressed:  # Seulement enregistrer les clics, pas les relâchements
            screen_width, screen_height = pyautogui.size()
            
            # Mapper le bouton
            button_map = {
                mouse.Button.left: ClickButton.left,
                mouse.Button.right: ClickButton.right,
                mouse.Button.middle: ClickButton.middle
            }
            
            action = RecordedAction(
                timestamp=datetime.now(),
                action_type=ActionType.click,
                x=x / screen_width,
                y=y / screen_height,
                button=button_map.get(button, ClickButton.left),
                screen_width=screen_width,
                screen_height=screen_height
            )
            
            self._add_action(action)
    
    def _on_scroll(self, x, y, dx, dy):
        """Callback pour le scroll."""
        if not self.is_recording or not self.config.record_scrolling:
            return
        
        screen_width, screen_height = pyautogui.size()
        direction = "up" if dy > 0 else "down"
        
        action = RecordedAction(
            timestamp=datetime.now(),
            action_type=ActionType.scroll,
            x=x / screen_width,
            y=y / screen_height,
            scroll_direction=direction,
            scroll_amount=abs(dy),
            screen_width=screen_width,
            screen_height=screen_height
        )
        
        self._add_action(action)
    
    def _on_key_press(self, key):
        """Callback pour les touches pressées."""
        if not self.is_recording or not self.config.record_keyboard:
            return
        
        key_str = self._format_key(key)
        
        action = RecordedAction(
            timestamp=datetime.now(),
            action_type=ActionType.key_press,
            key=key_str
        )
        
        self._add_action(action)
    
    def _on_key_release(self, key):
        """Callback pour les touches relâchées."""
        if not self.is_recording or not self.config.record_keyboard:
            return
        
        key_str = self._format_key(key)
        
        action = RecordedAction(
            timestamp=datetime.now(),
            action_type=ActionType.key_release,
            key=key_str
        )
        
        self._add_action(action)
    
    def _format_key(self, key) -> str:
        """Formate une touche pour l'enregistrement."""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char
            else:
                return str(key).replace('Key.', '')
        except:
            return str(key)
    
    def _add_action(self, action: RecordedAction):
        """Ajoute une action à la session active."""
        if not self.active_session_id or self.active_session_id not in self.sessions:
            return
        
        session = self.sessions[self.active_session_id]
        
        # Vérifier la limite d'actions
        if len(session.actions) >= self.config.max_actions_per_session:
            return
        
        action.id = str(uuid.uuid4())
        session.actions.append(action)
        session.total_actions = len(session.actions)
    
    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """Récupère une session par son ID."""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[RecordingSession]:
        """Récupère toutes les sessions."""
        return list(self.sessions.values())
    
    def delete_session(self, session_id: str) -> bool:
        """Supprime une session."""
        if session_id in self.sessions:
            # Supprimer le fichier de sauvegarde
            file_path = os.path.join(self.data_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            del self.sessions[session_id]
            return True
        return False
    
    def _save_session(self, session: RecordingSession):
        """Sauvegarde une session sur disque."""
        file_path = os.path.join(self.data_dir, f"{session.id}.json")
        
        # Convertir en dict pour la sérialisation JSON
        session_data = {
            "id": session.id,
            "name": session.name,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "is_active": session.is_active,
            "total_actions": session.total_actions,
            "actions": [
                {
                    "id": action.id,
                    "timestamp": action.timestamp.isoformat(),
                    "action_type": action.action_type,
                    "x": action.x,
                    "y": action.y,
                    "button": action.button,
                    "key": action.key,
                    "text": action.text,
                    "scroll_direction": action.scroll_direction,
                    "scroll_amount": action.scroll_amount,
                    "screen_width": action.screen_width,
                    "screen_height": action.screen_height,
                    "additional_data": action.additional_data
                }
                for action in session.actions
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def load_sessions(self):
        """Charge les sessions sauvegardées depuis le disque."""
        if not os.path.exists(self.data_dir):
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # Reconvertir les données
                    actions = []
                    for action_data in session_data.get('actions', []):
                        action = RecordedAction(
                            id=action_data.get('id'),
                            timestamp=datetime.fromisoformat(action_data['timestamp']),
                            action_type=ActionType(action_data['action_type']),
                            x=action_data.get('x'),
                            y=action_data.get('y'),
                            button=ClickButton(action_data['button']) if action_data.get('button') else None,
                            key=action_data.get('key'),
                            text=action_data.get('text'),
                            scroll_direction=action_data.get('scroll_direction'),
                            scroll_amount=action_data.get('scroll_amount'),
                            screen_width=action_data.get('screen_width'),
                            screen_height=action_data.get('screen_height'),
                            additional_data=action_data.get('additional_data')
                        )
                        actions.append(action)
                    
                    session = RecordingSession(
                        id=session_data['id'],
                        name=session_data.get('name'),
                        start_time=datetime.fromisoformat(session_data['start_time']),
                        end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
                        actions=actions,
                        is_active=session_data.get('is_active', False),
                        total_actions=session_data.get('total_actions', len(actions))
                    )
                    
                    self.sessions[session.id] = session
                    
                except Exception as e:
                    print(f"Erreur lors du chargement de la session {filename}: {e}")

# Instance globale du service
recording_service = RecordingService()