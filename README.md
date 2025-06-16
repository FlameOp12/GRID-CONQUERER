# Grid Conquer

A turn-based strategy game where two players battle on an 8×8 grid to destroy each other's Crown.

## Game Rules

### Unit Types
- 🪖 Soldier: Moves and attacks orthogonally
- 🛡️ Knight: Moves and attacks diagonally
- 🧙 Healer: Moves and heals in all directions
- 🧱 Wall: Static defensive unit
- 👑 Crown: Your main objective - protect it!

### Game Phases
1. **Placement Phase**
   - Players take turns placing their units
   - Player 1 places in bottom 3 rows
   - Player 2 places in top 3 rows
   - Crown must be placed within starting area

2. **Battle Phase**
   - Players take turns moving and attacking
   - Each unit can perform one action per turn
   - Victory is achieved by destroying the enemy Crown

### Unit Actions
- **Movement**: Move to an adjacent tile based on unit type
- **Attack**: Deal 50 damage to an adjacent enemy unit
- **Heal**: Healers can heal adjacent friendly units for 30 HP (costs 30 HP)

## Setup and Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python main.py
```

## Controls

- **Left Click**: Select unit or perform action
- **Close Window**: Exit game

## Game Features

- Visual health bars for all units
- Clear indication of valid moves and attacks
- Turn-based gameplay with alternating players
- Strategic unit placement and combat
- Victory condition tracking

## Development

The game is built using:
- Python 3.8+
- Pygame for graphics and user interaction
- NumPy for grid management

## Project Structure

```
grid_conquer/
├── main.py              # Main game entry point
├── game_engine.py       # Core game logic
├── units.py            # Unit classes and behaviors
├── ui.py               # User interface management
├── constants.py        # Game constants and settings
└── requirements.txt    # Project dependencies
``` 