from enum import Enum

class type_player(Enum):
    PLAYER = "player"
    COMPUTER = "computer"

class GameMode(Enum):
    WEAK_AI = "weak_ai"
    STRONG_AI = "strong_ai"
    FRIEND = "friend"

class ShipOrientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class AIType(Enum):
    WEAK = "weak_ai"
    STRONG = "strong_ai"

class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    MEDIUM_GRAY = (128, 128, 128)
    LIGHT_GRAY = (240, 240, 240)
    PALE_GRAY = (180, 180, 180)
