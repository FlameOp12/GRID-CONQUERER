import pygame
import pygame.freetype
from typing import Tuple, Optional
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    TILE_SIZE, BOARD_SIZE,
    PLAYER1_COLOR, PLAYER2_COLOR,
    GRID_BG_COLOR, GRID_LINE_COLOR,
    SELECTED_COLOR, VALID_MOVE_COLOR, VALID_ATTACK_COLOR,
    VALID_HEAL_COLOR, GameState, UnitType
)
from game_engine import GameEngine
from units import Unit

class GameUI:
    def __init__(self):
        pygame.init()
        pygame.freetype.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        
        self.font = pygame.freetype.SysFont('Arial', 24)
        self.unit_font = pygame.freetype.SysFont('Arial', 32)
        
        self.game_engine = GameEngine()
        self.running = True
        self.selected_position: Optional[Tuple[int, int]] = None

    def draw_grid(self):
        """Draw the game grid."""
        # Fill background
        self.screen.fill(GRID_BG_COLOR)
        
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen,
                GRID_LINE_COLOR,
                (i * TILE_SIZE, 0),
                (i * TILE_SIZE, WINDOW_HEIGHT)
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen,
                GRID_LINE_COLOR,
                (0, i * TILE_SIZE),
                (WINDOW_WIDTH, i * TILE_SIZE)
            )

    def draw_unit(self, unit: Unit):
        """Draw a unit on the board."""
        x, y = unit.position
        center_x = x * TILE_SIZE + TILE_SIZE // 2
        center_y = y * TILE_SIZE + TILE_SIZE // 2
        
        # Draw unit symbol
        color = PLAYER1_COLOR if unit.player == 1 else PLAYER2_COLOR
        self.unit_font.render_to(
            self.screen,
            (center_x - 10, center_y - 15),
            unit.get_symbol(),
            color
        )
        
        # Draw health bar
        health_width = int((unit.hp / unit.max_hp) * (TILE_SIZE - 10))
        health_x = x * TILE_SIZE + 5
        health_y = y * TILE_SIZE + 5
        
        # Background (gray)
        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (health_x, health_y, TILE_SIZE - 10, 5)
        )
        
        # Health (green)
        pygame.draw.rect(
            self.screen,
            (0, 255, 0),
            (health_x, health_y, health_width, 5)
        )

    def draw_valid_actions(self):
        """Draw valid moves, attacks, and heals."""
        if not self.game_engine.selected_unit:
            return
            
        # Draw valid moves
        for pos in self.game_engine.valid_moves:
            x, y = pos
            pygame.draw.rect(
                self.screen,
                VALID_MOVE_COLOR,
                (x * TILE_SIZE + 2, y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4),
                2
            )
            
        # Draw valid attacks
        for pos in self.game_engine.valid_attacks:
            x, y = pos
            pygame.draw.rect(
                self.screen,
                VALID_ATTACK_COLOR,
                (x * TILE_SIZE + 2, y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4),
                2
            )
            
        # Draw valid heals
        for pos in self.game_engine.valid_heals:
            x, y = pos
            pygame.draw.rect(
                self.screen,
                VALID_HEAL_COLOR,
                (x * TILE_SIZE + 2, y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4),
                2
            )

    def draw_game_state(self):
        """Draw the current game state."""
        # Draw grid
        self.draw_grid()
        
        # Draw units
        for unit in self.game_engine.get_all_units():
            if unit.alive:
                self.draw_unit(unit)
                
        # Draw valid actions
        self.draw_valid_actions()
        
        # Draw game state text
        state_text = ""
        if self.game_engine.state == GameState.PLACEMENT_PHASE:
            state_text = f"Player {self.game_engine.current_player}'s Turn - Place Units"
        elif self.game_engine.state in [GameState.PLAYER_1_TURN, GameState.PLAYER_2_TURN]:
            state_text = f"Player {self.game_engine.current_player}'s Turn"
        elif self.game_engine.state == GameState.GAME_OVER:
            state_text = f"Game Over - Player {self.game_engine.winner} Wins!"
            
        self.font.render_to(
            self.screen,
            (10, WINDOW_HEIGHT - 30),
            state_text,
            (0, 0, 0)
        )

    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click events."""
        x, y = pos
        board_x = x // TILE_SIZE
        board_y = y // TILE_SIZE
        
        if not (0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE):
            return
            
        position = (board_x, board_y)
        
        if self.game_engine.state == GameState.PLACEMENT_PHASE:
            # Get the current player's units
            player_units = [u for u in self.game_engine.get_all_units() if u.player == self.game_engine.current_player]
            
            # Determine which unit to place based on count
            unit_type = None
            if len(player_units) == 0:
                unit_type = UnitType.SOLDIER
            elif len(player_units) == 1:
                unit_type = UnitType.KNIGHT
            elif len(player_units) == 2:
                unit_type = UnitType.HEALER
            elif len(player_units) == 3:
                unit_type = UnitType.WALL
            elif len(player_units) == 4:
                unit_type = UnitType.CROWN
            else:
                # All units placed, start the game
                self.game_engine.start_game()
                return
                
            # Place the unit
            if self.game_engine.place_unit(unit_type, position, self.game_engine.current_player):
                # Switch player after successful placement
                self.game_engine.current_player = 3 - self.game_engine.current_player
                
        elif self.game_engine.state in [GameState.PLAYER_1_TURN, GameState.PLAYER_2_TURN]:
            # Handle unit selection and actions
            if not self.game_engine.selected_unit:
                self.game_engine.select_unit(position)
            else:
                # Try to perform an action
                if position in self.game_engine.valid_moves:
                    self.game_engine.move_unit(position)
                elif position in self.game_engine.valid_attacks:
                    self.game_engine.attack_unit(position)
                elif position in self.game_engine.valid_heals:
                    self.game_engine.heal_unit(position)
                else:
                    # Deselect unit if clicking elsewhere
                    self.game_engine.selected_unit = None
                    self.game_engine.valid_moves = []
                    self.game_engine.valid_attacks = []
                    self.game_engine.valid_heals = []

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                        
            # Draw everything
            self.draw_game_state()
            pygame.display.flip()
            
        pygame.quit() 