"""
Move Generator Module for Royal Match Bot
Handles finding valid moves and simulating their effects.
"""

import numpy as np
from typing import List, Tuple, Optional, Set
import logging

from .game_rules import Piece, PieceColor, PowerUpType, Move, is_valid_match, get_power_up_type
from .game_rules import MIN_MATCH_LENGTH

logger = logging.getLogger(__name__)

class MoveGenerator:
    """Generates and validates possible moves on the board"""
    
    def __init__(self):
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
    
    def find_all_possible_moves(self, board_matrix: np.ndarray) -> List[Move]:
        """
        Find all valid moves that create 3+ matches
        
        Args:
            board_matrix: 2D array of Piece objects
            
        Returns:
            List of valid Move objects
        """
        try:
            if board_matrix.size == 0:
                return []
            
            valid_moves = []
            rows, cols = board_matrix.shape
            
            # Check each adjacent pair for valid swaps
            for row in range(rows):
                for col in range(cols):
                    # Check all four directions
                    for dr, dc in self.directions:
                        new_row, new_col = row + dr, col + dc
                        
                        # Check bounds
                        if not (0 <= new_row < rows and 0 <= new_col < cols):
                            continue
                        
                        # Skip if we've already checked this pair
                        if (new_row, new_col) < (row, col):
                            continue
                        
                        # Check if swap creates a valid match
                        if self._would_create_match(board_matrix, row, col, new_row, new_col):
                            move = Move(
                                from_pos=(row, col),
                                to_pos=(new_row, new_col)
                            )
                            valid_moves.append(move)
            
            logger.info(f"Found {len(valid_moves)} valid moves")
            return valid_moves
            
        except Exception as e:
            logger.error(f"Error finding valid moves: {e}")
            return []
    
    def _would_create_match(self, board_matrix: np.ndarray, row1: int, col1: int, 
                           row2: int, col2: int) -> bool:
        """
        Check if swapping two pieces would create a valid match
        
        Args:
            board_matrix: Current board state
            row1, col1: Position of first piece
            row2, col2: Position of second piece
            
        Returns:
            True if swap creates a match, False otherwise
        """
        try:
            # Create a copy of the board for simulation
            test_board = board_matrix.copy()
            
            # Swap the pieces
            test_board[row1, col1], test_board[row2, col2] = \
                test_board[row2, col2], test_board[row1, col1]
            
            # Check if either piece is now part of a match
            return (self._has_match_at(test_board, row1, col1) or 
                   self._has_match_at(test_board, row2, col2))
            
        except Exception as e:
            logger.error(f"Error checking match creation: {e}")
            return False
    
    def _has_match_at(self, board_matrix: np.ndarray, row: int, col: int) -> bool:
        """
        Check if there's a match involving the piece at the given position
        
        Args:
            board_matrix: Board state to check
            row, col: Position to check
            
        Returns:
            True if there's a match, False otherwise
        """
        try:
            piece = board_matrix[row, col]
            if piece is None or piece.is_empty():
                return False
            
            # Check horizontal matches
            horizontal_match = self._check_line_match(board_matrix, row, col, 0, 1)
            
            # Check vertical matches
            vertical_match = self._check_line_match(board_matrix, row, col, 1, 0)
            
            return horizontal_match or vertical_match
            
        except Exception as e:
            logger.error(f"Error checking match at position: {e}")
            return False
    
    def _check_line_match(self, board_matrix: np.ndarray, row: int, col: int, 
                         dr: int, dc: int) -> bool:
        """
        Check for matches in a line (horizontal or vertical)
        
        Args:
            board_matrix: Board state to check
            row, col: Starting position
            dr, dc: Direction vector
            
        Returns:
            True if there's a match of 3+ pieces
        """
        try:
            piece = board_matrix[row, col]
            if piece is None or piece.is_empty():
                return False
            
            # Count consecutive pieces of the same color
            count = 1
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while (0 <= r < board_matrix.shape[0] and 
                   0 <= c < board_matrix.shape[1] and
                   board_matrix[r, c] is not None and
                   not board_matrix[r, c].is_empty() and
                   board_matrix[r, c].color == piece.color):
                count += 1
                r += dr
                c += dc
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while (0 <= r < board_matrix.shape[0] and 
                   0 <= c < board_matrix.shape[1] and
                   board_matrix[r, c] is not None and
                   not board_matrix[r, c].is_empty() and
                   board_matrix[r, c].color == piece.color):
                count += 1
                r -= dr
                c -= dc
            
            return count >= MIN_MATCH_LENGTH
            
        except Exception as e:
            logger.error(f"Error checking line match: {e}")
            return False
    
    def find_matches(self, board_matrix: np.ndarray) -> List[List[Tuple[int, int]]]:
        """
        Find all current matches on the board
        
        Args:
            board_matrix: Board state to analyze
            
        Returns:
            List of match positions (each match is a list of (row, col) tuples)
        """
        try:
            if board_matrix.size == 0:
                return []
            
            matches = []
            rows, cols = board_matrix.shape
            visited = set()
            
            # Check each position for matches
            for row in range(rows):
                for col in range(cols):
                    if (row, col) in visited:
                        continue
                    
                    piece = board_matrix[row, col]
                    if piece is None or piece.is_empty():
                        continue
                    
                    # Check horizontal matches
                    horizontal_match = self._get_line_match(board_matrix, row, col, 0, 1, visited)
                    if horizontal_match:
                        matches.append(horizontal_match)
                    
                    # Check vertical matches
                    vertical_match = self._get_line_match(board_matrix, row, col, 1, 0, visited)
                    if vertical_match:
                        matches.append(vertical_match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            return []
    
    def _get_line_match(self, board_matrix: np.ndarray, row: int, col: int, 
                        dr: int, dc: int, visited: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """
        Get the positions of pieces in a line match
        
        Args:
            board_matrix: Board state to check
            row, col: Starting position
            dr, dc: Direction vector
            visited: Set of already visited positions
            
        Returns:
            List of match positions or None if no match
        """
        try:
            piece = board_matrix[row, col]
            if piece is None or piece.is_empty():
                return None
            
            match_positions = [(row, col)]
            visited.add((row, col))
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while (0 <= r < board_matrix.shape[0] and 
                   0 <= c < board_matrix.shape[1] and
                   board_matrix[r, c] is not None and
                   not board_matrix[r, c].is_empty() and
                   board_matrix[r, c].color == piece.color):
                match_positions.append((r, c))
                visited.add((r, c))
                r += dr
                c += dc
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while (0 <= r < board_matrix.shape[0] and 
                   0 <= c < board_matrix.shape[1] and
                   board_matrix[r, c] is not None and
                   not board_matrix[r, c].is_empty() and
                   board_matrix[r, c].color == piece.color):
                match_positions.append((r, c))
                visited.add((r, c))
                r -= dr
                c -= dc
            
            # Only return if it's a valid match
            if len(match_positions) >= MIN_MATCH_LENGTH:
                return match_positions
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting line match: {e}")
            return None

class MoveSimulator:
    """Simulates the effects of moves on the board"""
    
    def __init__(self):
        self.move_generator = MoveGenerator()
    
    def simulate_move_effects(self, board_matrix: np.ndarray, move: Move) -> Tuple[np.ndarray, List[List[Tuple[int, int]]]]:
        """
        Simulate a move and return the resulting board state and matches
        
        Args:
            board_matrix: Current board state
            move: Move to simulate
            
        Returns:
            Tuple of (new_board_state, list_of_matches)
        """
        try:
            # Create a copy of the board
            new_board = board_matrix.copy()
            
            # Apply the move
            row1, col1 = move.from_pos
            row2, col2 = move.to_pos
            
            new_board[row1, col1], new_board[row2, col2] = \
                new_board[row2, col2], new_board[row1, col1]
            
            # Find all matches after the move
            matches = self.move_generator.find_matches(new_board)
            
            # Simulate cascading effects
            final_board, all_matches = self._simulate_cascade(new_board, matches)
            
            return final_board, all_matches
            
        except Exception as e:
            logger.error(f"Error simulating move effects: {e}")
            return board_matrix, []
    
    def _simulate_cascade(self, board_matrix: np.ndarray, initial_matches: List[List[Tuple[int, int]]]) -> Tuple[np.ndarray, List[List[Tuple[int, int]]]]:
        """
        Simulate cascading effects of matches
        
        Args:
            board_matrix: Board state after initial move
            initial_matches: Initial matches from the move
            
        Returns:
            Tuple of (final_board_state, all_matches_including_cascades)
        """
        try:
            current_board = board_matrix.copy()
            all_matches = initial_matches.copy()
            
            # Continue until no more matches
            while initial_matches:
                # Remove matched pieces
                for match in initial_matches:
                    for row, col in match:
                        current_board[row, col] = Piece(color=PieceColor.EMPTY)
                
                # Simulate pieces falling (simplified)
                current_board = self._simulate_falling(current_board)
                
                # Find new matches
                initial_matches = self.move_generator.find_matches(current_board)
                if initial_matches:
                    all_matches.extend(initial_matches)
            
            return current_board, all_matches
            
        except Exception as e:
            logger.error(f"Error simulating cascade: {e}")
            return board_matrix, []
    
    def _simulate_falling(self, board_matrix: np.ndarray) -> np.ndarray:
        """
        Simulate pieces falling to fill empty spaces
        
        Args:
            board_matrix: Board with empty spaces
            
        Returns:
            Board with pieces fallen
        """
        try:
            new_board = board_matrix.copy()
            rows, cols = new_board.shape
            
            # For each column, move pieces down
            for col in range(cols):
                # Start from bottom, move up
                write_row = rows - 1
                for read_row in range(rows - 1, -1, -1):
                    if new_board[read_row, col] is not None and not new_board[read_row, col].is_empty():
                        if write_row != read_row:
                            new_board[write_row, col] = new_board[read_row, col]
                            new_board[read_row, col] = Piece(color=PieceColor.EMPTY)
                        write_row -= 1
                
                # Fill remaining spaces with empty pieces
                for row in range(write_row + 1):
                    new_board[row, col] = Piece(color=PieceColor.EMPTY)
            
            return new_board
            
        except Exception as e:
            logger.error(f"Error simulating falling: {e}")
            return board_matrix
    
    def count_pieces_cleared(self, matches: List[List[Tuple[int, int]]]) -> int:
        """
        Count total pieces cleared by matches
        
        Args:
            matches: List of match positions
            
        Returns:
            Total number of pieces cleared
        """
        try:
            unique_positions = set()
            for match in matches:
                for pos in match:
                    unique_positions.add(pos)
            
            return len(unique_positions)
            
        except Exception as e:
            logger.error(f"Error counting cleared pieces: {e}")
            return 0