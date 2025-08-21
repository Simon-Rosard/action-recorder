import time
import pyautogui
from typing import Optional
from app.models.recording_models import RecordedAction, ActionType, ClickButton
from app.services.recording_service import recording_service

class PlaybackService:
    def __init__(self):
        self.is_playing = False
        self.current_session_id: Optional[str] = None
    
    def play_session(self, session_id: str, speed_multiplier: float = 1.0, 
                    start_from: int = 0, end_at: Optional[int] = None):
        """Rejoue une session enregistrée."""
        if self.is_playing:
            raise ValueError("Playback is already active")
        
        session = recording_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        self.is_playing = True
        self.current_session_id = session_id
        
        try:
            actions = session.actions[start_from:end_at]
            if not actions:
                return
            
            # Temps de référence pour les délais
            start_time = actions[0].timestamp
            last_action_time = start_time
            
            for i, action in enumerate(actions):
                if not self.is_playing:
                    break
                
                # Calculer le délai depuis la dernière action
                time_diff = (action.timestamp - last_action_time).total_seconds()
                if time_diff > 0:
                    time.sleep(time_diff / speed_multiplier)
                
                # Exécuter l'action
                self._execute_action(action)
                last_action_time = action.timestamp
        
        finally:
            self.is_playing = False
            self.current_session_id = None
    
    def stop_playback(self):
        """Arrête la lecture en cours."""
        self.is_playing = False
    
    def _execute_action(self, action: RecordedAction):
        """Exécute une action enregistrée."""
        try:
            if action.action_type == ActionType.click:
                self._execute_click(action)
            elif action.action_type == ActionType.mouse_move:
                self._execute_mouse_move(action)
            elif action.action_type == ActionType.key_press:
                self._execute_key_press(action)
            elif action.action_type == ActionType.scroll:
                self._execute_scroll(action)
        except Exception as e:
            print(f"Erreur lors de l'exécution de l'action {action.id}: {e}")
    
    def _execute_click(self, action: RecordedAction):
        """Exécute un clic."""
        if action.x is None or action.y is None:
            return
        
        # Obtenir les dimensions actuelles de l'écran
        current_width, current_height = pyautogui.size()
        
        # Calculer les coordonnées absolues
        x = int(action.x * current_width)
        y = int(action.y * current_height)
        
        # Exécuter le clic selon le type de bouton
        if action.button == ClickButton.right:
            pyautogui.rightClick(x, y)
        elif action.button == ClickButton.middle:
            pyautogui.middleClick(x, y)
        else:
            pyautogui.click(x, y)
    
    def _execute_mouse_move(self, action: RecordedAction):
        """Exécute un mouvement de souris."""
        if action.x is None or action.y is None:
            return
        
        current_width, current_height = pyautogui.size()
        x = int(action.x * current_width)
        y = int(action.y * current_height)
        
        pyautogui.moveTo(x, y)
    
    def _execute_key_press(self, action: RecordedAction):
        """Exécute une pression de touche."""
        if not action.key:
            return
        
        try:
            # Gérer les touches spéciales
            if len(action.key) == 1:
                pyautogui.press(action.key)
            else:
                # Touches spéciales comme 'enter', 'space', etc.
                pyautogui.press(action.key.lower())
        except Exception as e:
            print(f"Impossible d'exécuter la touche '{action.key}': {e}")
    
    def _execute_scroll(self, action: RecordedAction):
        """Exécute un scroll."""
        if action.x is None or action.y is None:
            return
        
        current_width, current_height = pyautogui.size()
        x = int(action.x * current_width)
        y = int(action.y * current_height)
        
        # Se positionner à l'endroit du scroll
        pyautogui.moveTo(x, y)
        
        # Exécuter le scroll
        scroll_amount = action.scroll_amount or 3
        if action.scroll_direction == "up":
            pyautogui.scroll(scroll_amount)
        else:
            pyautogui.scroll(-scroll_amount)

# Instance globale du service
playback_service = PlaybackService()