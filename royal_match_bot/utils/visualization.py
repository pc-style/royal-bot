"""
Visualization module for Royal Match bot.
Handles drawing suggestions and annotations on game images.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from ..core.move_generator import Move


def visualize_suggested_move(original_image: np.ndarray, move: Move, reasoning: str = "") -> np.ndarray:
    """
    Draw arrows/highlights on original screenshot to show suggested move.
    
    Args:
        original_image: Original screenshot as numpy array
        move: Move to visualize
        reasoning: Optional reasoning text to display
        
    Returns:
        Annotated image with move visualization
    """
    if move is None:
        return original_image
    
    # Create a copy to avoid modifying original
    annotated_image = original_image.copy()
    
    # Convert positions to pixel coordinates (this would need proper board detection)
    pos1_pixel = _board_pos_to_pixel(move.pos1, annotated_image.shape)
    pos2_pixel = _board_pos_to_pixel(move.pos2, annotated_image.shape)
    
    # Draw circles at both positions
    cv2.circle(annotated_image, pos1_pixel, 20, (255, 0, 0), 3)  # Red circle
    cv2.circle(annotated_image, pos2_pixel, 20, (0, 255, 0), 3)  # Green circle
    
    # Draw arrow between positions
    cv2.arrowedLine(annotated_image, pos1_pixel, pos2_pixel, (255, 255, 0), 3)
    
    # Add text with score and reasoning
    text_y = 30
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Score text
    score_text = f"Score: {move.score:.1f}"
    cv2.putText(annotated_image, score_text, (10, text_y), font, 0.7, (255, 255, 255), 2)
    text_y += 30
    
    # Move description
    move_text = f"Move: {move.pos1} -> {move.pos2}"
    cv2.putText(annotated_image, move_text, (10, text_y), font, 0.6, (255, 255, 255), 2)
    text_y += 25
    
    # Reasoning (split into multiple lines if too long)
    if reasoning:
        words = reasoning.split()
        line = ""
        for word in words:
            if len(line + word) < 50:  # Approximate character limit per line
                line += word + " "
            else:
                cv2.putText(annotated_image, line.strip(), (10, text_y), font, 0.5, (255, 255, 255), 1)
                text_y += 20
                line = word + " "
        
        # Add remaining text
        if line.strip():
            cv2.putText(annotated_image, line.strip(), (10, text_y), font, 0.5, (255, 255, 255), 1)
    
    return annotated_image


def highlight_matches(image: np.ndarray, match_positions: list, board_shape: Tuple[int, int]) -> np.ndarray:
    """
    Highlight matching pieces on the board.
    
    Args:
        image: Board image
        match_positions: List of (row, col) positions that will be matched
        board_shape: Shape of the board (rows, cols)
        
    Returns:
        Image with highlighted matches
    """
    highlighted_image = image.copy()
    
    for pos in match_positions:
        pixel_pos = _board_pos_to_pixel(pos, image.shape, board_shape)
        cv2.circle(highlighted_image, pixel_pos, 15, (255, 255, 0), 2)  # Yellow highlight
    
    return highlighted_image


def draw_board_grid(image: np.ndarray, board_shape: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Draw grid lines over the board for debugging.
    
    Args:
        image: Board image
        board_shape: Shape of the board (rows, cols)
        
    Returns:
        Image with grid overlay
    """
    grid_image = image.copy()
    height, width = image.shape[:2]
    rows, cols = board_shape
    
    # Draw horizontal lines
    for i in range(1, rows):
        y = int(i * height / rows)
        cv2.line(grid_image, (0, y), (width, y), (128, 128, 128), 1)
    
    # Draw vertical lines
    for i in range(1, cols):
        x = int(i * width / cols)
        cv2.line(grid_image, (x, 0), (x, height), (128, 128, 128), 1)
    
    return grid_image


def save_annotated_image(image: np.ndarray, filepath: str) -> bool:
    """
    Save annotated image to file.
    
    Args:
        image: Image to save
        filepath: Path to save the image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert RGB to BGR for OpenCV
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filepath, bgr_image)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def _board_pos_to_pixel(board_pos: Tuple[int, int], image_shape: Tuple[int, int], 
                       board_shape: Tuple[int, int] = (8, 8)) -> Tuple[int, int]:
    """
    Convert board position to pixel coordinates.
    
    Args:
        board_pos: Board position (row, col)
        image_shape: Shape of the image (height, width, channels)
        board_shape: Shape of the board (rows, cols)
        
    Returns:
        Pixel coordinates (x, y)
    """
    row, col = board_pos
    board_rows, board_cols = board_shape
    height, width = image_shape[:2]
    
    # Calculate cell size
    cell_height = height // board_rows
    cell_width = width // board_cols
    
    # Calculate center of the cell
    x = int(col * cell_width + cell_width // 2)
    y = int(row * cell_height + cell_height // 2)
    
    return (x, y)


def create_move_preview(board_image: np.ndarray, move: Move) -> np.ndarray:
    """
    Create a preview showing the board state after a move.
    
    Args:
        board_image: Current board image
        move: Move to preview
        
    Returns:
        Image showing predicted board state
    """
    # TODO: Implement board state prediction visualization
    # For now, just return the original image with move highlighted
    return visualize_suggested_move(board_image, move)


def add_debug_info(image: np.ndarray, debug_info: dict) -> np.ndarray:
    """
    Add debug information overlay to an image.
    
    Args:
        image: Image to annotate
        debug_info: Dictionary with debug information
        
    Returns:
        Image with debug overlay
    """
    debug_image = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    y_offset = image.shape[0] - 100  # Start from bottom
    line_height = 20
    
    for key, value in debug_info.items():
        text = f"{key}: {value}"
        cv2.putText(debug_image, text, (10, y_offset), font, 0.5, (255, 255, 255), 1)
        y_offset += line_height
    
    return debug_image