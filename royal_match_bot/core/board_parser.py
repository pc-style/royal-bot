"""
Board Parser Module for Royal Match Bot
Handles building the board matrix and parsing level objectives.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import logging
import re

from .game_rules import Piece, PieceColor, PowerUpType, ObstacleType, Objective
from .image_processing import BoardDetector, PieceClassifier

logger = logging.getLogger(__name__)

class BoardParser:
    """Parses the game board and extracts game state information"""
    
    def __init__(self):
        self.board_detector = BoardDetector()
        self.piece_classifier = PieceClassifier()
        self.grid_size = (8, 8)  # Default grid size
        
    def parse_level_objectives(self, screenshot: np.ndarray) -> List[Objective]:
        """
        Parse level objectives from screenshot (usually top-left area)
        
        Args:
            screenshot: Full screenshot image
            
        Returns:
            List of Objective objects
        """
        try:
            # Extract the top-left area where objectives are typically displayed
            height, width = screenshot.shape[:2]
            objective_area = screenshot[0:height//4, 0:width//3]
            
            # Convert to grayscale for text detection
            gray = cv2.cvtColor(objective_area, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to isolate text
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # For now, return placeholder objectives
            # In a real implementation, you'd use OCR (pytesseract) to extract text
            # and parse it into structured objectives
            
            objectives = [
                Objective(type="collect", target="red", amount=20, current=0),
                Objective(type="clear", target="boxes", amount=5, current=0)
            ]
            
            logger.info(f"Parsed {len(objectives)} objectives")
            return objectives
            
        except Exception as e:
            logger.error(f"Error parsing objectives: {e}")
            return []
    
    def build_board_matrix(self, board_image: np.ndarray) -> np.ndarray:
        """
        Create 2D array representing current board state
        
        Args:
            board_image: Cropped board image
            
        Returns:
            2D numpy array of Piece objects
        """
        try:
            # Get grid cells
            grid_image, cell_coords = self.board_detector.identify_grid_cells(board_image)
            
            if not cell_coords:
                logger.error("No grid cells identified")
                return np.array([])
            
            # Calculate cell dimensions
            height, width = board_image.shape[:2]
            cell_width = width // self.grid_size[0]
            cell_height = height // self.grid_size[1]
            
            # Initialize board matrix
            board_matrix = np.empty(self.grid_size, dtype=object)
            
            # Process each cell
            for row in range(self.grid_size[1]):
                for col in range(self.grid_size[0]):
                    # Calculate cell boundaries
                    x1 = col * cell_width
                    y1 = row * cell_height
                    x2 = x1 + cell_width
                    y2 = y1 + cell_height
                    
                    # Extract cell image
                    cell_image = board_image[y1:y2, x1:x2]
                    
                    # Classify the piece
                    piece = self.piece_classifier.classify_piece_type(cell_image)
                    
                    # Store in matrix
                    board_matrix[row, col] = piece
            
            logger.info(f"Board matrix built: {self.grid_size[0]}x{self.grid_size[1]}")
            return board_matrix
            
        except Exception as e:
            logger.error(f"Error building board matrix: {e}")
            return np.array([])
    
    def extract_cell_image(self, board_image: np.ndarray, row: int, col: int) -> np.ndarray:
        """
        Extract a specific cell image from the board
        
        Args:
            board_image: Full board image
            row: Row index
            col: Column index
            
        Returns:
            Cell image as numpy array
        """
        try:
            height, width = board_image.shape[:2]
            cell_width = width // self.grid_size[0]
            cell_height = height // self.grid_size[1]
            
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            return board_image[y1:y2, x1:x2]
            
        except Exception as e:
            logger.error(f"Error extracting cell image: {e}")
            return np.array([])
    
    def get_board_statistics(self, board_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Get statistics about the current board state
        
        Args:
            board_matrix: 2D array of Piece objects
            
        Returns:
            Dictionary with board statistics
        """
        try:
            if board_matrix.size == 0:
                return {}
            
            stats = {
                'total_pieces': 0,
                'color_counts': {},
                'power_up_counts': {},
                'obstacle_counts': {},
                'empty_cells': 0
            }
            
            # Count pieces by type
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece is None:
                        continue
                    
                    if piece.is_empty():
                        stats['empty_cells'] += 1
                    else:
                        stats['total_pieces'] += 1
                        
                        # Count colors
                        color_name = piece.color.value
                        stats['color_counts'][color_name] = stats['color_counts'].get(color_name, 0) + 1
                        
                        # Count power-ups
                        if piece.is_power_up():
                            power_up_name = piece.power_up.value
                            stats['power_up_counts'][power_up_name] = stats['power_up_counts'].get(power_up_name, 0) + 1
                        
                        # Count obstacles
                        if piece.has_obstacle():
                            obstacle_name = piece.obstacle.value
                            stats['obstacle_counts'][obstacle_name] = stats['obstacle_counts'].get(obstacle_name, 0) + 1
            
            logger.info(f"Board statistics: {stats['total_pieces']} pieces, {stats['empty_cells']} empty cells")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating board statistics: {e}")
            return {}
    
    def validate_board_matrix(self, board_matrix: np.ndarray) -> bool:
        """
        Validate that the board matrix is properly formed
        
        Args:
            board_matrix: 2D array to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if board_matrix.size == 0:
                logger.warning("Board matrix is empty")
                return False
            
            if board_matrix.shape != self.grid_size:
                logger.warning(f"Board matrix shape {board_matrix.shape} doesn't match expected {self.grid_size}")
                return False
            
            # Check that all cells contain Piece objects
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    if board_matrix[row, col] is None:
                        logger.warning(f"Empty cell at ({row}, {col})")
                        return False
            
            logger.info("Board matrix validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating board matrix: {e}")
            return False
    
    def print_board_matrix(self, board_matrix: np.ndarray) -> None:
        """
        Print a human-readable representation of the board
        
        Args:
            board_matrix: 2D array of Piece objects
        """
        try:
            if board_matrix.size == 0:
                print("Empty board matrix")
                return
            
            print("Board Matrix:")
            print("=" * (self.grid_size[0] * 3 + 1))
            
            for row in range(board_matrix.shape[0]):
                row_str = "|"
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece is None:
                        row_str += " ?|"
                    elif piece.is_empty():
                        row_str += "  |"
                    else:
                        # Use first letter of color
                        color_letter = piece.color.value[0].upper()
                        if piece.is_power_up():
                            color_letter = "*"  # Indicate power-up
                        elif piece.has_obstacle():
                            color_letter = "#"  # Indicate obstacle
                        row_str += f" {color_letter}|"
                
                print(row_str)
                if row < board_matrix.shape[0] - 1:
                    print("-" * (self.grid_size[0] * 3 + 1))
            
            print("=" * (self.grid_size[0] * 3 + 1))
            
        except Exception as e:
            logger.error(f"Error printing board matrix: {e}")

class ObjectiveParser:
    """Parses level objectives from text or images"""
    
    def __init__(self):
        # Common objective patterns
        self.objective_patterns = {
            'collect': r'collect\s+(\d+)\s+(\w+)',
            'clear': r'clear\s+(\d+)\s+(\w+)',
            'spread': r'spread\s+(\w+)\s+(\d+)\s+times',
            'reach': r'reach\s+(\d+)\s+(\w+)'
        }
    
    def parse_objective_text(self, text: str) -> List[Objective]:
        """
        Parse objective text into structured objectives
        
        Args:
            text: Raw objective text
            
        Returns:
            List of Objective objects
        """
        try:
            objectives = []
            text_lower = text.lower()
            
            for obj_type, pattern in self.objective_patterns.items():
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    if obj_type == 'collect':
                        amount, target = int(match[0]), match[1]
                        objectives.append(Objective(type=obj_type, target=target, amount=amount))
                    elif obj_type == 'clear':
                        amount, target = int(match[0]), match[1]
                        objectives.append(Objective(type=obj_type, target=target, amount=amount))
                    elif obj_type == 'spread':
                        target, amount = match[0], int(match[1])
                        objectives.append(Objective(type=obj_type, target=target, amount=amount))
                    elif obj_type == 'reach':
                        amount, target = int(match[0]), match[1]
                        objectives.append(Objective(type=obj_type, target=target, amount=amount))
            
            return objectives
            
        except Exception as e:
            logger.error(f"Error parsing objective text: {e}")
            return []