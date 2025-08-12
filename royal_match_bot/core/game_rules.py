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
    """Obstacles and special elements"""
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
    obstacle_layers: int = 1  # For multi-layer obstacles like boxes
    
    def is_empty(self) -> bool:
        return self.color == PieceColor.EMPTY
    
    def has_power_up(self) -> bool:
        return self.power_up is not None
    
    def has_obstacle(self) -> bool:
        return self.obstacle is not None

@dataclass
class Move:
    """Represents a possible move (piece swap)"""
    pos1: Tuple[int, int]  # (row, col) of first piece
    pos2: Tuple[int, int]  # (row, col) of second piece
    score: float = 0.0
    reasoning: str = ""
    
    def is_adjacent(self) -> bool:
        """Check if the two positions are adjacent"""
        row1, col1 = self.pos1
        row2, col2 = self.pos2
        return (abs(row1 - row2) == 1 and col1 == col2) or \
               (abs(col1 - col2) == 1 and row1 == row2)

@dataclass
class Objective:
    """Level objective information"""
    type: str  # "collect", "clear", "spread", etc.
    target: str  # color, obstacle type, etc.
    count: int  # target count
    current: int = 0  # current progress
    
    def is_complete(self) -> bool:
        return self.current >= self.count

# Scoring constants for move evaluation
SCORING_WEIGHTS = {
    # Objective progress (highest priority)
    "OBJECTIVE_PROGRESS": 100,
    
    # Power-up creation
    "LIGHT_BALL_CREATION": 100,
    "TNT_CREATION": 75,
    "ROCKET_CREATION": 50,
    "PROPELLER_CREATION": 40,
    
    # Power-up combinations
    "LIGHT_BALL_COMBO": 150,
    "TNT_TNT_COMBO": 100,
    "OTHER_COMBO": 75,
    
    # Cascade and board clearing
    "CASCADE_POTENTIAL": 25,
    "BOARD_CLEARING": 10,
    
    # Obstacle clearing
    "OBSTACLE_CLEARING": 30,
    
    # Match bonuses
    "MATCH_3": 5,
    "MATCH_4": 15,
    "MATCH_5": 30,
    "MATCH_6": 50,
}

# Power-up creation requirements
POWER_UP_REQUIREMENTS = {
    PowerUpType.ROCKET: 4,      # 4 in a line
    PowerUpType.TNT: 5,         # 5 in L/T shape
    PowerUpType.PROPELLER: 4,   # 4 in square
    PowerUpType.LIGHT_BALL: 5,  # 5+ in line
}

def is_valid_swap(pos1: Tuple[int, int], pos2: Tuple[int, int], board_size: int) -> bool:
    """Check if a swap between two positions is valid (adjacent)"""
    row1, col1 = pos1
    row2, col2 = pos2
    
    # Check bounds
    if not (0 <= row1 < board_size and 0 <= col1 < board_size and
            0 <= row2 < board_size and 0 <= col2 < board_size):
        return False
    
    # Check adjacency
    return (abs(row1 - row2) == 1 and col1 == col2) or \
           (abs(col1 - col2) == 1 and row1 == row2)

def get_adjacent_positions(pos: Tuple[int, int], board_size: int) -> List[Tuple[int, int]]:
    """Get all adjacent positions to a given position"""
    row, col = pos
    adjacent = []
    
    # Check all 4 directions
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < board_size and 0 <= new_col < board_size:
            adjacent.append((new_row, new_col))
    
    return adjacent

def count_matches_in_line(pieces: List[Piece]) -> int:
    """Count consecutive matching pieces in a line"""
    if not pieces:
        return 0
    
    max_count = 1
    current_count = 1
    current_color = pieces[0].color
    
    for piece in pieces[1:]:
        if piece.color == current_color and piece.color != PieceColor.EMPTY:
            current_count += 1
            max_count = max(max_count, current_count)
        else:
            current_count = 1
            current_color = piece.color
    
    return max_count

def can_create_power_up(pieces: List[Piece]) -> Optional[PowerUpType]:
    """Check if a line of pieces can create a power-up"""
    if not pieces:
        return None
    
    # Count consecutive matches
    match_count = count_matches_in_line(pieces)
    
    # Check for power-up creation
    for power_up, required in POWER_UP_REQUIREMENTS.items():
        if match_count >= required:
            return power_up
    
    return None