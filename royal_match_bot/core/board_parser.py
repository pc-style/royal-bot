"""
Board parser module for Royal Match bot.
Handles grid detection and game state parsing.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from .image_processing import identify_grid_cells, classify_piece_type


class BoardState:
    """Represents the current state of the game board."""
    
    def __init__(self, rows: int = 8, cols: int = 8):
        self.rows = rows
        self.cols = cols
        self.board_matrix = [[None for _ in range(cols)] for _ in range(rows)]
        self.objectives = {}
        self.remaining_moves = 0
    
    def set_piece(self, row: int, col: int, piece_data: dict):
        """Set piece data at specific board position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.board_matrix[row][col] = piece_data
    
    def get_piece(self, row: int, col: int) -> Optional[dict]:
        """Get piece data at specific board position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board_matrix[row][col]
        return None
    
    def print_board(self):
        """Print a simple representation of the board for debugging."""
        for row in self.board_matrix:
            row_str = ""
            for piece in row:
                if piece is None:
                    row_str += "[ ] "
                else:
                    color = piece.get('color', 'unknown')
                    row_str += f"[{color[0].upper() if color != 'unknown' else '?'}] "
            print(row_str)


def parse_level_objectives(screenshot: np.ndarray) -> dict:
    """
    OCR the objective area and extract goals and remaining moves.
    
    Args:
        screenshot: Full screenshot as numpy array
        
    Returns:
        Dictionary with objectives and remaining moves
    """
    # TODO: Implement OCR for objectives
    # Return placeholder objectives
    return {
        'collect_red': 20,
        'collect_blue': 15,
        'remaining_moves': 25
    }


def build_board_matrix(board_image: np.ndarray) -> BoardState:
    """
    Create 2D array representing current board state.
    
    Args:
        board_image: Board area image as numpy array
        
    Returns:
        BoardState object with current game state
    """
    board_state = BoardState()
    
    # Get grid cells
    grid_cells = identify_grid_cells(board_image)
    
    # Process each cell
    cell_idx = 0
    for row in range(8):
        for col in range(8):
            if cell_idx < len(grid_cells):
                x1, y1, x2, y2 = grid_cells[cell_idx]
                cell_image = board_image[y1:y2, x1:x2]
                
                # Classify the piece in this cell
                piece_data = classify_piece_type(cell_image)
                board_state.set_piece(row, col, piece_data)
                
                cell_idx += 1
    
    return board_state


def detect_board_boundaries(screenshot: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Detect the boundaries of the game board in the screenshot.
    
    Args:
        screenshot: Full screenshot as numpy array
        
    Returns:
        Tuple of (x1, y1, x2, y2) coordinates of board boundaries
    """
    # TODO: Implement proper board detection
    # For now, assume board takes up middle portion of screen
    height, width = screenshot.shape[:2]
    
    # Rough estimation - board is usually in center with some margin
    margin_x = width // 8
    margin_y = height // 6
    
    x1 = margin_x
    y1 = margin_y
    x2 = width - margin_x
    y2 = height - margin_y
    
    return (x1, y1, x2, y2)