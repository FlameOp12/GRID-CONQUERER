from typing import List, Tuple, Optional, Dict
from constants import GameState, UnitType, BOARD_SIZE, HEAL_AMOUNT, HEALER_HEAL_COST
from units import Unit

class GameEngine:
    def __init__(self):
        self.state = GameState.PLACEMENT_PHASE
        self.current_player = 1
        self.units: Dict[Tuple[int, int], Unit] = {}  # position -> Unit
        self.selected_unit: Optional[Unit] = None
        self.valid_moves: List[Tuple[int, int]] = []
        self.valid_attacks: List[Tuple[int, int]] = []
        self.valid_heals: List[Tuple[int, int]] = []

    def is_valid_placement(self, position: Tuple[int, int], player: int) -> bool:
        """Check if a position is valid for unit placement."""
        x, y = position
        
        # Check if position is within player's starting area
        if player == 1 and y >= 3:  # Bottom 3 rows for player 1
            return False
        if player == 2 and y < 5:   # Top 3 rows for player 2
            return False
            
        # Check if position is already occupied
        return position not in self.units

    def place_unit(self, unit_type: UnitType, position: Tuple[int, int], player: int) -> bool:
        """Place a unit on the board during the placement phase."""
        if self.state != GameState.PLACEMENT_PHASE:
            return False
            
        if not self.is_valid_placement(position, player):
            return False
            
        unit = Unit(unit_type, player, position)
        self.units[position] = unit
        return True

    def start_game(self) -> bool:
        """Start the game after placement phase."""
        if self.state != GameState.PLACEMENT_PHASE:
            return False
            
        # Check if both players have placed all their units
        player1_units = [u for u in self.units.values() if u.player == 1]
        player2_units = [u for u in self.units.values() if u.player == 2]
        
        if len(player1_units) != 5 or len(player2_units) != 5:
            return False
            
        self.state = GameState.PLAYER_1_TURN
        return True

    def select_unit(self, position: Tuple[int, int]) -> bool:
        """Select a unit for movement/attack/heal."""
        if self.state not in [GameState.PLAYER_1_TURN, GameState.PLAYER_2_TURN]:
            return False
            
        if position not in self.units:
            return False
            
        unit = self.units[position]
        if unit.player != self.current_player or not unit.alive:
            return False
            
        self.selected_unit = unit
        self.update_valid_actions()
        return True

    def update_valid_actions(self) -> None:
        """Update valid moves, attacks, and heals for the selected unit."""
        if not self.selected_unit:
            return
            
        # Get all occupied positions
        occupied_positions = list(self.units.keys())
        
        # Get enemy positions
        enemy_positions = [pos for pos, unit in self.units.items() 
                         if unit.player != self.current_player and unit.alive]
        
        # Get friendly positions
        friendly_positions = [pos for pos, unit in self.units.items() 
                            if unit.player == self.current_player and unit.alive]
        
        # Update valid actions
        self.valid_moves = self.selected_unit.get_valid_moves(BOARD_SIZE, occupied_positions)
        self.valid_attacks = self.selected_unit.get_valid_attacks(BOARD_SIZE, enemy_positions)
        self.valid_heals = self.selected_unit.get_valid_heals(BOARD_SIZE, friendly_positions)

    def move_unit(self, new_position: Tuple[int, int]) -> bool:
        """Move the selected unit to a new position."""
        if not self.selected_unit or new_position not in self.valid_moves:
            return False
            
        # Remove unit from old position and add to new position
        old_position = self.selected_unit.position
        del self.units[old_position]
        self.selected_unit.move(new_position)
        self.units[new_position] = self.selected_unit
        
        # Update valid actions
        self.update_valid_actions()
        return True

    def attack_unit(self, target_position: Tuple[int, int]) -> bool:
        """Attack a unit at the target position."""
        if not self.selected_unit or target_position not in self.valid_attacks:
            return False
            
        target_unit = self.units[target_position]
        damage = self.selected_unit.get_attack_damage()
        target_unit.take_damage(damage)
        
        # Remove dead unit
        if not target_unit.alive:
            del self.units[target_position]
            
        # End turn
        self.end_turn()
        return True

    def heal_unit(self, target_position: Tuple[int, int]) -> bool:
        """Heal a unit at the target position."""
        if not self.selected_unit or target_position not in self.valid_heals:
            return False
            
        target_unit = self.units[target_position]
        target_unit.heal(HEAL_AMOUNT)
        self.selected_unit.heal(HEALER_HEAL_COST)
        
        # Remove dead healer if it died from healing
        if not self.selected_unit.alive:
            del self.units[self.selected_unit.position]
            
        # End turn
        self.end_turn()
        return True

    def end_turn(self) -> None:
        """End the current player's turn."""
        self.selected_unit = None
        self.valid_moves = []
        self.valid_attacks = []
        self.valid_heals = []
        
        if self.state == GameState.PLAYER_1_TURN:
            self.state = GameState.PLAYER_2_TURN
            self.current_player = 2
        else:
            self.state = GameState.PLAYER_1_TURN
            self.current_player = 1
            
        self.check_game_over()

    def check_game_over(self) -> None:
        """Check if the game is over."""
        player1_crown = next((u for u in self.units.values() 
                            if u.player == 1 and u.unit_type == UnitType.CROWN), None)
        player2_crown = next((u for u in self.units.values() 
                            if u.player == 2 and u.unit_type == UnitType.CROWN), None)
                            
        if not player1_crown or not player1_crown.alive:
            self.state = GameState.GAME_OVER
            self.winner = 2
        elif not player2_crown or not player2_crown.alive:
            self.state = GameState.GAME_OVER
            self.winner = 1

    def get_unit_at(self, position: Tuple[int, int]) -> Optional[Unit]:
        """Get the unit at a specific position."""
        return self.units.get(position)

    def get_all_units(self) -> List[Unit]:
        """Get all units on the board."""
        return list(self.units.values()) 