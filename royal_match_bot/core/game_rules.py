"""
Royal Match Game Rules and Constants
Defines the core game mechanics, piece types, and scoring system.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

class PieceColor(Enum):
    """Basic piece colors in Royal Match"""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"
    EMPTY = "empty"

class PowerUpType(Enum):
    """Special power-up pieces"""
    ROCKET = "rocket"          # 4 in a line
    TNT = "tnt"               # 5 in L/T shape
    PROPELLER = "propeller"    # 4 in square
    LIGHT_BALL = "light_ball"  # 5+ in line

class ObstacleType(Enum):
    """Obstacles that block gameplay"""
    BOX = "box"
    CHAIN = "chain"
    JELLY = "jelly"
    VASE = "vase"
    POT = "pot"

@dataclass
class Piece:
    """Represents a single piece on the board"""
    color: PieceColor
    power_up: Optional[PowerUpType] = None
    obstacle: Optional[ObstacleType] = None
    obstacle_layers: int = 0  # For multi-layer obstacles like boxes
    
    def is_empty(self) -> bool:
        return self.color == PieceColor.EMPTY
    
    def is_power_up(self) -> bool:
        return self.power_up is not None
    
    def has_obstacle(self) -> bool:
        return self.obstacle is not None

@dataclass
class Move:
    """Represents a possible move on the board"""
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    score: int = 0
    reasoning: str = ""
    
    def is_horizontal(self) -> bool:
        return self.from_pos[0] == self.to_pos[0]
    
    def is_vertical(self) -> bool:
        return self.from_pos[1] == self.to_pos[1]

@dataclass
class Objective:
    """Level objective information"""
    type: str  # "collect", "clear", "spread", etc.
    target: str  # color, obstacle type, etc.
    amount: int
    current: int = 0
    
    @property
    def progress(self) -> float:
        return self.current / self.amount if self.amount > 0 else 0.0

# Scoring constants
SCORE_WEIGHTS = {
    'objective_progress': 100,
    'power_up_creation': {
        PowerUpType.LIGHT_BALL: 100,
        PowerUpType.TNT: 75,
        PowerUpType.ROCKET: 50,
        PowerUpType.PROPELLER: 40
    },
    'power_up_combination': 75,
    'cascade_potential': 25,
    'board_clearing': 10,
    'obstacle_clearing': 30
}

# Match requirements
MIN_MATCH_LENGTH = 3
POWER_UP_REQUIREMENTS = {
    PowerUpType.ROCKET: 4,      # 4 in a line
    PowerUpType.TNT: 5,         # 5 in L/T shape
    PowerUpType.PROPELLER: 4,   # 4 in square
    PowerUpType.LIGHT_BALL: 5   # 5+ in line
}

def is_valid_match(pieces: List[Piece]) -> bool:
    """Check if a sequence of pieces forms a valid match"""
    if len(pieces) < MIN_MATCH_LENGTH:
        return False
    
    # All pieces must be the same color and not empty
    first_color = pieces[0].color
    if first_color == PieceColor.EMPTY:
        return False
    
    return all(piece.color == first_color for piece in pieces)

def get_power_up_type(match_length: int, match_shape: str = "line") -> Optional[PowerUpType]:
    """Determine what power-up should be created based on match"""
    if match_length >= 5:
        return PowerUpType.LIGHT_BALL
    elif match_length == 4:
        if match_shape == "square":
            return PowerUpType.PROPELLER
        else:
            return PowerUpType.ROCKET
    elif match_length == 5 and match_shape in ["L", "T"]:
        return PowerUpType.TNT
    
    return None

def calculate_cascade_score(matches: List[List[Tuple[int, int]]]) -> int:
    """Calculate bonus score for cascade effects"""
    if len(matches) <= 1:
        return 0
    
    # Bonus for each additional match in cascade
    return (len(matches) - 1) * SCORE_WEIGHTS['cascade_potential']