import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from typing import Tuple, Optional
from constants import (
    BOARD_SIZE, PLAYER1_COLOR, PLAYER2_COLOR,
    GameState, UnitType, HEAL_AMOUNT, HEALER_HEAL_COST
)
from game_engine import GameEngine

class DraggableUnit(tk.Label):
    def __init__(self, parent, image, unit_type, player, **kwargs):
        super().__init__(parent, image=image, **kwargs)
        self.unit_type = unit_type
        self.player = player
        self.bind('<Button-1>', self.start_drag)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<ButtonRelease-1>', self.stop_drag)
        
    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def drag(self, event):
        x = self.winfo_x() - self._drag_start_x + event.x
        y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=x, y=y)
        
    def stop_drag(self, event):
        # Get the widget under the cursor
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if isinstance(widget, ttk.Button) and hasattr(widget, 'grid_info'):
            # Get grid coordinates
            grid_info = widget.grid_info()
            if grid_info:
                x, y = grid_info['column'], grid_info['row']
                # Trigger placement
                self.master.handle_unit_placement(self.unit_type, (x, y))
        # Return to original position
        self.place_forget()

class GridConquerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grid Conquer")
        self.root.resizable(False, False)
        
        # Load images
        self.images = {}
        self.load_images()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create game board
        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10)
        
        # Create troop selection panel
        self.troop_frame = ttk.Frame(self.main_frame)
        self.troop_frame.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create info panel
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.grid(row=0, column=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize game engine
        self.game_engine = GameEngine()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Board.TButton', padding=5)
        self.style.configure('Info.TLabel', padding=5)
        self.style.configure('ValidMove.TButton', background='green')
        self.style.configure('ValidAttack.TButton', background='red')
        self.style.configure('ValidHeal.TButton', background='blue')
        self.style.configure('InvalidHeal.TButton', background='gray')
        
        # Configure HP bar style
        self.style.layout('HP.TProgressbar', 
            [('Horizontal.Progressbar.trough',
                {'children': [('Horizontal.Progressbar.pbar',
                    {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'})])
        self.style.configure('HP.TProgressbar',
            troughcolor='#E0E0E0',
            background='#4CAF50',
            thickness=15,
            borderwidth=0)
        self.style.configure('HP.TLabel',
            font=('Arial', 8),
            padding=0)
        
        # Create board buttons
        self.board_buttons = []
        self.create_board()
        
        # Create troop selection panel
        self.create_troop_panel()
        
        # Create info labels
        self.create_info_panel()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_images(self):
        """Load all game images."""
        image_files = {
            'grass': 'grass.png',
            'soldier_1': 'soldier-1.png',
            'soldier_2': 'soldier-2.png',
            'knight_1': 'knight-1.png',
            'knight_2': 'knight-2.png',
            'healer_1': 'healer-1.png',
            'healer_2': 'healer-2.png',
            'wall_1': 'wall-1.png',
            'wall_2': 'wall-2.png',
            'crown_1': 'crown-1.png',
            'crown_2': 'crown-2.png'
        }
        
        for key, filename in image_files.items():
            try:
                image = Image.open(os.path.join('assets', filename))
                image = image.resize((60, 60), Image.Resampling.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
                
    def create_board(self):
        """Create the game board with buttons."""
        for y in range(BOARD_SIZE):
            row = []
            for x in range(BOARD_SIZE):
                # Create frame for button and HP bar
                cell_frame = ttk.Frame(self.board_frame)
                cell_frame.grid(row=y, column=x, padx=1, pady=1)
                
                # Create button
                btn = ttk.Button(
                    cell_frame,
                    style='Board.TButton',
                    width=8,
                    command=lambda x=x, y=y: self.handle_click(x, y)
                )
                btn.grid(row=0, column=0)
                
                # Create HP bar frame
                hp_frame = ttk.Frame(cell_frame)
                hp_frame.grid(row=1, column=0, pady=1)
                
                # Create HP bar
                hp_bar = ttk.Progressbar(
                    hp_frame,
                    length=60,
                    mode='determinate',
                    style='HP.TProgressbar'
                )
                hp_bar.pack(side=tk.LEFT, padx=1)
                
                # Create HP text label
                hp_text = ttk.Label(
                    hp_frame,
                    text="",
                    style='HP.TLabel',
                    width=8
                )
                hp_text.pack(side=tk.LEFT, padx=1)
                
                row.append((btn, hp_bar, hp_text))
            self.board_buttons.append(row)
            
    def create_troop_panel(self):
        """Create the troop selection panel."""
        # Title
        ttk.Label(
            self.troop_frame,
            text="Available Units",
            style='Info.TLabel'
        ).grid(row=0, column=0, pady=10)
        
        # Create draggable units
        self.troop_units = []
        row = 1
        
        # Add units based on current player
        unit_types = [
            (UnitType.SOLDIER, "Soldier"),
            (UnitType.KNIGHT, "Knight"),
            (UnitType.HEALER, "Healer"),
            (UnitType.WALL, "Wall"),
            (UnitType.CROWN, "Crown")
        ]
        
        for unit_type, name in unit_types:
            # Create frame for unit
            unit_frame = ttk.Frame(self.troop_frame)
            unit_frame.grid(row=row, column=0, pady=5)
            
            # Create draggable unit
            image_key = f"{unit_type.name.lower()}_{self.game_engine.current_player}"
            unit = DraggableUnit(
                unit_frame,
                self.images[image_key],
                unit_type,
                self.game_engine.current_player,
                relief=tk.RAISED,
                borderwidth=2
            )
            unit.pack(side=tk.LEFT, padx=5)
            
            # Add unit name
            ttk.Label(
                unit_frame,
                text=name,
                style='Info.TLabel'
            ).pack(side=tk.LEFT, padx=5)
            
            self.troop_units.append(unit)
            row += 1
            
    def create_info_panel(self):
        """Create the information panel."""
        # Game state label
        self.state_label = ttk.Label(
            self.info_frame,
            text="Placement Phase - Player 1's Turn",
            style='Info.TLabel'
        )
        self.state_label.grid(row=0, column=0, pady=10)
        
        # Selected unit info
        self.unit_info = ttk.Label(
            self.info_frame,
            text="No unit selected",
            style='Info.TLabel'
        )
        self.unit_info.grid(row=1, column=0, pady=10)
        
        # Valid moves info
        self.moves_info = ttk.Label(
            self.info_frame,
            text="",
            style='Info.TLabel'
        )
        self.moves_info.grid(row=2, column=0, pady=10)
        
    def update_board(self):
        """Update the game board display."""
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                btn, hp_bar, hp_text = self.board_buttons[y][x]
                unit = self.game_engine.get_unit_at((x, y))
                
                if unit and unit.alive:
                    # Set unit image based on type and player
                    image_key = f"{unit.unit_type.name.lower()}_{unit.player}"
                    btn.configure(image=self.images.get(image_key, ''))
                    
                    # Update HP bar and text
                    hp_percentage = (unit.hp / unit.max_hp) * 100
                    hp_bar['value'] = hp_percentage
                    
                    # Update HP text
                    hp_text.configure(text=f"{unit.hp}/{unit.max_hp}")
                    
                    # Show HP elements
                    hp_bar.master.grid()
                else:
                    # Set grass background
                    btn.configure(image=self.images['grass'])
                    
                    # Hide HP elements
                    hp_bar.master.grid_remove()
                    
                # Update button style based on valid actions
                if self.game_engine.selected_unit:
                    if (x, y) in self.game_engine.valid_moves:
                        btn.configure(style='ValidMove.TButton')
                    elif (x, y) in self.game_engine.valid_attacks:
                        btn.configure(style='ValidAttack.TButton')
                    elif (x, y) in self.game_engine.valid_heals:
                        # Check if target can be healed
                        target_unit = self.game_engine.get_unit_at((x, y))
                        if (target_unit and 
                            target_unit.hp < target_unit.max_hp and 
                            self.game_engine.selected_unit.hp > HEALER_HEAL_COST):
                            btn.configure(style='ValidHeal.TButton')
                        else:
                            btn.configure(style='InvalidHeal.TButton')
                    else:
                        btn.configure(style='Board.TButton')
                else:
                    btn.configure(style='Board.TButton')
                    
    def update_info_panel(self):
        """Update the information panel."""
        # Update game state
        state_text = ""
        if self.game_engine.state == GameState.PLACEMENT_PHASE:
            state_text = f"Placement Phase - Player {self.game_engine.current_player}'s Turn"
        elif self.game_engine.state in [GameState.PLAYER_1_TURN, GameState.PLAYER_2_TURN]:
            state_text = f"Player {self.game_engine.current_player}'s Turn"
        elif self.game_engine.state == GameState.GAME_OVER:
            state_text = f"Game Over - Player {self.game_engine.winner} Wins!"
        self.state_label.configure(text=state_text)
        
        # Update unit info
        if self.game_engine.selected_unit:
            unit = self.game_engine.selected_unit
            info_text = f"Selected: {unit.unit_type.name}\nHP: {unit.hp}/{unit.max_hp}"
            
            # Add healer-specific info
            if unit.unit_type == UnitType.HEALER:
                info_text += f"\nHeal Cost: {HEALER_HEAL_COST} HP"
                if unit.hp <= HEALER_HEAL_COST:
                    info_text += "\nCannot heal - Not enough HP!"
                    
            self.unit_info.configure(text=info_text)
            
            # Update valid actions
            moves_text = ""
            if self.game_engine.valid_moves:
                moves_text += "Valid moves: " + ", ".join(f"{chr(65+x)}{y+1}" for x, y in self.game_engine.valid_moves) + "\n"
            if self.game_engine.valid_attacks:
                moves_text += "Valid attacks: " + ", ".join(f"{chr(65+x)}{y+1}" for x, y in self.game_engine.valid_attacks) + "\n"
            if self.game_engine.valid_heals:
                moves_text += "Valid heals: " + ", ".join(f"{chr(65+x)}{y+1}" for x, y in self.game_engine.valid_heals)
                if unit.unit_type == UnitType.HEALER:
                    moves_text += "\n(Only units with less than full HP can be healed)"
            self.moves_info.configure(text=moves_text)
        else:
            self.unit_info.configure(text="No unit selected")
            self.moves_info.configure(text="")
            
    def handle_click(self, x: int, y: int):
        """Handle board button clicks."""
        position = (x, y)
        
        if self.game_engine.state == GameState.PLACEMENT_PHASE:
            # Get the current player's units
            player_units = [u for u in self.game_engine.get_all_units() if u.player == self.game_engine.current_player]
            
            # Determine which unit to place
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
                self.update_display()
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
                    self.game_engine.end_turn()  # End turn after move
                elif position in self.game_engine.valid_attacks:
                    self.game_engine.attack_unit(position)
                    self.game_engine.end_turn()  # End turn after attack
                elif position in self.game_engine.valid_heals:
                    self.game_engine.heal_unit(position)
                    self.game_engine.end_turn()  # End turn after heal
                else:
                    # Deselect unit if clicking elsewhere
                    self.game_engine.selected_unit = None
                    self.game_engine.valid_moves = []
                    self.game_engine.valid_attacks = []
                    self.game_engine.valid_heals = []
                    
        self.update_display()
        
    def handle_unit_placement(self, unit_type: UnitType, position: Tuple[int, int]):
        """Handle unit placement from drag and drop."""
        if self.game_engine.state == GameState.PLACEMENT_PHASE:
            if self.game_engine.place_unit(unit_type, position, self.game_engine.current_player):
                # Switch player after successful placement
                self.game_engine.current_player = 3 - self.game_engine.current_player
                # Update troop panel for new player
                self.update_troop_panel()
                self.update_display()
                
    def update_troop_panel(self):
        """Update the troop panel for the current player."""
        # Clear existing units
        for unit in self.troop_units:
            unit.destroy()
        self.troop_units.clear()
        
        # Recreate troop panel
        self.create_troop_panel()
        
    def update_display(self):
        """Update the entire game display."""
        self.update_board()
        self.update_info_panel()
        
        # If game has started, hide troop panel
        if self.game_engine.state != GameState.PLACEMENT_PHASE:
            self.troop_frame.grid_remove()
        else:
            self.troop_frame.grid()
            
    def on_closing(self):
        """Handle window closing."""
        self.root.destroy()
        
    def run(self):
        """Start the game."""
        self.update_display()
        self.root.mainloop()

if __name__ == "__main__":
    game = GridConquerUI()
    game.run() 