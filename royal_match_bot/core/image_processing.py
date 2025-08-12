"""
Image Processing Module for Royal Match Bot
Handles screenshot analysis, board detection, and piece classification.
"""

import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from typing import Tuple, List, Optional
import logging

from .game_rules import PieceColor, PowerUpType, ObstacleType, Piece

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoardDetector:
    """Detects and extracts the game board from screenshots"""
    
    def __init__(self):
        # Color ranges for detecting board boundaries
        self.board_colors = {
            'brown': ([10, 50, 50], [20, 255, 255]),  # HSV ranges
            'dark_brown': ([5, 30, 30], [15, 200, 200])
        }
        
        # Expected board dimensions (can be adjusted)
        self.expected_grid_size = (8, 8)
        self.min_board_area = 10000  # Minimum area to consider as board
    
    def extract_game_board(self, screenshot: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect game board boundaries in screenshot and crop to playable area
        
        Args:
            screenshot: Full screenshot as numpy array (BGR format)
            
        Returns:
            Cropped board image or None if detection fails
        """
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            
            # Create mask for board colors
            board_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            for color_name, (lower, upper) in self.board_colors.items():
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(hsv, lower, upper)
                board_mask = cv2.bitwise_or(board_mask, mask)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(board_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                logger.warning("No board contours found")
                return None
            
            # Find the largest contour (should be the board)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area < self.min_board_area:
                logger.warning(f"Board area too small: {area}")
                return None
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Crop the board area
            board_image = screenshot[y:y+h, x:x+w]
            
            logger.info(f"Board extracted: {w}x{h} at ({x}, {y})")
            return board_image
            
        except Exception as e:
            logger.error(f"Error extracting board: {e}")
            return None
    
    def identify_grid_cells(self, board_image: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """
        Divide board into individual cell positions
        
        Args:
            board_image: Cropped board image
            
        Returns:
            Tuple of (grid_image, cell_coordinates)
        """
        try:
            height, width = board_image.shape[:2]
            
            # Calculate cell dimensions
            cell_width = width // self.expected_grid_size[0]
            cell_height = height // self.expected_grid_size[1]
            
            # Create grid overlay
            grid_image = board_image.copy()
            
            # Draw grid lines
            for i in range(1, self.expected_grid_size[0]):
                x = i * cell_width
                cv2.line(grid_image, (x, 0), (x, height), (0, 255, 0), 2)
            
            for i in range(1, self.expected_grid_size[1]):
                y = i * cell_height
                cv2.line(grid_image, (0, y), (width, y), (0, 255, 0), 2)
            
            # Generate cell coordinates (center points)
            cell_coords = []
            for row in range(self.expected_grid_size[1]):
                for col in range(self.expected_grid_size[0]):
                    center_x = col * cell_width + cell_width // 2
                    center_y = row * cell_height + cell_height // 2
                    cell_coords.append((center_x, center_y))
            
            return grid_image, cell_coords
            
        except Exception as e:
            logger.error(f"Error identifying grid cells: {e}")
            return board_image, []

class PieceClassifier:
    """Classifies individual pieces based on color and pattern analysis"""
    
    def __init__(self):
        # Define color ranges for each piece type (HSV)
        self.color_ranges = {
            PieceColor.RED: ([0, 100, 100], [10, 255, 255]),
            PieceColor.BLUE: ([100, 100, 100], [130, 255, 255]),
            PieceColor.GREEN: ([40, 100, 100], [80, 255, 255]),
            PieceColor.YELLOW: ([20, 100, 100], [30, 255, 255]),
            PieceColor.PURPLE: ([130, 100, 100], [160, 255, 255]),
            PieceColor.ORANGE: ([10, 100, 100], [20, 255, 255])
        }
        
        # Power-up detection templates (simplified)
        self.power_up_patterns = {
            PowerUpType.ROCKET: "horizontal_line",
            PowerUpType.TNT: "cross_pattern",
            PowerUpType.PROPELLER: "square_pattern",
            PowerUpType.LIGHT_BALL: "star_pattern"
        }
    
    def classify_piece_type(self, cell_image: np.ndarray) -> Piece:
        """
        Classify a piece based on its image
        
        Args:
            cell_image: Image of a single cell
            
        Returns:
            Piece object with classification
        """
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(cell_image, cv2.COLOR_BGR2HSV)
            
            # Get dominant color using K-means clustering
            pixels = hsv.reshape(-1, 3)
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the most common color
            labels = kmeans.labels_
            centers = kmeans.cluster_centers_
            
            # Find the cluster with most pixels
            unique_labels, counts = np.unique(labels, return_counts=True)
            dominant_cluster = unique_labels[np.argmax(counts)]
            dominant_color = centers[dominant_cluster]
            
            # Classify the color
            piece_color = self._classify_color(dominant_color)
            
            # Check for power-ups (simplified detection)
            power_up = self._detect_power_up(cell_image)
            
            # Check for obstacles (simplified detection)
            obstacle = self._detect_obstacle(cell_image)
            
            return Piece(
                color=piece_color,
                power_up=power_up,
                obstacle=obstacle
            )
            
        except Exception as e:
            logger.error(f"Error classifying piece: {e}")
            return Piece(color=PieceColor.EMPTY)
    
    def _classify_color(self, hsv_color: np.ndarray) -> PieceColor:
        """Classify HSV color to piece color"""
        h, s, v = hsv_color
        
        # Check each color range
        for color, (lower, upper) in self.color_ranges.items():
            if (lower[0] <= h <= upper[0] and 
                lower[1] <= s <= upper[1] and 
                lower[2] <= v <= upper[2]):
                return color
        
        # If no match, return empty
        return PieceColor.EMPTY
    
    def _detect_power_up(self, cell_image: np.ndarray) -> Optional[PowerUpType]:
        """Detect power-up patterns in cell image"""
        # This is a simplified detection - in practice, you'd use more sophisticated
        # template matching or machine learning approaches
        
        # Convert to grayscale
        gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
        
        # Simple edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Count edge pixels as a simple pattern indicator
        edge_density = np.sum(edges > 0) / edges.size
        
        # Very basic heuristics
        if edge_density > 0.3:  # High edge density might indicate power-up
            # This is where you'd implement actual power-up detection
            # For now, return None
            pass
        
        return None
    
    def _detect_obstacle(self, cell_image: np.ndarray) -> Optional[ObstacleType]:
        """Detect obstacles in cell image"""
        # Similar to power-up detection, this would use more sophisticated methods
        # For now, return None
        return None

def preprocess_screenshot(screenshot_path: str) -> Optional[np.ndarray]:
    """
    Load and preprocess a screenshot for analysis
    
    Args:
        screenshot_path: Path to screenshot file
        
    Returns:
        Preprocessed image as numpy array
    """
    try:
        # Load image
        if screenshot_path.endswith(('.png', '.jpg', '.jpeg')):
            image = cv2.imread(screenshot_path)
        else:
            # Try PIL for other formats
            pil_image = Image.open(screenshot_path)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        if image is None:
            logger.error(f"Could not load image: {screenshot_path}")
            return None
        
        # Resize if too large (for performance)
        max_dimension = 1200
        height, width = image.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # Apply basic preprocessing
        # Gaussian blur to reduce noise
        image = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Enhance contrast
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return image
        
    except Exception as e:
        logger.error(f"Error preprocessing screenshot: {e}")
        return None

def debug_visualization(image: np.ndarray, title: str = "Debug Image") -> None:
    """Display image for debugging purposes"""
    try:
        # Convert BGR to RGB for matplotlib
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(rgb_image)
        plt.title(title)
        plt.axis('off')
        plt.show()
    except Exception as e:
        logger.error(f"Error displaying debug image: {e}")