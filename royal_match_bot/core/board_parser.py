"""
Board Parser Module for Royal Match Bot
Handles building the game state matrix and parsing level objectives.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import logging
import re

from .game_rules import Piece, PieceColor, PowerUpType, ObstacleType, Objective
from .image_processing import ImageProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoardParser:
    """Parses the game board and builds the game state matrix"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.default_grid_size = 8  # Most common Royal Match grid size
        
    def parse_level_objectives(self, screenshot_path: str) -> List[Objective]:
        """
        Parse level objectives from the screenshot
        
        Args:
            screenshot_path: Path to the screenshot image
            
        Returns:
            List of Objective objects
        """
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Failed to load image: {screenshot_path}")
                return []
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Try to detect objective areas (usually top-left or top-center)
            objectives = []
            
            # Look for common objective patterns
            objectives.extend(self._detect_collect_objectives(image_rgb))
            objectives.extend(self._detect_clear_objectives(image_rgb))
            objectives.extend(self._detect_spread_objectives(image_rgb))
            
            # If no objectives detected, create a default one
            if not objectives:
                logger.warning("No objectives detected, using default")
                objectives.append(Objective(
                    type="collect",
                    target="any",
                    count=50,
                    current=0
                ))
            
            logger.info(f"Detected {len(objectives)} objectives")
            return objectives
            
        except Exception as e:
            logger.error(f"Error parsing level objectives: {e}")
            return []
    
    def _detect_collect_objectives(self, image: np.ndarray) -> List[Objective]:
        """Detect 'collect X pieces of color Y' objectives"""
        objectives = []
        
        try:
            # This is a simplified implementation
            # In a real bot, you'd use OCR to read the text
            # For now, we'll use color detection in the UI area
            
            # Look for colored indicators in the top area
            top_region = image[:100, :]  # Top 100 pixels
            
            # Check for different colors that might indicate objectives
            for color_name, color_value in [
                ("red", (255, 0, 0)),
                ("blue", (0, 0, 255)),
                ("green", (0, 255, 0)),
                ("yellow", (255, 255, 0)),
                ("purple", (128, 0, 128)),
                ("orange", (255, 165, 0))
            ]:
                # Simple color detection (this is very basic)
                color_mask = cv2.inRange(top_region, 
                                       np.array(color_value) - 50, 
                                       np.array(color_value) + 50)
                if np.sum(color_mask) > 1000:  # Threshold for color presence
                    objectives.append(Objective(
                        type="collect",
                        target=color_name,
                        count=20,  # Default count
                        current=0
                    ))
            
        except Exception as e:
            logger.error(f"Error detecting collect objectives: {e}")
        
        return objectives
    
    def _detect_clear_objectives(self, image: np.ndarray) -> List[Objective]:
        """Detect 'clear X obstacles' objectives"""
        objectives = []
        
        try:
            # Look for obstacle indicators in the UI
            # This would typically involve OCR or template matching
            # For now, return empty list
            pass
            
        except Exception as e:
            logger.error(f"Error detecting clear objectives: {e}")
        
        return objectives
    
    def _detect_spread_objectives(self, image: np.ndarray) -> List[Objective]:
        """Detect 'spread jelly to X positions' objectives"""
        objectives = []
        
        try:
            # Look for jelly indicators
            # This would typically involve OCR or template matching
            # For now, return empty list
            pass
            
        except Exception as e:
            logger.error(f"Error detecting spread objectives: {e}")
        
        return objectives
    
    def build_board_matrix(self, board_image: np.ndarray, grid_size: Optional[int] = None) -> List[List[Piece]]:
        """
        Build a 2D matrix representing the current board state
        
        Args:
            board_image: The cropped board image
            grid_size: Size of the grid (8x8 or 9x9)
            
        Returns:
            2D list of Piece objects representing the board
        """
        try:
            if grid_size is None:
                grid_size = self.default_grid_size
            
            # Identify grid cells
            grid_cells = self.image_processor.identify_grid_cells(board_image, grid_size)
            if not grid_cells:
                logger.error("Failed to identify grid cells")
                return []
            
            # Build piece matrix
            piece_matrix = []
            for row_idx, row_cells in enumerate(grid_cells):
                row_pieces = []
                for col_idx, (x, y, w, h) in enumerate(row_cells):
                    # Extract cell image
                    cell_image = board_image[y:y+h, x:x+w]
                    
                    # Classify piece
                    piece = self.image_processor.classify_piece_type(cell_image)
                    row_pieces.append(piece)
                    
                    logger.debug(f"Cell ({row_idx}, {col_idx}): {piece.color.value}")
                
                piece_matrix.append(row_pieces)
            
            logger.info(f"Built board matrix: {len(piece_matrix)}x{len(piece_matrix[0]) if piece_matrix else 0}")
            return piece_matrix
            
        except Exception as e:
            logger.error(f"Error building board matrix: {e}")
            return []
    
    def detect_grid_size(self, board_image: np.ndarray) -> int:
        """
        Automatically detect the grid size from the board image
        
        Args:
            board_image: The board image
            
        Returns:
            Detected grid size (8 or 9)
        """
        try:
            height, width = board_image.shape[:2]
            
            # Try different grid sizes and see which gives better cell division
            best_size = 8
            best_score = 0
            
            for size in [8, 9]:
                # Calculate cell dimensions
                cell_width = width // size
                cell_height = height // size
                
                # Check if cells are roughly square
                aspect_ratio = cell_width / cell_height
                squareness_score = 1.0 - abs(1.0 - aspect_ratio)
                
                # Check if cell dimensions are reasonable
                if 20 <= cell_width <= 100 and 20 <= cell_height <= 100:
                    score = squareness_score
                    if score > best_score:
                        best_score = score
                        best_size = size
            
            logger.info(f"Detected grid size: {best_size}")
            return best_size
            
        except Exception as e:
            logger.error(f"Error detecting grid size: {e}")
            return 8  # Default fallback
    
    def validate_board_matrix(self, piece_matrix: List[List[Piece]]) -> bool:
        """
        Validate that the board matrix is properly formed
        
        Args:
            piece_matrix: The board matrix to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not piece_matrix:
                logger.error("Board matrix is empty")
                return False
            
            # Check that all rows have the same length
            row_lengths = [len(row) for row in piece_matrix]
            if len(set(row_lengths)) != 1:
                logger.error(f"Inconsistent row lengths: {row_lengths}")
                return False
            
            # Check that we have a reasonable grid size
            grid_size = len(piece_matrix)
            if grid_size not in [8, 9]:
                logger.warning(f"Unusual grid size: {grid_size}")
            
            # Check that all pieces are valid
            for row_idx, row in enumerate(piece_matrix):
                for col_idx, piece in enumerate(row):
                    if piece is None:
                        logger.error(f"None piece at ({row_idx}, {col_idx})")
                        return False
                    if not isinstance(piece, Piece):
                        logger.error(f"Invalid piece type at ({row_idx}, {col_idx}): {type(piece)}")
                        return False
            
            logger.info("Board matrix validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating board matrix: {e}")
            return False
    
    def get_board_statistics(self, piece_matrix: List[List[Piece]]) -> Dict:
        """
        Get statistics about the current board state
        
        Args:
            piece_matrix: The board matrix
            
        Returns:
            Dictionary with board statistics
        """
        try:
            stats = {
                'total_pieces': 0,
                'color_counts': {},
                'power_up_counts': {},
                'obstacle_counts': {},
                'empty_cells': 0
            }
            
            # Count pieces by type
            for row in piece_matrix:
                for piece in row:
                    if piece.is_empty():
                        stats['empty_cells'] += 1
                    else:
                        stats['total_pieces'] += 1
                        
                        # Count colors
                        color = piece.color.value
                        stats['color_counts'][color] = stats['color_counts'].get(color, 0) + 1
                        
                        # Count power-ups
                        if piece.power_up:
                            power_up = piece.power_up.value
                            stats['power_up_counts'][power_up] = stats['power_up_counts'].get(power_up, 0) + 1
                        
                        # Count obstacles
                        if piece.obstacle:
                            obstacle = piece.obstacle.value
                            stats['obstacle_counts'][obstacle] = stats['obstacle_counts'].get(obstacle, 0) + 1
            
            logger.info(f"Board statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting board statistics: {e}")
            return {}
    
    def find_pieces_by_color(self, piece_matrix: List[List[Piece]], color: PieceColor) -> List[Tuple[int, int]]:
        """
        Find all positions of pieces with a specific color
        
        Args:
            piece_matrix: The board matrix
            color: Color to search for
            
        Returns:
            List of (row, col) positions
        """
        try:
            positions = []
            for row_idx, row in enumerate(piece_matrix):
                for col_idx, piece in enumerate(row):
                    if piece.color == color:
                        positions.append((row_idx, col_idx))
            
            return positions
            
        except Exception as e:
            logger.error(f"Error finding pieces by color: {e}")
            return []
    
    def find_pieces_by_power_up(self, piece_matrix: List[List[Piece]], power_up: PowerUpType) -> List[Tuple[int, int]]:
        """
        Find all positions of pieces with a specific power-up
        
        Args:
            piece_matrix: The board matrix
            power_up: Power-up type to search for
            
        Returns:
            List of (row, col) positions
        """
        try:
            positions = []
            for row_idx, row in enumerate(piece_matrix):
                for col_idx, piece in enumerate(row):
                    if piece.power_up == power_up:
                        positions.append((row_idx, col_idx))
            
            return positions
            
        except Exception as e:
            logger.error(f"Error finding pieces by power-up: {e}")
            return []