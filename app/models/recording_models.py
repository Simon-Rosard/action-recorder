from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ActionType(str, Enum):
    click = "click"
    key_press = "key_press"
    key_release = "key_release"
    mouse_move = "mouse_move"
    scroll = "scroll"
    type_text = "type_text"

class ClickButton(str, Enum):
    left = "left"
    right = "right"
    middle = "middle"

class RecordedAction(BaseModel):
    id: Optional[str] = None
    timestamp: datetime
    action_type: ActionType
    x: Optional[float] = None
    y: Optional[float] = None
    button: Optional[ClickButton] = None
    key: Optional[str] = None
    text: Optional[str] = None
    scroll_direction: Optional[str] = None
    scroll_amount: Optional[int] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    additional_data: Optional[dict] = None

class RecordingSession(BaseModel):
    id: str
    name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    actions: List[RecordedAction] = []
    is_active: bool = True
    total_actions: int = 0

class RecordingConfig(BaseModel):
    record_mouse_moves: bool = True
    record_clicks: bool = True
    record_keyboard: bool = True
    record_scrolling: bool = True
    mouse_move_threshold: int = 5  # Minimum pixels to record mouse move
    max_actions_per_session: int = 10000

class SessionRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[RecordingConfig] = None

class PlaybackRequest(BaseModel):
    session_id: str
    speed_multiplier: float = 1.0
    start_from_action: int = 0
    end_at_action: Optional[int] = None