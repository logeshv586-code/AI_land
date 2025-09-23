# Tetris Block Game

A classic Tetris game implemented in Python using Pygame.

## Features

- Classic Tetris gameplay with all 7 tetromino pieces (I, O, T, S, Z, J, L)
- Piece rotation and movement
- Line clearing mechanics
- Scoring system with level progression
- Game over detection
- Next piece preview

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```
   python tetris.py
   ```

2. Controls:
   - **Left Arrow**: Move piece left
   - **Right Arrow**: Move piece right
   - **Down Arrow**: Move piece down faster
   - **Up Arrow**: Rotate piece
   - **Spacebar**: Drop piece instantly
   - **R**: Restart game (when game over)

## Game Rules

- Pieces fall from the top of the screen
- Use the arrow keys to move and rotate pieces
- Complete horizontal lines to clear them and score points
- The game speeds up as you progress through levels
- Game ends when pieces reach the top of the board

## Scoring

- Points are awarded for clearing lines
- Score increases with level multiplier
- Level increases every 10 lines cleared
- Fall speed increases with each level

Enjoy playing Tetris!