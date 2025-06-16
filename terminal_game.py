from game_engine import GameEngine
from constants import UnitType, GameState, BOARD_SIZE
from typing import Tuple, Optional

class TerminalGame:
    def __init__(self):
        self.game_engine = GameEngine()
        self.selected_position: Optional[Tuple[int, int]] = None

    def print_board(self):
        """Print the current game board with units."""
        print("\n   " + "  ".join(chr(65 + i) for i in range(BOARD_SIZE)))  # Column labels A-H
        for y in range(BOARD_SIZE):
            row = f"{y+1} "  # Row numbers 1-8
            for x in range(BOARD_SIZE):
                unit = self.game_engine.get_unit_at((x, y))
                if unit and unit.alive:
                    # Color coding: Player 1 (Blue) = 34, Player 2 (Red) = 31
                    color = 34 if unit.player == 1 else 31
                    cell = f"\033[{color}m{unit.get_symbol()}\033[0m"
                else:
                    cell = "·"
                row += f" {cell} "
            print(row)
        print()

    def print_unit_info(self, unit):
        """Print information about a unit."""
        print(f"\nUnit: {unit.get_symbol()}")
        print(f"Type: {unit.unit_type.name}")
        print(f"Player: {unit.player}")
        print(f"HP: {unit.hp}/{unit.max_hp}")
        if unit.unit_type == UnitType.HEALER:
            print("Can heal adjacent friendly units")
        elif unit.unit_type in [UnitType.SOLDIER, UnitType.KNIGHT]:
            print("Can attack adjacent enemy units")

    def get_position_input(self, prompt: str) -> Optional[Tuple[int, int]]:
        """Get a valid board position from user input."""
        while True:
            try:
                pos = input(prompt).strip().upper()
                if pos == 'Q':
                    return None
                if len(pos) != 2 or not pos[0].isalpha() or not pos[1].isdigit():
                    print("Invalid input! Use format 'A1' to 'H8' or 'Q' to quit")
                    continue
                x = ord(pos[0]) - ord('A')
                y = int(pos[1]) - 1
                if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                    return (x, y)
                print("Position out of bounds! Use A1 to H8")
            except ValueError:
                print("Invalid input! Use format 'A1' to 'H8'")

    def handle_placement_phase(self):
        """Handle the unit placement phase."""
        print("\n=== PLACEMENT PHASE ===")
        print("Place your units in your starting area:")
        print("Player 1 (Blue): Bottom 3 rows (6-8)")
        print("Player 2 (Red): Top 3 rows (1-3)")
        
        while self.game_engine.state == GameState.PLACEMENT_PHASE:
            self.print_board()
            player = self.game_engine.current_player
            print(f"\nPlayer {player}'s turn to place units")
            
            # Get the current player's units
            player_units = [u for u in self.game_engine.get_all_units() if u.player == player]
            
            # Determine which unit to place
            unit_type = None
            if len(player_units) == 0:
                unit_type = UnitType.SOLDIER
                print("Place your Soldier (🪖)")
            elif len(player_units) == 1:
                unit_type = UnitType.KNIGHT
                print("Place your Knight (🛡️)")
            elif len(player_units) == 2:
                unit_type = UnitType.HEALER
                print("Place your Healer (🧙)")
            elif len(player_units) == 3:
                unit_type = UnitType.WALL
                print("Place your Wall (🧱)")
            elif len(player_units) == 4:
                unit_type = UnitType.CROWN
                print("Place your Crown (👑)")
            else:
                self.game_engine.start_game()
                break

            pos = self.get_position_input("Enter position (e.g., A1) or Q to quit: ")
            if pos is None:
                return False
                
            if not self.game_engine.place_unit(unit_type, pos, player):
                print("Invalid placement! Try again.")
                continue
                
            self.game_engine.current_player = 3 - player
            
        return True

    def handle_battle_phase(self):
        """Handle the battle phase."""
        print("\n=== BATTLE PHASE ===")
        print("Commands:")
        print("  MOVE: Select your unit, then select destination")
        print("  ATTACK: Select your unit, then select enemy to attack")
        print("  HEAL: Select your Healer, then select friendly unit to heal")
        print("  Q: Quit game")
        
        while self.game_engine.state in [GameState.PLAYER_1_TURN, GameState.PLAYER_2_TURN]:
            self.print_board()
            player = self.game_engine.current_player
            print(f"\nPlayer {player}'s turn")
            
            # Select unit
            pos = self.get_position_input("Select your unit (e.g., A1) or Q to quit: ")
            if pos is None:
                return False
                
            if not self.game_engine.select_unit(pos):
                print("Invalid selection! Select one of your units.")
                continue
                
            unit = self.game_engine.selected_unit
            self.print_unit_info(unit)
            
            # Show valid actions
            if self.game_engine.valid_moves:
                print("\nValid moves:", ", ".join(f"{chr(65+x)}{y+1}" for x, y in self.game_engine.valid_moves))
            if self.game_engine.valid_attacks:
                print("Valid attacks:", ", ".join(f"{chr(65+x)}{y+1}" for x, y in self.game_engine.valid_attacks))
            if self.game_engine.valid_heals:
                print("Valid heals:", ", ".join(f"{chr(65+x)}{y+1}" for x, y in self.game_engine.valid_heals))
                
            # Get action
            action_pos = self.get_position_input("Select action position or Q to cancel: ")
            if action_pos is None:
                self.game_engine.selected_unit = None
                continue
                
            # Perform action
            if action_pos in self.game_engine.valid_moves:
                self.game_engine.move_unit(action_pos)
                print("Unit moved!")
            elif action_pos in self.game_engine.valid_attacks:
                self.game_engine.attack_unit(action_pos)
                print("Attack successful!")
            elif action_pos in self.game_engine.valid_heals:
                self.game_engine.heal_unit(action_pos)
                print("Healing successful!")
            else:
                print("Invalid action! Try again.")
                continue
                
        return True

    def run(self):
        """Run the game."""
        print("Welcome to Grid Conquer!")
        print("A turn-based strategy game where you battle to destroy the enemy's Crown.")
        
        if not self.handle_placement_phase():
            return
            
        if not self.handle_battle_phase():
            return
            
        # Game over
        self.print_board()
        print(f"\nGame Over! Player {self.game_engine.winner} wins!")

if __name__ == "__main__":
    game = TerminalGame()
    game.run() 