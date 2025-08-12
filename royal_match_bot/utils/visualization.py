"""
Visualization Utility Module for Royal Match Bot
Handles drawing move suggestions and board analysis on images.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

from ..core.game_rules import Move, Piece, PieceColor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoveVisualizer:
    """Visualizes move suggestions and board analysis on images"""
    
    def __init__(self):
        # Color definitions for visualization
        self.colors = {
            'arrow': (0, 255, 0),      # Green arrow
            'highlight': (255, 255, 0), # Yellow highlight
            'text': (255, 255, 255),    # White text
            'background': (0, 0, 0),    # Black background
            'score_good': (0, 255, 0),  # Green for good scores
            'score_medium': (255, 165, 0), # Orange for medium scores
            'score_poor': (255, 0, 0)   # Red for poor scores
        }
        
        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.font_thickness = 2
        
    def visualize_suggested_move(self, original_image: np.ndarray, move: Move, 
                                reasoning: str, grid_cells: Optional[List[List[Tuple[int, int, int, int]]]] = None) -> np.ndarray:
        """
        Draw the suggested move on the original image
        
        Args:
            original_image: The original screenshot
            move: The suggested move
            reasoning: Explanation for the move
            grid_cells: Grid cell coordinates for precise positioning
            
        Returns:
            Annotated image showing the move suggestion
        """
        try:
            # Create a copy for visualization
            vis_image = original_image.copy()
            
            if grid_cells:
                # Use grid cell coordinates for precise positioning
                self._draw_move_on_grid(vis_image, move, grid_cells)
            else:
                # Use estimated positions (less precise)
                self._draw_move_estimated(vis_image, move)
            
            # Add reasoning text
            self._add_reasoning_text(vis_image, reasoning, move.score)
            
            # Add move score
            self._add_score_display(vis_image, move.score)
            
            logger.info("Move visualization completed")
            return vis_image
            
        except Exception as e:
            logger.error(f"Error visualizing suggested move: {e}")
            return original_image
    
    def _draw_move_on_grid(self, image: np.ndarray, move: Move, 
                           grid_cells: List[List[Tuple[int, int, int, int]]]) -> None:
        """Draw move using precise grid cell coordinates"""
        try:
            row1, col1 = move.pos1
            row2, col2 = move.pos2
            
            # Get cell coordinates
            if (row1 < len(grid_cells) and col1 < len(grid_cells[row1]) and
                row2 < len(grid_cells) and col2 < len(grid_cells[row2])):
                
                x1, y1, w1, h1 = grid_cells[row1][col1]
                x2, y2, w2, h2 = grid_cells[row2][col2]
                
                # Calculate center points
                center1 = (x1 + w1 // 2, y1 + h1 // 2)
                center2 = (x2 + w2 // 2, y2 + h2 // 2)
                
                # Draw arrow between the two pieces
                self._draw_arrow(image, center1, center2)
                
                # Highlight the two pieces
                self._highlight_cell(image, (x1, y1, w1, h1))
                self._highlight_cell(image, (x2, y2, w2, h2))
                
        except Exception as e:
            logger.error(f"Error drawing move on grid: {e}")
    
    def _draw_move_estimated(self, image: np.ndarray, move: Move) -> None:
        """Draw move using estimated positions (fallback method)"""
        try:
            height, width = image.shape[:2]
            
            # Estimate cell size (assume 8x8 grid)
            grid_size = 8
            cell_width = width // grid_size
            cell_height = height // grid_size
            
            # Calculate estimated positions
            row1, col1 = move.pos1
            row2, col2 = move.pos2
            
            x1 = col1 * cell_width + cell_width // 2
            y1 = row1 * cell_height + cell_height // 2
            x2 = col2 * cell_width + cell_width // 2
            y2 = row2 * cell_height + cell_height // 2
            
            # Draw arrow
            self._draw_arrow(image, (x1, y1), (x2, y2))
            
            # Highlight cells
            self._highlight_estimated_cell(image, (x1, y1), cell_width, cell_height)
            self._highlight_estimated_cell(image, (x2, y2), cell_width, cell_height)
            
        except Exception as e:
            logger.error(f"Error drawing move estimated: {e}")
    
    def _draw_arrow(self, image: np.ndarray, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Draw an arrow between two points"""
        try:
            # Draw the main line
            cv2.line(image, start, end, self.colors['arrow'], 3)
            
            # Calculate arrow head
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            
            # Normalize
            length = np.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
                
                # Arrow head points
                arrow_length = 15
                arrow_angle = np.pi / 6  # 30 degrees
                
                # Calculate perpendicular vector
                perp_x = -dy
                perp_y = dx
                
                # Arrow head points
                head1_x = int(end[0] - arrow_length * (dx * np.cos(arrow_angle) + perp_x * np.sin(arrow_angle)))
                head1_y = int(end[1] - arrow_length * (dy * np.cos(arrow_angle) + perp_y * np.sin(arrow_angle)))
                
                head2_x = int(end[0] - arrow_length * (dx * np.cos(arrow_angle) - perp_x * np.sin(arrow_angle)))
                head2_y = int(end[1] - arrow_length * (dy * np.cos(arrow_angle) - perp_y * np.sin(arrow_angle)))
                
                # Draw arrow head
                cv2.line(image, end, (head1_x, head1_y), self.colors['arrow'], 3)
                cv2.line(image, end, (head2_x, head2_y), self.colors['arrow'], 3)
                
        except Exception as e:
            logger.error(f"Error drawing arrow: {e}")
    
    def _highlight_cell(self, image: np.ndarray, cell_coords: Tuple[int, int, int, int]) -> None:
        """Highlight a grid cell with a colored border"""
        try:
            x, y, w, h = cell_coords
            
            # Draw rectangle border
            cv2.rectangle(image, (x, y), (x + w, y + h), self.colors['highlight'], 3)
            
            # Add subtle fill
            overlay = image.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), self.colors['highlight'], -1)
            cv2.addWeighted(overlay, 0.2, image, 0.8, 0, image)
            
        except Exception as e:
            logger.error(f"Error highlighting cell: {e}")
    
    def _highlight_estimated_cell(self, image: np.ndarray, center: Tuple[int, int], 
                                 cell_width: int, cell_height: int) -> None:
        """Highlight an estimated cell position"""
        try:
            x, y = center
            half_w = cell_width // 2
            half_h = cell_height // 2
            
            # Draw rectangle border
            cv2.rectangle(image, (x - half_w, y - half_h), (x + half_w, y + half_h), 
                         self.colors['highlight'], 3)
            
        except Exception as e:
            logger.error(f"Error highlighting estimated cell: {e}")
    
    def _add_reasoning_text(self, image: np.ndarray, reasoning: str, score: float) -> None:
        """Add reasoning text to the image"""
        try:
            # Split reasoning into lines if it's long
            max_line_length = 50
            lines = []
            current_line = ""
            
            for word in reasoning.split():
                if len(current_line + " " + word) <= max_line_length:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Position text at top-left
            y_offset = 30
            for line in lines:
                # Add black background for text readability
                text_size = cv2.getTextSize(line, self.font, self.font_scale, self.font_thickness)[0]
                cv2.rectangle(image, (10, y_offset - text_size[1] - 5), 
                             (10 + text_size[0] + 10, y_offset + 5), 
                             self.colors['background'], -1)
                
                # Add text
                cv2.putText(image, line, (15, y_offset), self.font, self.font_scale, 
                           self.colors['text'], self.font_thickness)
                y_offset += 25
            
        except Exception as e:
            logger.error(f"Error adding reasoning text: {e}")
    
    def _add_score_display(self, image: np.ndarray, score: float) -> None:
        """Add score display to the image"""
        try:
            # Position score at top-right
            score_text = f"Score: {score:.1f}"
            
            # Get text size
            text_size = cv2.getTextSize(score_text, self.font, self.font_scale, self.font_thickness)[0]
            
            # Position at top-right
            x = image.shape[1] - text_size[0] - 20
            y = 30
            
            # Add background
            cv2.rectangle(image, (x - 10, y - text_size[1] - 5), 
                         (x + text_size[0] + 10, y + 5), 
                         self.colors['background'], -1)
            
            # Choose color based on score
            if score >= 100:
                color = self.colors['score_good']
            elif score >= 50:
                color = self.colors['score_medium']
            else:
                color = self.colors['score_poor']
            
            # Add text
            cv2.putText(image, score_text, (x, y), self.font, self.font_scale, 
                       color, self.font_thickness)
            
        except Exception as e:
            logger.error(f"Error adding score display: {e}")
    
    def create_move_comparison(self, original_image: np.ndarray, moves: List[Move], 
                              grid_cells: Optional[List[List[Tuple[int, int, int, int]]]] = None) -> np.ndarray:
        """
        Create a visualization comparing multiple moves
        
        Args:
            original_image: The original screenshot
            moves: List of moves to compare
            grid_cells: Grid cell coordinates
            
        Returns:
            Image showing all moves for comparison
        """
        try:
            # Create a copy for visualization
            vis_image = original_image.copy()
            
            # Draw each move with different colors
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            
            for i, move in enumerate(moves[:5]):  # Limit to 5 moves
                color = colors[i % len(colors)]
                
                # Temporarily change arrow color
                original_arrow_color = self.colors['arrow']
                self.colors['arrow'] = color
                
                # Draw the move
                if grid_cells:
                    self._draw_move_on_grid(vis_image, move, grid_cells)
                else:
                    self._draw_move_estimated(vis_image, move)
                
                # Restore original color
                self.colors['arrow'] = original_arrow_color
                
                # Add move label
                self._add_move_label(vis_image, move, i + 1, color)
            
            # Add legend
            self._add_move_legend(vis_image, moves[:5])
            
            return vis_image
            
        except Exception as e:
            logger.error(f"Error creating move comparison: {e}")
            return original_image
    
    def _add_move_label(self, image: np.ndarray, move: Move, move_num: int, color: Tuple[int, int, int]) -> None:
        """Add a label for a specific move"""
        try:
            # Position label near the move
            row1, col1 = move.pos1
            label_text = f"M{move_num}"
            
            # Estimate position (simplified)
            height, width = image.shape[:2]
            grid_size = 8
            cell_width = width // grid_size
            cell_height = height // grid_size
            
            x = col1 * cell_width + 10
            y = row1 * cell_height + 20
            
            # Add background
            text_size = cv2.getTextSize(label_text, self.font, 0.5, 1)[0]
            cv2.rectangle(image, (x - 5, y - text_size[1] - 5), 
                         (x + text_size[0] + 5, y + 5), 
                         self.colors['background'], -1)
            
            # Add text
            cv2.putText(image, label_text, (x, y), self.font, 0.5, color, 1)
            
        except Exception as e:
            logger.error(f"Error adding move label: {e}")
    
    def _add_move_legend(self, image: np.ndarray, moves: List[Move]) -> None:
        """Add a legend explaining the moves"""
        try:
            # Position legend at bottom-left
            y_start = image.shape[0] - 150
            x_start = 10
            
            # Add background
            cv2.rectangle(image, (x_start, y_start), (x_start + 300, y_start + 140), 
                         self.colors['background'], -1)
            
            # Add title
            cv2.putText(image, "Move Comparison", (x_start + 10, y_start + 20), 
                       self.font, 0.6, self.colors['text'], 1)
            
            # Add move details
            y_offset = y_start + 40
            for i, move in enumerate(moves):
                move_text = f"M{i+1}: {move.pos1} <-> {move.pos2} (Score: {move.score:.1f})"
                cv2.putText(image, move_text, (x_start + 10, y_offset), 
                           self.font, 0.4, self.colors['text'], 1)
                y_offset += 20
                
        except Exception as e:
            logger.error(f"Error adding move legend: {e}")
    
    def save_visualization(self, image: np.ndarray, output_path: str) -> bool:
        """
        Save the visualization to a file
        
        Args:
            image: Image to save
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert RGB to BGR for OpenCV
            if len(image.shape) == 3:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                bgr_image = image
            
            # Save image
            success = cv2.imwrite(output_path, bgr_image)
            
            if success:
                logger.info(f"Visualization saved to: {output_path}")
            else:
                logger.error(f"Failed to save visualization to: {output_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving visualization: {e}")
            return False