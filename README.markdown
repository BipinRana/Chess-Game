# Chess Game

A fully-featured chess game developed in Python, leveraging only its standard libraries and select external dependencies. This project was built from scratch as a solo endeavor, without relying on external tutorials, YouTube guides, or other GitHub repositories.

## Features

### 1. Single-Player Mode
- **Difficulty Levels**:
  - **Easy**: Powered by a custom implementation of the Minimax algorithm with alpha-beta pruning for efficient AI decision-making.
  - **Hard**: Integrates the Stockfish chess engine for a challenging experience.
  - **Note**: A medium difficulty level was planned but is currently incomplete and may exhibit bugs.
- Play against a computer opponent tailored to your skill level.

### 2. Multiplayer Mode
- Supports two-player matches.
- Players are paired based on their join order, ensuring seamless matchmaking.

### 3. Move Suggestion
- Powered by the Stockfish chess engine, providing high-quality move recommendations to assist players.

### 4. Move Tracking
- Highlights the most recent move to help players follow the game's progress.

### 5. Undo/Redo Functionality
- Allows players to undo or redo moves, offering flexibility during gameplay.

### 6. Pause Menu
- Accessible in-game menu with options to:
  - Pause the game
  - Restart the match
  - Return to the main menu
  - Quit the application

## Project Status
This project was developed as a solo effort and, while functional, may contain bugs or inefficiencies, particularly in the incomplete medium difficulty level. **Note**: Development on this project has been paused as of the last update.

## Credits
- **Assets**: All visual assets were created by [ToffeeBunny](https://toffeebunny.itch.io/). A huge thank you for providing these excellent resources!
- **Sound Effects**: Sourced from [Chess.com](https://chess.com/).
- **Chess Engine**: Move suggestions and AI in Hard mode are powered by [Stockfish](https://stockfishchess.org/). Visit their website for more information about this powerful open-source chess engine.

## Getting Started
To run the game locally:
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/Chess-Game.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure [Stockfish](https://stockfishchess.org/download/) is installed and properly configured for Hard mode and move suggestions.
4. Run the game:
   ```bash
   python main.py
   ```

## Contributing
While this project is currently on hold, contributions, bug reports, or suggestions are welcome. Please feel free to open an issue or submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).