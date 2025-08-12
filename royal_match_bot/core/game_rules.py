"""
Game rules module for Royal Match bot.
Defines game mechanics, piece types, and power-up rules.
"""

from enum import Enum
from typing import List, Tuple


class PieceColor(Enum):
    """Enumeration of piece colors in Royal Match."""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"
    EMPTY = "empty"


class PowerUpType(Enum):
    """Enumeration of power-up types."""
    ROCKET = "rocket"
    TNT = "tnt"
    PROPELLER = "propeller"
    LIGHT_BALL = "light_ball"
    NONE = None


class ObstacleType(Enum):
    """Enumeration of obstacle types."""
    BOX = "box"
    CHAIN = "chain"
    JELLY = "jelly"
    VASE = "vase"
    NONE = None


class GameRules:
    """Contains Royal Match game rules and mechanics."""
    
    @staticmethod
    def is_valid_swap(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Check if two positions can be swapped (must be adjacent).
        
        Args:
            pos1: First position (row, col)
            pos2: Second position (row, col)
            
        Returns:
            True if positions are adjacent
        """
        row1, col1 = pos1
        row2, col2 = pos2
        
        # Check if positions are adjacent (horizontally or vertically)
        row_diff = abs(row1 - row2)
        col_diff = abs(col1 - col2)
        
        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    @staticmethod
    def find_matches(board_matrix: List[List[dict]], pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find all matching pieces starting from a position.
        
        Args:
            board_matrix: 2D board matrix
            pos: Starting position (row, col)
            
        Returns:
            List of positions that form matches
        """
        row, col = pos
        if not board_matrix or not board_matrix[row][col]:
            return []
        
        piece_color = board_matrix[row][col].get('color')
        if piece_color == 'empty' or piece_color == 'unknown':
            return []
        
        matches = []
        rows = len(board_matrix)
        cols = len(board_matrix[0])
        
        # Check horizontal matches
        horizontal_matches = [pos]
        
        # Check left
        c = col - 1
        while c >= 0 and board_matrix[row][c] and board_matrix[row][c].get('color') == piece_color:
            horizontal_matches.append((row, c))
            c -= 1
        
        # Check right
        c = col + 1
        while c < cols and board_matrix[row][c] and board_matrix[row][c].get('color') == piece_color:
            horizontal_matches.append((row, c))
            c += 1
        
        if len(horizontal_matches) >= 3:
            matches.extend(horizontal_matches)
        
        # Check vertical matches
        vertical_matches = [pos]
        
        # Check up
        r = row - 1
        while r >= 0 and board_matrix[r][col] and board_matrix[r][col].get('color') == piece_color:
            vertical_matches.append((r, col))
            r -= 1
        
        # Check down
        r = row + 1
        while r < rows and board_matrix[r][col] and board_matrix[r][col].get('color') == piece_color:
            vertical_matches.append((r, col))
            r += 1
        
        if len(vertical_matches) >= 3:
            matches.extend(vertical_matches)
        
        # Remove duplicates
        return list(set(matches))
    
    @staticmethod
    def get_power_up_for_match(match_length: int, match_shape: str) -> PowerUpType:
        """
        Determine what power-up is created for a given match.
        
        Args:
            match_length: Number of pieces in the match
            match_shape: Shape of the match ('line', 'L', 'T', 'square')
            
        Returns:
            PowerUpType that should be created
        """
        if match_length >= 5:
            return PowerUpType.LIGHT_BALL
        elif match_length == 4:
            if match_shape in ['L', 'T']:
                return PowerUpType.TNT
            elif match_shape == 'square':
                return PowerUpType.PROPELLER
            else:  # line
                return PowerUpType.ROCKET
        else:
            return PowerUpType.NONE
    
    @staticmethod
    def get_power_up_combination_effect(power1: PowerUpType, power2: PowerUpType) -> dict:
        """
        Get the effect of combining two power-ups.
        
        Args:
            power1: First power-up type
            power2: Second power-up type
            
        Returns:
            Dictionary describing the combination effect
        """
        combinations = {
            (PowerUpType.ROCKET, PowerUpType.ROCKET): {
                'effect': 'cross_clear',
                'description': 'Clears row AND column'
            },
            (PowerUpType.TNT, PowerUpType.TNT): {
                'effect': 'large_explosion',
                'description': 'Clears 5x5 area'
            },
            (PowerUpType.LIGHT_BALL, PowerUpType.ROCKET): {
                'effect': 'convert_to_rockets',
                'description': 'Converts all pieces of target color to rockets'
            },
            (PowerUpType.LIGHT_BALL, PowerUpType.TNT): {
                'effect': 'convert_to_tnt',
                'description': 'Converts all pieces of target color to TNT'
            },
            (PowerUpType.LIGHT_BALL, PowerUpType.LIGHT_BALL): {
                'effect': 'clear_board',
                'description': 'Clears entire board'
            }
        }
        
        # Try both orders of power-ups
        key = (power1, power2)
        if key in combinations:
            return combinations[key]
        
        key = (power2, power1)
        if key in combinations:
            return combinations[key]
        
        return {
            'effect': 'both_activate',
            'description': 'Both power-ups activate separately'
        }