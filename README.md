# Royal Match Move Suggestion Bot

An AI-powered bot that analyzes Royal Match game screenshots and suggests optimal moves. The bot processes board images, identifies game pieces, finds valid moves, and recommends the best action to take based on game objectives.

## Features

- **Image Processing**: Analyzes Royal Match screenshots to extract game board
- **Piece Recognition**: Identifies colored pieces, power-ups, and obstacles
- **Move Generation**: Finds all valid moves that create matches
- **Strategic Scoring**: Evaluates moves based on objectives and game strategy
- **Visualization**: Creates annotated images showing suggested moves
- **Debug Mode**: Detailed logging and analysis for development

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pc-style/royal-bot.git
cd royal-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Analyze a Royal Match screenshot:
```bash
python main.py --image screenshot.png
```

Save visualization to specific file:
```bash
python main.py --image screenshot.png --output suggestion.png
```

### Debug Mode

Run with detailed logging:
```bash
python main.py --image screenshot.png --debug
```

### Demo Mode

Run demo with test board (no screenshot needed):
```bash
python main.py --demo
```

## Project Structure

```
royal_match_bot/
├── core/
│   ├── image_processing.py    # Screenshot analysis and board extraction
│   ├── board_parser.py        # Grid detection and game state parsing
│   ├── move_generator.py      # Find and validate possible moves
│   ├── strategy_engine.py     # Move scoring and selection
│   └── game_rules.py         # Royal Match game mechanics
├── utils/
│   ├── visualization.py      # Draw suggestions on images
│   └── debugging.py          # Development and debugging helpers
└── main.py                   # Entry point and CLI interface
```

## How It Works

1. **Image Processing**: The bot loads a Royal Match screenshot and extracts the game board area
2. **Board Parsing**: The board is divided into a grid and each cell is analyzed to identify piece types and colors
3. **Move Generation**: All possible adjacent swaps are checked to find moves that create valid matches (3+ pieces)
4. **Move Scoring**: Each valid move is scored based on:
   - Objective progress (collecting required pieces)
   - Power-up creation potential
   - Cascade opportunities
   - Strategic value
5. **Best Move Selection**: The highest-scoring move is selected and explained
6. **Visualization**: An annotated image is created showing the suggested move

## Game Rules Supported

### Basic Mechanics
- Match-3 puzzle gameplay
- 8x8 or 9x9 grids
- 6 main piece colors (red, blue, green, yellow, purple, orange)
- Adjacent piece swapping

### Power-ups
- **Rocket** (4 in a line): Clears entire row or column
- **TNT/Bomb** (5 in L/T shape): Clears 3x3 area
- **Propeller** (4 in square): Clears random area
- **Light Ball** (5+ in line): Clears all pieces of target color

### Power-up Combinations
- Rocket + Rocket: Clears row AND column
- TNT + TNT: Clears 5x5 area
- Light Ball + Power-up: Converts all pieces of color to that power-up type
- Light Ball + Light Ball: Clears entire board

## Current Implementation Status

### ✅ Completed (Phase 1)
- Project structure and basic architecture
- Core module skeletons with planned interfaces
- Basic board representation and piece classification framework
- Move generation and validation logic
- Strategic scoring system foundation
- Visualization and debugging utilities
- CLI interface and demo mode

### 🚧 In Progress (Phase 2)
- Image processing and board recognition algorithms
- Piece color and type classification
- Template matching for piece identification
- Basic move scoring implementation

### 📋 Planned (Phase 3+)
- Advanced computer vision for accurate piece recognition
- Power-up detection and combination logic
- Objective parsing from screenshots (OCR)
- Cascade simulation and multi-move planning
- Performance optimization and accuracy improvements

## Development

### Running Tests
```bash
python main.py --demo  # Test with sample board
```

### Debug Mode
```bash
python main.py --image screenshot.png --debug
```

### Adding New Features
1. Core game logic goes in `royal_match_bot/core/`
2. Utility functions go in `royal_match_bot/utils/`
3. Follow the existing class and function structure
4. Add debug logging using the `DebugLogger` class

## Dependencies

- **opencv-python**: Image processing and computer vision
- **numpy**: Numerical operations and array handling
- **pillow**: Image loading and manipulation
- **scikit-learn**: Machine learning algorithms for classification

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes following the existing architecture
4. Test with the demo mode and debug output
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of service of Royal Match and similar games.

## Future Enhancements

- Real-time screen capture and analysis
- Mobile device integration
- Machine learning model training for piece recognition
- Advanced strategy algorithms
- Support for different game modes and level types
- Performance benchmarking and optimization