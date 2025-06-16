from dataclasses import dataclass
from typing import List, Tuple, Optional
from constants import UnitType, UNIT_STATS, ORTHOGONAL_DIRECTIONS, DIAGONAL_DIRECTIONS, ALL_DIRECTIONS

@dataclass
class Unit:
    unit_type: UnitType
    player: int  # 1 or 2
    position: Tuple[int, int]
    hp: int
    max_hp: int
    alive: bool = True

    def __init__(self, unit_type: UnitType, player: int, position: Tuple[int, int]):
        self.unit_type = unit_type
        self.player = player
        self.position = position
        stats = UNIT_STATS[unit_type]
        self.hp = stats['hp']
        self.max_hp = stats['hp']
        self.alive = True

    def get_valid_moves(self, board_size: int, occupied_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get all valid moves for this unit based on its type and current position."""
        if not self.alive or self.unit_type in [UnitType.WALL, UnitType.CROWN]:
            return []

        valid_moves = []
        x, y = self.position
        move_range = UNIT_STATS[self.unit_type]['move_range']

        # Determine allowed directions based on unit type
        if self.unit_type == UnitType.SOLDIER:
            directions = ORTHOGONAL_DIRECTIONS
        elif self.unit_type == UnitType.KNIGHT:
            directions = DIAGONAL_DIRECTIONS
        else:  # Healer
            directions = ALL_DIRECTIONS

        for dx, dy in directions:
            for i in range(1, move_range + 1):
                new_x, new_y = x + dx * i, y + dy * i
                
                # Check if position is within board bounds
                if not (0 <= new_x < board_size and 0 <= new_y < board_size):
                    break
                
                # Check if position is occupied
                if (new_x, new_y) in occupied_positions:
                    break
                
                valid_moves.append((new_x, new_y))

        return valid_moves

    def get_valid_attacks(self, board_size: int, enemy_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get all valid attack positions for this unit."""
        if not self.alive or self.unit_type in [UnitType.WALL, UnitType.CROWN, UnitType.HEALER]:
            return []

        valid_attacks = []
        x, y = self.position
        attack_range = UNIT_STATS[self.unit_type]['attack_range']

        # Determine allowed directions based on unit type
        if self.unit_type == UnitType.SOLDIER:
            directions = ORTHOGONAL_DIRECTIONS
        elif self.unit_type == UnitType.KNIGHT:
            directions = DIAGONAL_DIRECTIONS
        else:  # Healer
            return []  # Healers cannot attack

        for dx, dy in directions:
            for i in range(1, attack_range + 1):
                new_x, new_y = x + dx * i, y + dy * i
                
                # Check if position is within board bounds
                if not (0 <= new_x < board_size and 0 <= new_y < board_size):
                    break
                
                # Check if there's an enemy at this position
                if (new_x, new_y) in enemy_positions:
                    valid_attacks.append((new_x, new_y))
                    break

        return valid_attacks

    def get_valid_heals(self, board_size: int, friendly_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get all valid heal positions for this unit (Healer only)."""
        if not self.alive or self.unit_type != UnitType.HEALER:
            return []

        valid_heals = []
        x, y = self.position

        for dx, dy in ALL_DIRECTIONS:
            new_x, new_y = x + dx, y + dy
            
            # Check if position is within board bounds
            if not (0 <= new_x < board_size and 0 <= new_y < board_size):
                continue
            
            # Check if there's a friendly unit at this position
            if (new_x, new_y) in friendly_positions:
                valid_heals.append((new_x, new_y))

        return valid_heals

    def move(self, new_position: Tuple[int, int]) -> None:
        """Move the unit to a new position."""
        self.position = new_position

    def take_damage(self, damage: int) -> None:
        """Apply damage to the unit."""
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.alive = False

    def heal(self, amount: int) -> None:
        """Heal the unit."""
        if self.unit_type == UnitType.HEALER:
            self.hp = max(0, self.hp - amount)  # Healer takes damage when healing
            if self.hp == 0:
                self.alive = False
        else:
            self.hp = min(self.max_hp, self.hp + amount)

    def get_symbol(self) -> str:
        """Get the unit's display symbol."""
        return UNIT_STATS[self.unit_type]['symbol']

    def get_attack_damage(self) -> int:
        """Get the unit's attack damage."""
        return UNIT_STATS[self.unit_type]['attack'] 