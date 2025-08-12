"""
Visualization Module for Royal Match Bot
Handles drawing move suggestions and debugging information on images.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
import logging

from ..core.game_rules import Move, Piece, PieceColor, PowerUpType

logger = logging.getLogger(__name__)

class MoveVisualizer:
    """Visualizes move suggestions on game screenshots"""
    
    def __init__(self):
        # Color definitions for visualization
        self.colors = {
            'arrow': (0, 255, 0),      # Green arrow
            'highlight': (255, 255, 0), # Yellow highlight
            'text': (255, 255, 255),    # White text
            'background': (0, 0, 0),    # Black background
            'score_high': (0, 255, 0),  # Green for high scores
            'score_medium': (255, 255, 0), # Yellow for medium scores
            'score_low': (255, 0, 0)    # Red for low scores
        }
        
        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.font_thickness = 2
        
    def visualize_suggested_move(self, original_image: np.ndarray, move: Move, 
                                reasoning: str, board_matrix: np.ndarray) -> np.ndarray:
        """
        Draw move suggestion on the original screenshot
        
        Args:
            original_image: Original screenshot
            move: Suggested move to visualize
            reasoning: Text explanation of the move
            board_matrix: Board matrix for piece information
            
        Returns:
            Annotated image with move visualization
        """
        try:
            # Create a copy of the original image
            annotated_image = original_image.copy()
            
            # Calculate board boundaries (assuming 8x8 grid)
            board_height, board_width = original_image.shape[:2]
            cell_width = board_width // 8
            cell_height = board_height // 8
            
            # Convert board coordinates to image coordinates
            from_row, from_col = move.from_pos
            to_row, to_col = move.to_pos
            
            # Calculate center points of cells
            from_x = from_col * cell_width + cell_width // 2
            from_y = from_row * cell_height + cell_height // 2
            to_x = to_col * cell_width + cell_width // 2
            to_y = to_row * cell_height + cell_height // 2
            
            # Draw arrow between the two pieces
            self._draw_arrow(annotated_image, (from_x, from_y), (to_x, to_y))
            
            # Highlight the two pieces being swapped
            self._highlight_cell(annotated_image, from_row, from_col, cell_width, cell_height)
            self._highlight_cell(annotated_image, to_row, to_col, cell_width, cell_height)
            
            # Add move information text
            self._add_move_info(annotated_image, move, reasoning, (20, 30))
            
            # Add score information
            if hasattr(move, 'score'):
                self._add_score_info(annotated_image, move.score, (20, 80))
            
            # Add board statistics
            self._add_board_stats(annotated_image, board_matrix, (20, 130))
            
            logger.info("Move visualization completed")
            return annotated_image
            
        except Exception as e:
            logger.error(f"Error visualizing move: {e}")
            return original_image
    
    def _draw_arrow(self, image: np.ndarray, start_point: Tuple[int, int], 
                    end_point: Tuple[int, int]) -> None:
        """Draw an arrow between two points"""
        try:
            # Draw the main line
            cv2.line(image, start_point, end_point, self.colors['arrow'], 3)
            
            # Calculate arrow head
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            
            # Normalize the direction vector
            length = np.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
            
            # Arrow head size
            arrow_size = 15
            
            # Calculate arrow head points
            arrow_point1 = (
                int(end_point[0] - arrow_size * dx + arrow_size * dy),
                int(end_point[1] - arrow_size * dy - arrow_size * dx)
            )
            arrow_point2 = (
                int(end_point[0] - arrow_size * dx - arrow_size * dy),
                int(end_point[1] - arrow_size * dy + arrow_size * dx)
            )
            
            # Draw arrow head
            cv2.line(image, end_point, arrow_point1, self.colors['arrow'], 3)
            cv2.line(image, end_point, arrow_point2, self.colors['arrow'], 3)
            
        except Exception as e:
            logger.error(f"Error drawing arrow: {e}")
    
    def _highlight_cell(self, image: np.ndarray, row: int, col: int, 
                       cell_width: int, cell_height: int) -> None:
        """Highlight a specific cell on the board"""
        try:
            # Calculate cell boundaries
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            # Draw rectangle around the cell
            cv2.rectangle(image, (x1, y1), (x2, y2), self.colors['highlight'], 3)
            
            # Add a subtle fill
            overlay = image.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), self.colors['highlight'], -1)
            cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
            
        except Exception as e:
            logger.error(f"Error highlighting cell: {e}")
    
    def _add_move_info(self, image: np.ndarray, move: Move, reasoning: str, 
                       position: Tuple[int, int]) -> None:
        """Add move information text to the image"""
        try:
            x, y = position
            
            # Move description
            move_text = f"Move: ({move.from_pos[0]},{move.from_pos[1]}) -> ({move.to_pos[0]},{move.to_pos[1]})"
            cv2.putText(image, move_text, (x, y), self.font, self.font_scale, 
                       self.colors['text'], self.font_thickness)
            
            # Reasoning
            y += 25
            cv2.putText(image, f"Reason: {reasoning}", (x, y), self.font, self.font_scale, 
                       self.colors['text'], self.font_thickness)
            
        except Exception as e:
            logger.error(f"Error adding move info: {e}")
    
    def _add_score_info(self, image: np.ndarray, score: int, position: Tuple[int, int]) -> None:
        """Add score information to the image"""
        try:
            x, y = position
            
            # Determine score color
            if score >= 100:
                color = self.colors['score_high']
                level = "Excellent"
            elif score >= 50:
                color = self.colors['score_medium']
                level = "Good"
            else:
                color = self.colors['score_low']
                level = "Fair"
            
            # Score text
            score_text = f"Score: {score} ({level})"
            cv2.putText(image, score_text, (x, y), self.font, self.font_scale, 
                       color, self.font_thickness)
            
        except Exception as e:
            logger.error(f"Error adding score info: {e}")
    
    def _add_board_stats(self, image: np.ndarray, board_matrix: np.ndarray, 
                        position: Tuple[int, int]) -> None:
        """Add board statistics to the image"""
        try:
            if board_matrix.size == 0:
                return
            
            x, y = position
            
            # Count pieces by color
            color_counts = {}
            power_up_count = 0
            obstacle_count = 0
            
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece is None:
                        continue
                    
                    if piece.is_empty():
                        continue
                    
                    # Count colors
                    color = piece.color.value
                    color_counts[color] = color_counts.get(color, 0) + 1
                    
                    # Count power-ups
                    if piece.is_power_up():
                        power_up_count += 1
                    
                    # Count obstacles
                    if piece.has_obstacle():
                        obstacle_count += 1
            
            # Display statistics
            stats_text = f"Board Stats: {len(color_counts)} colors, {power_up_count} power-ups, {obstacle_count} obstacles"
            cv2.putText(image, stats_text, (x, y), self.font, 0.5, 
                       self.colors['text'], 1)
            
        except Exception as e:
            logger.error(f"Error adding board stats: {e}")
    
    def create_debug_board(self, board_matrix: np.ndarray, cell_size: int = 60) -> np.ndarray:
        """
        Create a debug visualization of the board matrix
        
        Args:
            board_matrix: Board matrix to visualize
            cell_size: Size of each cell in pixels
            
        Returns:
            Debug board image
        """
        try:
            if board_matrix.size == 0:
                return np.zeros((100, 100, 3), dtype=np.uint8)
            
            rows, cols = board_matrix.shape
            image_height = rows * cell_size
            image_width = cols * cell_size
            
            # Create blank image
            debug_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
            
            # Color mapping for pieces
            color_map = {
                PieceColor.RED: (0, 0, 255),      # BGR format
                PieceColor.BLUE: (255, 0, 0),
                PieceColor.GREEN: (0, 255, 0),
                PieceColor.YELLOW: (0, 255, 255),
                PieceColor.PURPLE: (255, 0, 255),
                PieceColor.ORANGE: (0, 165, 255),
                PieceColor.EMPTY: (128, 128, 128)
            }
            
            # Draw each cell
            for row in range(rows):
                for col in range(cols):
                    piece = board_matrix[row, col]
                    if piece is None:
                        continue
                    
                    # Calculate cell position
                    x1 = col * cell_size
                    y1 = row * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    # Get color for the piece
                    color = color_map.get(piece.color, (128, 128, 128))
                    
                    # Fill cell with piece color
                    cv2.rectangle(debug_image, (x1, y1), (x2, y2), color, -1)
                    
                    # Draw cell border
                    cv2.rectangle(debug_image, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    
                    # Add piece information
                    self._add_piece_info(debug_image, piece, (x1, y1), cell_size)
            
            return debug_image
            
        except Exception as e:
            logger.error(f"Error creating debug board: {e}")
            return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def _add_piece_info(self, image: np.ndarray, piece: Piece, position: Tuple[int, int], 
                        cell_size: int) -> None:
        """Add piece information to debug board cell"""
        try:
            x, y = position
            
            # Piece color label
            color_text = piece.color.value[:3].upper()
            text_x = x + cell_size // 2 - 15
            text_y = y + cell_size // 2 + 5
            
            cv2.putText(image, color_text, (text_x, text_y), self.font, 0.4, 
                       (255, 255, 255), 1)
            
            # Power-up indicator
            if piece.is_power_up():
                power_up_text = piece.power_up.value[:3].upper()
                cv2.putText(image, power_up_text, (text_x, text_y + 15), self.font, 0.3, 
                           (255, 255, 0), 1)
            
            # Obstacle indicator
            if piece.has_obstacle():
                obstacle_text = piece.obstacle.value[:3].upper()
                cv2.putText(image, obstacle_text, (text_x, text_y + 30), self.font, 0.3, 
                           (0, 255, 255), 1)
            
        except Exception as e:
            logger.error(f"Error adding piece info: {e}")
    
    def save_visualization(self, image: np.ndarray, filename: str) -> bool:
        """
        Save visualization to file
        
        Args:
            image: Image to save
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = cv2.imwrite(filename, image)
            if success:
                logger.info(f"Visualization saved to {filename}")
            else:
                logger.error(f"Failed to save visualization to {filename}")
            return success
            
        except Exception as e:
            logger.error(f"Error saving visualization: {e}")
            return False