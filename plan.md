# royal-bot

# Royal Match Move Suggestion Bot - AI Development Prompt

## Project Overview
Create a Python-based bot that analyzes Royal Match game screenshots and suggests optimal moves. The bot should process board images, identify game pieces, find valid moves, and recommend the best action to take.

## Royal Match Game Rules & Mechanics

### Basic Gameplay
- **Match-3 puzzle game** where you swap adjacent pieces to create lines of 3+ identical colored items
- **Grid size**: Typically 8x8 or 9x9 depending on level
- **Piece types**: 6 main colors (red, blue, green, yellow, purple, orange) plus special pieces
- **Objectives**: Each level has specific goals (collect X of color Y, clear obstacles, etc.)
- **Moves limit**: Each level has a limited number of swaps allowed

### Power-ups (Created by matching 4+ pieces)
1. **Rocket** (4 in a line): Clears entire row or column
2. **TNT/Bomb** (5 in L/T shape): Clears 3x3 area around it
3. **Propeller** (4 in square): Flies to random location and clears area
4. **Light Ball** (5+ in line): Clears all pieces of target color

### Power-up Combinations
- **Rocket + Rocket**: Clears row AND column
- **TNT + TNT**: Clears 5x5 area
- **Light Ball + Any power-up**: Converts all pieces of most common color to that power-up type
- **Light Ball + Light Ball**: Clears entire board

### Obstacles & Special Elements
- **Boxes**: Require hits to break (1-3 layers)
- **Chains**: Lock pieces in place until broken
- **Jelly**: Spreads when adjacent pieces are cleared
- **Vases/Pots**: Must be cleared by matching adjacent pieces

## Technical Implementation Requirements

### 1. Image Processing & Board Recognition
```python
# Required libraries
import cv2
import numpy as np
import PIL
from sklearn.cluster import KMeans

# Core functions needed:
def extract_game_board(screenshot):
    """
    - Detect game board boundaries in screenshot
    - Crop to just the playable grid area
    - Return clean board image
    """

def identify_grid_cells(board_image):
    """
    - Divide board into individual cell positions
    - Account for piece animations/movements
    - Return grid coordinates for each cell
    """

def classify_piece_type(cell_image):
    """
    - Use color analysis and template matching
    - Identify: empty, red, blue, green, yellow, purple, orange
    - Detect power-ups: rocket, TNT, propeller, light ball
    - Recognize obstacles: boxes, chains, etc.
    - Return piece type and any special properties
    """
```

### 2. Game State Analysis
```python
def parse_level_objectives(screenshot):
    """
    - OCR the objective area (usually top-left)
    - Extract goals like "Collect 20 red pieces"
    - Parse remaining moves counter
    - Return structured objective data
    """

def build_board_matrix(board_image):
    """
    - Create 2D array representing current board state
    - Each cell contains: piece_type, color, power_up_type, obstacle_type
    - Handle empty spaces and falling pieces
    """
```

### 3. Move Generation & Validation
```python
def find_all_possible_moves(board_matrix):
    """
    - Check every adjacent pair for valid swaps
    - Only include moves that create 3+ matches
    - Consider both horizontal and vertical swaps
    - Return list of valid Move objects
    """

def simulate_move_effects(board_matrix, move):
    """
    - Simulate piece swap
    - Calculate all resulting matches and cascades
    - Track power-up activations and combinations
    - Return predicted board state after move
    """
```

### 4. Move Scoring & Strategy
```python
def score_move(move, board_state, objectives):
    """
    Scoring criteria (in order of priority):
    1. OBJECTIVE PROGRESS (100+ points)
       - Directly collects required pieces
       - Clears required obstacles
       - Spreads jelly if needed
    
    2. POWER-UP CREATION (50+ points)
       - Light Ball creation: +100
       - TNT creation: +75
       - Rocket creation: +50
       - Propeller creation: +40
    
    3. POWER-UP COMBINATIONS (75+ points)
       - Light Ball + Power-up: +150
       - TNT + TNT: +100
       - Other combinations: +75
    
    4. CASCADE POTENTIAL (25+ points)
       - Moves that create chain reactions
       - Multiple matches from single move
    
    5. BOARD CLEARING (10+ points)
       - Removes many pieces
       - Opens up new matching opportunities
    
    6. OBSTACLE CLEARING (30+ points)
       - Breaks boxes, chains, etc.
       - Clears path for future moves
    
    Return total score for the move
    """

def select_best_move(possible_moves, board_state, objectives):
    """
    - Score all possible moves
    - Apply strategic preferences:
      * Prioritize objective completion
      * Prefer power-up creation in lower board
      * Avoid moves that waste power-ups
      * Consider setup moves for future combinations
    - Return highest-scoring move with reasoning
    """
```

### 5. Output & Visualization
```python
def visualize_suggested_move(original_image, move, reasoning):
    """
    - Draw arrows/highlights on original screenshot
    - Show which pieces to swap
    - Display move score and reasoning text
    - Return annotated image
    """

def generate_move_explanation(move, score_breakdown):
    """
    Return human-readable explanation like:
    "Swap red piece at (3,4) with blue piece at (3,5)
     - Creates rocket (4 in a row)
     - Collects 6 red pieces toward objective
     - Score: 175 points
     - Reasoning: High objective progress + power-up creation"
    """
```

## Implementation Strategy

### Phase 1: Basic Board Recognition
1. Use template matching to identify piece colors
2. Implement grid detection and cell extraction
3. Create basic piece classification system
4. Test with simple board states

### Phase 2: Move Detection
1. Implement valid move finding algorithm
2. Add basic match detection (3+ in line)
3. Simple move scoring based on piece count
4. Test move suggestions on easy levels

### Phase 3: Advanced Features
1. Power-up recognition and combination logic
2. Objective parsing from screenshots
3. Sophisticated scoring system
4. Cascade simulation and multi-move planning

### Phase 4: Optimization
1. Improve piece recognition accuracy
2. Add support for all obstacle types
3. Fine-tune scoring weights based on testing
4. Handle edge cases and animations

## Error Handling & Edge Cases
- Handle partially animated boards (pieces falling)
- Deal with power-up effects obscuring board
- Account for different screen resolutions/devices
- Graceful degradation when piece recognition fails
- Validate that suggested moves are actually possible

## Testing Approach
1. Start with screenshot datasets from easy levels
2. Manually verify board recognition accuracy
3. Test move suggestions against known optimal solutions
4. Validate scoring system makes sense strategically
5. Test on progressively harder levels

## Success Metrics
- **Board recognition accuracy**: >95% piece identification
- **Move validity**: 100% of suggestions should be legal moves
- **Strategic quality**: Suggestions should prioritize objectives over random matching
- **Performance**: Process screenshot and return suggestion in <2 seconds

## Code Structure
```
royal_match_bot/
├── core/
│   ├── image_processing.py    # Screenshot analysis
│   ├── board_parser.py        # Grid and piece detection
│   ├── move_generator.py      # Find valid moves
│   ├── strategy_engine.py     # Move scoring and selection
│   └── game_rules.py         # Royal Match mechanics
├── utils/
│   ├── visualization.py      # Draw suggestions on images
│   └── debugging.py          # Development helpers
└── main.py                   # Entry point
```

Start with the basic board recognition and gradually add complexity. Focus on accuracy over speed initially, then optimize performance once the core logic is working reliably.
