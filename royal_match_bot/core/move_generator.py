"""
Move generator module for Royal Match bot.
Finds and validates possible moves on the board.
"""

from typing import List, Tuple, Optional
from .board_parser import BoardState
from .game_rules import GameRules, PieceColor


class Move:
    """Represents a possible move (swap) on the board."""
    
    def __init__(self, pos1: Tuple[int, int], pos2: Tuple[int, int], score: float = 0.0):
        self.pos1 = pos1  # (row, col) of first piece
        self.pos2 = pos2  # (row, col) of second piece
        self.score = score
        self.matches = []  # Positions that will be matched
        self.reasoning = ""
    
    def __str__(self):
        return f"Move: {self.pos1} <-> {self.pos2} (Score: {self.score:.1f})"
    
    def __repr__(self):
        return self.__str__()


def find_all_possible_moves(board_state: BoardState) -> List[Move]:
    """
    Check every adjacent pair for valid swaps that create matches.
    
    Args:
        board_state: Current board state
        
    Returns:
        List of valid Move objects
    """
    possible_moves = []
    
    for row in range(board_state.rows):
        for col in range(board_state.cols):
            # Check right neighbor
            if col < board_state.cols - 1:
                move = check_swap_validity(board_state, (row, col), (row, col + 1))
                if move:
                    possible_moves.append(move)
            
            # Check down neighbor
            if row < board_state.rows - 1:
                move = check_swap_validity(board_state, (row, col), (row + 1, col))
                if move:
                    possible_moves.append(move)
    
    return possible_moves


def check_swap_validity(board_state: BoardState, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> Optional[Move]:
    """
    Check if swapping two positions creates valid matches.
    
    Args:
        board_state: Current board state
        pos1: First position to swap
        pos2: Second position to swap
        
    Returns:
        Move object if swap is valid, None otherwise
    """
    row1, col1 = pos1
    row2, col2 = pos2
    
    # Get pieces at both positions
    piece1 = board_state.get_piece(row1, col1)
    piece2 = board_state.get_piece(row2, col2)
    
    if not piece1 or not piece2:
        return None
    
    # Skip if either piece is empty or unknown
    if (piece1.get('color') in ['empty', 'unknown'] or 
        piece2.get('color') in ['empty', 'unknown']):
        return None
    
    # Create a temporary board state with swapped pieces
    temp_board = simulate_swap(board_state, pos1, pos2)
    
    # Check if the swap creates matches at either position
    matches1 = GameRules.find_matches(temp_board.board_matrix, pos1)
    matches2 = GameRules.find_matches(temp_board.board_matrix, pos2)
    
    all_matches = list(set(matches1 + matches2))
    
    if len(all_matches) >= 3:  # At least one match of 3+ pieces
        move = Move(pos1, pos2)
        move.matches = all_matches
        return move
    
    return None


def simulate_swap(board_state: BoardState, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> BoardState:
    """
    Create a new board state with two pieces swapped.
    
    Args:
        board_state: Original board state
        pos1: First position to swap
        pos2: Second position to swap
        
    Returns:
        New BoardState with pieces swapped
    """
    # Create a deep copy of the board state
    new_state = BoardState(board_state.rows, board_state.cols)
    
    # Copy all pieces
    for row in range(board_state.rows):
        for col in range(board_state.cols):
            piece = board_state.get_piece(row, col)
            if piece:
                new_state.set_piece(row, col, piece.copy())
            else:
                new_state.set_piece(row, col, None)
    
    # Swap the two pieces
    row1, col1 = pos1
    row2, col2 = pos2
    
    piece1 = new_state.get_piece(row1, col1)
    piece2 = new_state.get_piece(row2, col2)
    
    new_state.set_piece(row1, col1, piece2)
    new_state.set_piece(row2, col2, piece1)
    
    return new_state


def simulate_move_effects(board_state: BoardState, move: Move) -> BoardState:
    """
    Simulate the complete effects of a move including cascades.
    
    Args:
        board_state: Current board state
        move: Move to simulate
        
    Returns:
        Predicted board state after move and all cascades
    """
    # Start with the swapped board
    result_state = simulate_swap(board_state, move.pos1, move.pos2)
    
    # TODO: Implement cascade simulation
    # For now, just remove the matched pieces
    for match_pos in move.matches:
        row, col = match_pos
        result_state.set_piece(row, col, {
            'piece_type': 'empty',
            'color': 'empty',
            'power_up_type': None,
            'obstacle_type': None
        })
    
    # TODO: Add gravity simulation (pieces falling down)
    # TODO: Add power-up creation logic
    # TODO: Add cascade detection and recursive matching
    
    return result_state


def apply_gravity(board_state: BoardState) -> BoardState:
    """
    Apply gravity to make pieces fall down into empty spaces.
    
    Args:
        board_state: Board state to apply gravity to
        
    Returns:
        New board state with gravity applied
    """
    new_state = BoardState(board_state.rows, board_state.cols)
    
    # For each column, move non-empty pieces down
    for col in range(board_state.cols):
        pieces = []
        
        # Collect all non-empty pieces in this column
        for row in range(board_state.rows):
            piece = board_state.get_piece(row, col)
            if piece and piece.get('color') != 'empty':
                pieces.append(piece)
        
        # Place pieces at the bottom of the column
        for i, piece in enumerate(reversed(pieces)):
            row = board_state.rows - 1 - i
            new_state.set_piece(row, col, piece)
        
        # Fill remaining spaces with empty pieces
        for row in range(board_state.rows - len(pieces)):
            new_state.set_piece(row, col, {
                'piece_type': 'empty',
                'color': 'empty',
                'power_up_type': None,
                'obstacle_type': None
            })
    
    return new_state