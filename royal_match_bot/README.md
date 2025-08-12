# Royal Match Move Suggestion Bot

An intelligent Python-based bot that analyzes Royal Match game screenshots and suggests optimal moves. The bot processes board images, identifies game pieces, finds valid moves, and recommends the best action to take based on strategic analysis.

## Features

- **Image Processing**: Automatically detects and extracts game board from screenshots
- **Piece Recognition**: Identifies piece colors, power-ups, and obstacles using computer vision
- **Move Generation**: Finds all valid moves that create 3+ matches
- **Strategic Analysis**: Scores moves based on objectives, power-up creation, and board clearing
- **Visualization**: Draws move suggestions with arrows and explanations on screenshots
- **Debug Mode**: Comprehensive debugging and analysis tools for development

## Game Mechanics Supported

### Basic Gameplay
- Match-3 puzzle mechanics with 6 colors (red, blue, green, yellow, purple, orange)
- 8x8 or 9x9 grid boards
- Adjacent piece swapping to create lines of 3+ identical pieces

### Power-ups
- **Rocket** (4 in a line): Clears entire row or column
- **TNT/Bomb** (5 in L/T shape): Clears 3x3 area
- **Propeller** (4 in square): Flies to random location and clears area
- **Light Ball** (5+ in line): Clears all pieces of target color

### Obstacles
- **Boxes**: Multi-layer obstacles requiring hits to break
- **Chains**: Lock pieces in place until broken
- **Jelly**: Spreads when adjacent pieces are cleared
- **Vases/Pots**: Must be cleared by matching adjacent pieces

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenCV and other computer vision libraries
- Tesseract OCR (optional, for objective text recognition)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### System Dependencies (Ubuntu/Debian)
```bash
# Install OpenCV dependencies
sudo apt-get update
sudo apt-get install python3-opencv

# Install Tesseract (optional)
sudo apt-get install tesseract-ocr
```

## Usage

### Basic Usage
```bash
# Analyze a screenshot and get move suggestion
python main.py path/to/screenshot.png

# Save annotated image to specific file
python main.py path/to/screenshot.png --output my_move.png

# Enable debug mode for detailed analysis
python main.py path/to/screenshot.png --debug

# Run in test mode with generated data
python main.py --test
```

### Command Line Options
- `screenshot`: Path to the screenshot file to analyze
- `--output, -o`: Output file for annotated image (default: suggested_move.png)
- `--debug, -d`: Enable debug mode with detailed logging and analysis
- `--test, -t`: Run in test mode with generated data

### Example Output
```
============================================================
MOVE SUGGESTION
============================================================
Suggested Move: Swap piece at (3,4) with piece at (3,5)

Score: 175 points
Reasoning: Advances objectives (+100); Creates power-ups (+75)

Level Objectives:
- Collect 20 red (0.0% complete)
- Clear 5 boxes (0.0% complete)
============================================================
```

## Architecture

### Core Modules
- **`game_rules.py`**: Defines game mechanics, piece types, and scoring constants
- **`image_processing.py`**: Handles screenshot analysis and board detection
- **`board_parser.py`**: Parses board state and level objectives
- **`move_generator.py`**: Finds valid moves and simulates their effects
- **`strategy_engine.py`**: Scores moves and selects the best one

### Utility Modules
- **`visualization.py`**: Draws move suggestions and debugging information
- **`debugging.py`**: Provides development and testing support tools

### Main Entry Point
- **`main.py`**: Orchestrates the entire workflow from screenshot to move suggestion

## Scoring System

The bot uses a sophisticated scoring system that prioritizes:

1. **Objective Progress** (100+ points): Directly advances level goals
2. **Power-up Creation** (50+ points): Creates rockets, TNT, propellers, light balls
3. **Power-up Combinations** (75+ points): Combines multiple power-ups for greater effects
4. **Cascade Potential** (25+ points): Moves that create chain reactions
5. **Board Clearing** (10+ points): Removes many pieces and opens opportunities
6. **Obstacle Clearing** (30+ points): Breaks boxes, chains, and other barriers

## Development

### Project Structure
```
royal_match_bot/
├── core/                    # Core game logic modules
│   ├── game_rules.py       # Game mechanics and constants
│   ├── image_processing.py # Screenshot analysis
│   ├── board_parser.py     # Board state parsing
│   ├── move_generator.py   # Move generation and simulation
│   └── strategy_engine.py  # Move scoring and selection
├── utils/                   # Utility modules
│   ├── visualization.py    # Move visualization
│   └── debugging.py        # Development tools
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running Tests
```bash
# Run in test mode to verify functionality
python main.py --test

# Enable debug mode for detailed analysis
python main.py --test --debug
```

### Adding New Features
1. **New Piece Types**: Add to `PieceColor`, `PowerUpType`, or `ObstacleType` enums
2. **New Scoring Criteria**: Extend the scoring system in `StrategyEngine`
3. **Enhanced Recognition**: Improve piece detection in `PieceClassifier`
4. **New Game Mechanics**: Add rules to `game_rules.py` and update simulators

### Debugging
The bot includes comprehensive debugging tools:
- Performance tracking and timing
- Board state analysis and visualization
- Move analysis and scoring breakdown
- Detailed logging at multiple levels

## Performance

### Target Metrics
- **Board Recognition Accuracy**: >95% piece identification
- **Move Validity**: 100% of suggestions should be legal moves
- **Processing Time**: <2 seconds per screenshot
- **Strategic Quality**: Prioritizes objectives over random matching

### Optimization Tips
- Use debug mode to identify bottlenecks
- Monitor performance metrics in logs
- Adjust image preprocessing parameters for your screenshots
- Fine-tune scoring weights based on testing results

## Limitations and Future Improvements

### Current Limitations
- Simplified power-up and obstacle detection
- Basic OCR for objective parsing
- Limited support for complex board patterns
- No machine learning for piece recognition

### Planned Enhancements
- **Advanced Recognition**: Machine learning-based piece identification
- **Pattern Recognition**: Better detection of L/T shapes and special patterns
- **Multi-move Planning**: Look ahead multiple moves for better strategy
- **Level-specific Strategies**: Adapt strategies based on level type
- **Real-time Analysis**: Process live game feed instead of screenshots

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include logging for debugging
- Write docstrings for all functions
- Test new features thoroughly

## Troubleshooting

### Common Issues

**"No board contours found"**
- Ensure screenshot shows the full game board
- Check that board has sufficient contrast
- Try adjusting board detection parameters

**"Board matrix validation failed"**
- Verify screenshot quality and resolution
- Check that board is properly oriented
- Ensure no UI elements overlap the board

**"No valid moves found"**
- Board may be in a state with no possible matches
- Check if pieces are properly recognized
- Verify grid size settings match your game

### Getting Help
- Check the log file (`royal_match_bot.log`) for detailed error information
- Run with `--debug` flag for additional diagnostic output
- Verify all dependencies are properly installed
- Test with `--test` flag to verify basic functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the Royal Match mobile game
- Built with OpenCV, NumPy, and other open-source libraries
- Developed for educational and research purposes

## Version History

- **v1.0.0**: Initial release with basic functionality
  - Board detection and piece recognition
  - Move generation and validation
  - Strategic scoring system
  - Visualization and debugging tools