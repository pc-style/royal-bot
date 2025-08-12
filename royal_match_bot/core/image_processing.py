"""
Image processing module for Royal Match bot.
Handles screenshot analysis and board extraction.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional


def extract_game_board(screenshot: np.ndarray) -> np.ndarray:
    """
    Detect game board boundaries in screenshot and crop to just the playable grid area.
    
    Args:
        screenshot: Input screenshot as numpy array
        
    Returns:
        Clean board image as numpy array
    """
    # Detect board boundaries
    x1, y1, x2, y2 = detect_board_boundaries(screenshot)
    
    # Crop to board area
    board_image = screenshot[y1:y2, x1:x2]
    
    # Apply preprocessing to improve piece detection
    board_image = enhance_board_image(board_image)
    
    return board_image


def enhance_board_image(board_image: np.ndarray) -> np.ndarray:
    """
    Apply image enhancements to improve piece detection accuracy.
    
    Args:
        board_image: Raw board image
        
    Returns:
        Enhanced board image
    """
    # Convert to float for processing
    enhanced = board_image.astype(np.float32) / 255.0
    
    # Increase contrast slightly
    enhanced = cv2.convertScaleAbs(enhanced * 255, alpha=1.1, beta=10)
    
    # Apply slight gaussian blur to reduce noise
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    
    return enhanced


def detect_board_boundaries(screenshot: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Detect the boundaries of the game board in the screenshot using edge detection.
    
    Args:
        screenshot: Full screenshot as numpy array
        
    Returns:
        Tuple of (x1, y1, x2, y2) coordinates of board boundaries
    """
    height, width = screenshot.shape[:2]
    
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    
    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for rectangular contours that could be the game board
    board_candidates = []
    
    for contour in contours:
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Check if it's roughly rectangular (4 vertices)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter by size (board should be significant portion of screen)
            if area > (width * height * 0.1) and area < (width * height * 0.8):
                # Check aspect ratio (board should be roughly square)
                aspect_ratio = w / h
                if 0.8 <= aspect_ratio <= 1.2:
                    board_candidates.append((x, y, x + w, y + h, area))
    
    if board_candidates:
        # Select the largest candidate
        board_candidates.sort(key=lambda x: x[4], reverse=True)
        x1, y1, x2, y2, _ = board_candidates[0]
        return (x1, y1, x2, y2)
    
    # Fallback: use heuristic based on screen layout
    # Royal Match typically has the board in the center-lower portion
    margin_x = width // 8
    margin_y_top = height // 4
    margin_y_bottom = height // 6
    
    x1 = margin_x
    y1 = margin_y_top
    x2 = width - margin_x
    y2 = height - margin_y_bottom
    
    return (x1, y1, x2, y2)


def identify_grid_cells(board_image: np.ndarray) -> list:
    """
    Divide board into individual cell positions.
    Account for piece animations/movements.
    
    Args:
        board_image: Board image as numpy array
        
    Returns:
        Grid coordinates for each cell
    """
    # TODO: Implement grid cell identification
    # Return placeholder grid for 8x8 board
    grid_cells = []
    height, width = board_image.shape[:2]
    cell_height = height // 8
    cell_width = width // 8
    
    for row in range(8):
        for col in range(8):
            x = col * cell_width
            y = row * cell_height
            grid_cells.append((x, y, x + cell_width, y + cell_height))
    
    return grid_cells


def classify_piece_type(cell_image: np.ndarray) -> dict:
    """
    Use color analysis and template matching to identify piece types.
    
    Args:
        cell_image: Individual cell image as numpy array
        
    Returns:
        Dictionary with piece type and properties
    """
    if cell_image is None or cell_image.size == 0:
        return {
            'piece_type': 'empty',
            'color': 'empty',
            'power_up_type': None,
            'obstacle_type': None
        }
    
    # Basic color analysis using dominant color detection
    dominant_color = detect_dominant_color(cell_image)
    
    # Map dominant color to game piece colors
    piece_color = map_color_to_piece(dominant_color)
    
    # TODO: Add power-up detection logic
    # TODO: Add obstacle detection logic
    
    return {
        'piece_type': 'normal' if piece_color != 'empty' else 'empty',
        'color': piece_color,
        'power_up_type': None,
        'obstacle_type': None
    }


def detect_dominant_color(image: np.ndarray) -> Tuple[int, int, int]:
    """
    Detect the dominant color in an image using k-means clustering.
    
    Args:
        image: Input image as numpy array
        
    Returns:
        RGB tuple of dominant color
    """
    if image.size == 0:
        return (0, 0, 0)
    
    # Reshape image to list of pixels
    pixels = image.reshape(-1, 3)
    
    # Use k-means to find dominant colors
    from sklearn.cluster import KMeans
    
    try:
        # Find 2 clusters (background and piece)
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get cluster centers and their sizes
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        # Count pixels in each cluster
        unique, counts = np.unique(labels, return_counts=True)
        
        # Return the color of the largest cluster
        dominant_idx = unique[np.argmax(counts)]
        dominant_color = colors[dominant_idx]
        
        return tuple(map(int, dominant_color))
    
    except Exception:
        # Fallback: use mean color
        mean_color = np.mean(pixels, axis=0)
        return tuple(map(int, mean_color))


def map_color_to_piece(rgb_color: Tuple[int, int, int]) -> str:
    """
    Map an RGB color to a Royal Match piece color.
    
    Args:
        rgb_color: RGB color tuple
        
    Returns:
        Piece color string
    """
    r, g, b = rgb_color
    
    # If the color is too dark, consider it empty
    if r < 30 and g < 30 and b < 30:
        return 'empty'
    
    # Calculate color dominance ratios
    total = r + g + b
    if total == 0:
        return 'empty'
    
    r_ratio = r / total
    g_ratio = g / total
    b_ratio = b / total
    
    # Define color detection based on which channel is dominant
    # and the relative intensities
    
    # Red: high red component, low green and blue
    if r > g and r > b and r > 100:
        if r_ratio > 0.4:  # Red is dominant
            return 'red'
    
    # Blue: high blue component
    if b > r and b > g and b > 100:
        if b_ratio > 0.4:
            return 'blue'
    
    # Green: high green component
    if g > r and g > b and g > 100:
        if g_ratio > 0.4:
            return 'green'
    
    # Yellow: high red and green, low blue
    if r > 150 and g > 150 and b < 100:
        return 'yellow'
    
    # Purple: moderate red and blue, low green
    if r > 80 and b > 80 and g < r * 0.7 and g < b * 0.7:
        return 'purple'
    
    # Orange: high red, moderate green, low blue
    if r > 150 and g > 80 and g < r * 0.8 and b < 80:
        return 'orange'
    
    # If we can't classify definitively, make a best guess based on highest channel
    max_channel = max(r, g, b)
    if max_channel == r and r > 80:
        return 'red'
    elif max_channel == g and g > 80:
        return 'green'
    elif max_channel == b and b > 80:
        return 'blue'
    
    return 'unknown'


def preprocess_screenshot(image_path: str) -> np.ndarray:
    """
    Load and preprocess a screenshot for analysis.
    
    Args:
        image_path: Path to screenshot file
        
    Returns:
        Preprocessed image as numpy array
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    except Exception as e:
        print(f"Error preprocessing screenshot: {e}")
        return None