"""
Move Generator Module for Royal Match Bot
Handles finding valid moves and simulating their effects.
"""

import copy
from typing import List, Tuple, Optional, Set, Dict
import logging

from .game_rules import Piece, PieceColor, PowerUpType, Move, is_valid_swap, get_adjacent_positions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoveGenerator:
    """Generates and validates possible moves for the game board"""
    
    def __init__(self):
        self.min_match_length = 3  # Minimum pieces needed for a match
        
    def find_all_possible_moves(self, board_matrix: List[List[Piece]]) -> List[Move]:
        """
        Find all possible valid moves that create matches
        
        Args:
            board_matrix: Current board state
            
        Returns:
            List of valid Move objects
        """
        try:
            if not board_matrix:
                return []
            
            grid_size = len(board_matrix)
            valid_moves = []
            
            # Check every adjacent pair for valid swaps
            for row in range(grid_size):
                for col in range(grid_size):
                    current_pos = (row, col)
                    
                    # Get adjacent positions
                    adjacent_positions = get_adjacent_positions(current_pos, grid_size)
                    
                    for adj_pos in adjacent_positions:
                        # Check if this swap would create a match
                        if self._would_create_match(board_matrix, current_pos, adj_pos):
                            move = Move(pos1=current_pos, pos2=adj_pos)
                            valid_moves.append(move)
            
            # Remove duplicate moves (A->B and B->A are the same)
            unique_moves = self._remove_duplicate_moves(valid_moves)
            
            logger.info(f"Found {len(unique_moves)} valid moves")
            return unique_moves
            
        except Exception as e:
            logger.error(f"Error finding possible moves: {e}")
            return []
    
    def _would_create_match(self, board_matrix: List[List[Piece]], pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Check if swapping two pieces would create a match
        
        Args:
            board_matrix: Current board state
            pos1: First position (row, col)
            pos2: Second position (row, col)
            
        Returns:
            True if swap would create a match
        """
        try:
            # Create a copy of the board for simulation
            test_board = copy.deepcopy(board_matrix)
            
            # Perform the swap
            row1, col1 = pos1
            row2, col2 = pos2
            
            test_board[row1][col1], test_board[row2][col2] = \
                test_board[row2][col2], test_board[row1][col1]
            
            # Check if any matches were created
            return self._has_matches(test_board)
            
        except Exception as e:
            logger.error(f"Error checking if move creates match: {e}")
            return False
    
    def _has_matches(self, board_matrix: List[List[Piece]]) -> bool:
        """
        Check if the board has any matches
        
        Args:
            board_matrix: Board to check
            
        Returns:
            True if there are matches
        """
        try:
            grid_size = len(board_matrix)
            
            # Check horizontal matches
            for row in range(grid_size):
                for col in range(grid_size - 2):
                    if (board_matrix[row][col].color != PieceColor.EMPTY and
                        board_matrix[row][col].color == board_matrix[row][col + 1].color and
                        board_matrix[row][col].color == board_matrix[row][col + 2].color):
                        return True
            
            # Check vertical matches
            for row in range(grid_size - 2):
                for col in range(grid_size):
                    if (board_matrix[row][col].color != PieceColor.EMPTY and
                        board_matrix[row][col].color == board_matrix[row + 1][col].color and
                        board_matrix[row][col].color == board_matrix[row + 2][col].color):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for matches: {e}")
            return False
    
    def _remove_duplicate_moves(self, moves: List[Move]) -> List[Move]:
        """
        Remove duplicate moves (A->B and B->A are the same)
        
        Args:
            moves: List of moves to deduplicate
            
        Returns:
            List of unique moves
        """
        try:
            unique_moves = []
            seen_pairs = set()
            
            for move in moves:
                # Create a canonical representation of the move
                pair = tuple(sorted([move.pos1, move.pos2]))
                
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    unique_moves.append(move)
            
            return unique_moves
            
        except Exception as e:
            logger.error(f"Error removing duplicate moves: {e}")
            return moves
    
    def simulate_move_effects(self, board_matrix: List[List[Piece]], move: Move) -> Tuple[List[List[Piece]], List[Piece]]:
        """
        Simulate the effects of a move, including cascades and power-up activations
        
        Args:
            board_matrix: Current board state
            piece_matrix: Move to simulate
            
        Returns:
            Tuple of (final_board_state, pieces_cleared)
        """
        try:
            # Create a copy for simulation
            sim_board = copy.deepcopy(board_matrix)
            pieces_cleared = []
            
            # Perform the swap
            row1, col1 = move.pos1
            row2, col2 = move.pos2
            
            sim_board[row1][col1], sim_board[row2][col2] = \
                sim_board[row2][col2], sim_board[row1][col1]
            
            # Simulate cascades until no more matches
            cascade_count = 0
            max_cascades = 10  # Prevent infinite loops
            
            while cascade_count < max_cascades:
                # Find all matches
                matches = self._find_all_matches(sim_board)
                if not matches:
                    break
                
                # Clear matches and collect pieces
                for match in matches:
                    for pos in match:
                        row, col = pos
                        if not sim_board[row][col].is_empty():
                            pieces_cleared.append(sim_board[row][col])
                            sim_board[row][col] = Piece(color=PieceColor.EMPTY)
                
                # Simulate falling pieces
                sim_board = self._simulate_falling(sim_board)
                
                # Check for power-up activations
                sim_board = self._simulate_power_up_activations(sim_board, pieces_cleared)
                
                cascade_count += 1
            
            if cascade_count >= max_cascades:
                logger.warning("Maximum cascade count reached")
            
            logger.info(f"Simulated move with {cascade_count} cascades, cleared {len(pieces_cleared)} pieces")
            return sim_board, pieces_cleared
            
        except Exception as e:
            logger.error(f"Error simulating move effects: {e}")
            return board_matrix, []
    
    def _find_all_matches(self, board_matrix: List[List[Piece]]) -> List[List[Tuple[int, int]]]:
        """
        Find all matches on the board
        
        Args:
            board_matrix: Board to check
            
        Returns:
            List of matches, each match is a list of positions
        """
        try:
            matches = []
            grid_size = len(board_matrix)
            
            # Check horizontal matches
            for row in range(grid_size):
                col = 0
                while col < grid_size - 2:
                    if board_matrix[row][col].color != PieceColor.EMPTY:
                        # Find the length of this match
                        match_length = 1
                        while (col + match_length < grid_size and 
                               board_matrix[row][col + match_length].color == board_matrix[row][col].color):
                            match_length += 1
                        
                        # If we have a match, add it
                        if match_length >= self.min_match_length:
                            match_positions = [(row, col + i) for i in range(match_length)]
                            matches.append(match_positions)
                            col += match_length
                        else:
                            col += 1
                    else:
                        col += 1
            
            # Check vertical matches
            for col in range(grid_size):
                row = 0
                while row < grid_size - 2:
                    if board_matrix[row][col].color != PieceColor.EMPTY:
                        # Find the length of this match
                        match_length = 1
                        while (row + match_length < grid_size and 
                               board_matrix[row + match_length][col].color == board_matrix[row][col].color):
                            match_length += 1
                        
                        # If we have a match, add it
                        if match_length >= self.min_match_length:
                            match_positions = [(row + i, col) for i in range(match_length)]
                            matches.append(match_positions)
                            row += match_length
                        else:
                            row += 1
                    else:
                        row += 1
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matches: {e}")
            return []
    
    def _simulate_falling(self, board_matrix: List[List[Piece]]) -> List[List[Piece]]:
        """
        Simulate pieces falling to fill empty spaces
        
        Args:
            board_matrix: Board with empty spaces
            
        Returns:
            Board with pieces fallen
        """
        try:
            grid_size = len(board_matrix)
            
            # For each column, move pieces down
            for col in range(grid_size):
                # Start from bottom and work up
                write_row = grid_size - 1
                for read_row in range(grid_size - 1, -1, -1):
                    if not board_matrix[read_row][col].is_empty():
                        if write_row != read_row:
                            board_matrix[write_row][col] = board_matrix[read_row][col]
                            board_matrix[read_row][col] = Piece(color=PieceColor.EMPTY)
                        write_row -= 1
            
            return board_matrix
            
        except Exception as e:
            logger.error(f"Error simulating falling: {e}")
            return board_matrix
    
    def _simulate_power_up_activations(self, board_matrix: List[List[Piece]], pieces_cleared: List[Piece]) -> List[List[Piece]]:
        """
        Simulate power-up activations and their effects
        
        Args:
            board_matrix: Current board state
            pieces_cleared: Pieces that were cleared in this cascade
            
        Returns:
            Board after power-up effects
        """
        try:
            # This is a simplified implementation
            # In a full implementation, you'd handle:
            # - Rocket effects (clear row/column)
            # - TNT effects (clear 3x3 area)
            # - Propeller effects (clear random area)
            # - Light ball effects (clear all pieces of target color)
            # - Power-up combinations
            
            # For now, just return the board as-is
            # TODO: Implement full power-up simulation
            return board_matrix
            
        except Exception as e:
            logger.error(f"Error simulating power-up activations: {e}")
            return board_matrix
    
    def get_move_potential(self, board_matrix: List[List[Piece]], move: Move) -> Dict:
        """
        Analyze the potential of a move
        
        Args:
            board_matrix: Current board state
            move: Move to analyze
            
        Returns:
            Dictionary with move analysis
        """
        try:
            # Simulate the move
            final_board, pieces_cleared = self.simulate_move_effects(board_matrix, move)
            
            # Analyze the results
            analysis = {
                'pieces_cleared': len(pieces_cleared),
                'colors_cleared': {},
                'power_ups_created': 0,
                'cascade_potential': 0,
                'board_clearing': 0
            }
            
            # Count pieces by color
            for piece in pieces_cleared:
                color = piece.color.value
                analysis['colors_cleared'][color] = analysis['colors_cleared'].get(color, 0) + 1
            
            # Count power-ups created
            for piece in pieces_cleared:
                if piece.power_up:
                    analysis['power_ups_created'] += 1
            
            # Calculate cascade potential (simplified)
            analysis['cascade_potential'] = len(pieces_cleared) // 3
            
            # Calculate board clearing percentage
            total_pieces = sum(len(row) for row in board_matrix)
            analysis['board_clearing'] = len(pieces_cleared) / total_pieces if total_pieces > 0 else 0
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing move potential: {e}")
            return {}