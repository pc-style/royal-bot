"""
Image Processing Module for Royal Match Bot
Handles screenshot analysis, board detection, and piece classification.
"""

import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from typing import Tuple, List, Optional, Dict
import logging

from .game_rules import PieceColor, PowerUpType, ObstacleType, Piece

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image processing and board extraction from screenshots"""
    
    def __init__(self):
        # Color ranges for piece detection (HSV format)
        self.color_ranges = {
            PieceColor.RED: {
                'lower': np.array([0, 100, 100]),
                'upper': np.array([10, 255, 255])
            },
            PieceColor.BLUE: {
                'lower': np.array([100, 100, 100]),
                'upper': np.array([130, 255, 255])
            },
            PieceColor.GREEN: {
                'lower': np.array([40, 100, 100]),
                'upper': np.array([80, 255, 255])
            },
            PieceColor.YELLOW: {
                'lower': np.array([20, 100, 100]),
                'upper': np.array([30, 255, 255])
            },
            PieceColor.PURPLE: {
                'lower': np.array([130, 100, 100]),
                'upper': np.array([160, 255, 255])
            },
            PieceColor.ORANGE: {
                'lower': np.array([10, 100, 100]),
                'upper': np.array([20, 255, 255])
            }
        }
        
        # Power-up detection templates (placeholder for now)
        self.power_up_templates = {}
        
    def extract_game_board(self, screenshot_path: str) -> Optional[np.ndarray]:
        """
        Extract the game board from a screenshot
        
        Args:
            screenshot_path: Path to the screenshot image
            
        Returns:
            Cropped board image or None if detection fails
        """
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Failed to load image: {screenshot_path}")
                return None
            
            # Convert to RGB for processing
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect board boundaries
            board_region = self._detect_board_boundaries(image_rgb)
            if board_region is None:
                logger.warning("Could not detect board boundaries, using full image")
                return image_rgb
            
            # Crop to board region
            x, y, w, h = board_region
            board_image = image_rgb[y:y+h, x:x+w]
            
            logger.info(f"Extracted board region: {board_region}")
            return board_image
            
        except Exception as e:
            logger.error(f"Error extracting game board: {e}")
            return None
    
    def _detect_board_boundaries(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the boundaries of the game board in the image
        
        Args:
            image: Input image
            
        Returns:
            (x, y, width, height) of board region or None
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
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
                
                # Check if it's roughly rectangular
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = w / h
                    
                    # Game board should be roughly square (aspect ratio close to 1)
                    if 0.8 <= aspect_ratio <= 1.2 and w > 200 and h > 200:
                        board_candidates.append((x, y, w, h))
            
            if not board_candidates:
                return None
            
            # Return the largest candidate (most likely to be the main board)
            board_candidates.sort(key=lambda x: x[2] * x[3], reverse=True)
            return board_candidates[0]
            
        except Exception as e:
            logger.error(f"Error detecting board boundaries: {e}")
            return None
    
    def identify_grid_cells(self, board_image: np.ndarray, grid_size: int = 8) -> List[List[Tuple[int, int, int, int]]]:
        """
        Divide the board into individual cell positions
        
        Args:
            board_image: The cropped board image
            grid_size: Size of the grid (8x8 or 9x9)
            
        Returns:
            2D list of (x, y, width, height) for each cell
        """
        try:
            height, width = board_image.shape[:2]
            
            # Calculate cell dimensions
            cell_width = width // grid_size
            cell_height = height // grid_size
            
            # Create grid of cell coordinates
            grid_cells = []
            for row in range(grid_size):
                row_cells = []
                for col in range(grid_size):
                    x = col * cell_width
                    y = row * cell_height
                    w = cell_width
                    h = cell_height
                    row_cells.append((x, y, w, h))
                grid_cells.append(row_cells)
            
            return grid_cells
            
        except Exception as e:
            logger.error(f"Error identifying grid cells: {e}")
            return []
    
    def classify_piece_type(self, cell_image: np.ndarray) -> Piece:
        """
        Classify the type of piece in a cell image
        
        Args:
            cell_image: Image of a single cell
            
        Returns:
            Piece object with color, power-up, and obstacle information
        """
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(cell_image, cv2.COLOR_RGB2HSV)
            
            # Detect color
            color = self._detect_piece_color(hsv)
            
            # Detect power-ups
            power_up = self._detect_power_up(cell_image)
            
            # Detect obstacles
            obstacle = self._detect_obstacle(cell_image)
            
            return Piece(
                color=color,
                power_up=power_up,
                obstacle=obstacle
            )
            
        except Exception as e:
            logger.error(f"Error classifying piece: {e}")
            return Piece(color=PieceColor.EMPTY)
    
    def _detect_piece_color(self, hsv_image: np.ndarray) -> PieceColor:
        """
        Detect the color of a piece using HSV color ranges
        
        Args:
            hsv_image: HSV image of the cell
            
        Returns:
            Detected piece color
        """
        try:
            # Calculate average HSV values for the cell
            avg_hsv = np.mean(hsv_image, axis=(0, 1))
            
            # Check each color range
            best_match = PieceColor.EMPTY
            best_score = 0
            
            for color, ranges in self.color_ranges.items():
                lower = ranges['lower']
                upper = ranges['upper']
                
                # Check if average HSV falls within range
                if np.all(avg_hsv >= lower) and np.all(avg_hsv <= upper):
                    # Calculate how well it fits (distance from range center)
                    center = (lower + upper) / 2
                    distance = np.linalg.norm(avg_hsv - center)
                    score = 1.0 / (1.0 + distance)
                    
                    if score > best_score:
                        best_score = score
                        best_match = color
            
            # If no clear match, try alternative detection methods
            if best_match == PieceColor.EMPTY:
                best_match = self._detect_color_alternative(hsv_image)
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error detecting piece color: {e}")
            return PieceColor.EMPTY
    
    def _detect_color_alternative(self, hsv_image: np.ndarray) -> PieceColor:
        """
        Alternative color detection using clustering
        
        Args:
            hsv_image: HSV image of the cell
            
        Returns:
            Detected piece color
        """
        try:
            # Reshape image for clustering
            pixels = hsv_image.reshape(-1, 3)
            
            # Use K-means to find dominant colors
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the dominant cluster
            dominant_cluster = kmeans.cluster_centers_[0]
            
            # Map HSV to color using simple thresholds
            h, s, v = dominant_cluster
            
            if v < 50:  # Too dark
                return PieceColor.EMPTY
            if s < 50:  # Too desaturated
                return PieceColor.EMPTY
            
            # Simple color mapping based on hue
            if 0 <= h < 15 or 165 <= h < 180:
                return PieceColor.RED
            elif 15 <= h < 45:
                return PieceColor.ORANGE
            elif 45 <= h < 75:
                return PieceColor.YELLOW
            elif 75 <= h < 105:
                return PieceColor.GREEN
            elif 105 <= h < 135:
                return PieceColor.BLUE
            elif 135 <= h < 165:
                return PieceColor.PURPLE
            else:
                return PieceColor.EMPTY
                
        except Exception as e:
            logger.error(f"Error in alternative color detection: {e}")
            return PieceColor.EMPTY
    
    def _detect_power_up(self, cell_image: np.ndarray) -> Optional[PowerUpType]:
        """
        Detect power-ups in a cell image
        
        Args:
            cell_image: Image of a single cell
            
        Returns:
            PowerUpType if detected, None otherwise
        """
        # TODO: Implement power-up detection using template matching
        # For now, return None (basic implementation)
        return None
    
    def _detect_obstacle(self, cell_image: np.ndarray) -> Optional[ObstacleType]:
        """
        Detect obstacles in a cell image
        
        Args:
            cell_image: Image of a single cell
            
        Returns:
            ObstacleType if detected, None otherwise
        """
        # TODO: Implement obstacle detection
        # For now, return None (basic implementation)
        return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better analysis
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                if image.dtype == np.uint8:
                    # Normalize to 0-1 range
                    image = image.astype(np.float32) / 255.0
            
            # Apply slight Gaussian blur to reduce noise
            if len(image.shape) == 3:
                image = cv2.GaussianBlur(image, (3, 3), 0)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def visualize_board_analysis(self, board_image: np.ndarray, grid_cells: List[List[Tuple[int, int, int, int]]], 
                                piece_matrix: List[List[Piece]]) -> np.ndarray:
        """
        Create a visualization of the board analysis
        
        Args:
            board_image: The board image
            grid_cells: Grid cell coordinates
            piece_matrix: 2D matrix of detected pieces
            
        Returns:
            Annotated image showing the analysis
        """
        try:
            # Create a copy for visualization
            vis_image = board_image.copy()
            
            # Draw grid lines
            for row in grid_cells:
                for x, y, w, h in row:
                    cv2.rectangle(vis_image, (x, y), (x + w, y + h), (255, 255, 255), 2)
            
            # Add piece information
            for row_idx, row in enumerate(piece_matrix):
                for col_idx, piece in enumerate(row):
                    if row_idx < len(grid_cells) and col_idx < len(grid_cells[row_idx]):
                        x, y, w, h = grid_cells[row_idx][col_idx]
                        
                        # Add color label
                        color_text = piece.color.value.upper()[:3]
                        cv2.putText(vis_image, color_text, (x + 5, y + 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        
                        # Add power-up indicator
                        if piece.power_up:
                            power_text = piece.power_up.value.upper()[:3]
                            cv2.putText(vis_image, power_text, (x + 5, y + h - 5), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            return vis_image
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return board_image