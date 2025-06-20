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
        self.root.configure(bg="#e3f2fd")
        
        # Get screen size and set window size to 80% of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Estimate side panel width (troop + info) and padding
        side_panel_width = 400  # adjust if your panels are wider
        padding = 80  # total horizontal padding
        vertical_padding = 80  # total vertical padding
        
        # Calculate available width and height for the board
        available_width = window_width - side_panel_width - padding
        available_height = window_height - vertical_padding
        
        # Use the minimum for a square board
        board_area = min(available_width, available_height)
        self.cell_size = int(board_area // BOARD_SIZE)
        self.btn_size = self.cell_size - 8
        self.hp_bar_width = self.btn_size
        self.hp_bar_height = max(18, self.cell_size // 6)
        
        # Load images
        self.images = {}
        self.load_images()
        
        # Create main frame with padding and modern look
        self.main_frame = tk.Frame(self.root, bg="#e3f2fd", padx=20, pady=20)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create game board
        self.board_frame = tk.Frame(self.main_frame, bg="#90caf9", bd=4, relief=tk.RIDGE)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10)
        
        # Create troop selection panel with card look
        self.troop_frame = tk.Frame(self.main_frame, bg="#fffde7", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.troop_frame.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create info panel with card look
        self.info_frame = tk.Frame(self.main_frame, bg="#f5f5f5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.info_frame.grid(row=0, column=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize game engine
        self.game_engine = GameEngine()
        
        # Create board buttons
        self.board_buttons = []
        self.create_board()
        
        # Create troop selection panel
        self.create_troop_panel()
        
        # Create info labels
        self.create_info_panel()
        
        # Style configuration (for highlights)
        self.style = ttk.Style()
        self.style.configure('Board.TButton', padding=5)
        self.style.configure('Info.TLabel', padding=5, font=("Segoe UI", 12))
        self.style.configure('ValidMove.TButton', background='#a5d6a7')
        self.style.configure('ValidAttack.TButton', background='#ef9a9a')
        self.style.configure('ValidHeal.TButton', background='#b3e5fc')
        self.style.configure('InvalidHeal.TButton', background='#eeeeee')
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_images(self):
        """Load all game images and resize them to the current button size."""
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
                image = image.resize((self.btn_size, self.btn_size), Image.Resampling.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
                
    def create_board(self):
        """Create the game board with buttons and modern appearance."""
        self.tile_colors = ["#e3f2fd", "#bbdefb"]  # Soft blue and lighter blue
        for y in range(BOARD_SIZE):
            row = []
            for x in range(BOARD_SIZE):
                # Create frame for button and HP bar
                cell_frame = tk.Frame(self.board_frame, bg=self.tile_colors[(x + y) % 2], bd=0, highlightthickness=0)
                cell_frame.grid(row=y, column=x, padx=3, pady=3, sticky="nsew")
                cell_frame.grid_propagate(False)
                cell_frame.config(width=self.cell_size, height=self.cell_size + self.hp_bar_height)
                
                # Create button with rounded corners effect
                btn = tk.Button(
                    cell_frame,
                    relief=tk.FLAT,
                    bg=self.tile_colors[(x + y) % 2],
                    activebackground="#90caf9",
                    font=("Segoe UI", max(14, self.btn_size // 4), "bold"),
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda x=x, y=y: self.handle_click(x, y)
                )
                btn.place(x=4, y=4, width=self.btn_size, height=self.btn_size)
                btn.bind('<Enter>', lambda e, b=btn: b.config(bg="#b3e5fc"))
                btn.bind('<Leave>', lambda e, b=btn, c=self.tile_colors[(x + y) % 2]: b.config(bg=c))
                
                # Create HP bar canvas (for custom color and text)
                hp_canvas = tk.Canvas(cell_frame, width=self.hp_bar_width, height=self.hp_bar_height, bg='#f5f5f5', highlightthickness=0, bd=0)
                hp_canvas.place(x=4, y=self.btn_size + 6)
                
                row.append((btn, hp_canvas, cell_frame))
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
                btn, hp_canvas, cell_frame = self.board_buttons[y][x]
                unit = self.game_engine.get_unit_at((x, y))
                
                # Set cell background
                cell_frame.config(bg=self.tile_colors[(x + y) % 2])
                btn.config(bg=self.tile_colors[(x + y) % 2], activebackground="#90caf9")
                
                if unit and unit.alive:
                    # Set unit image based on type and player
                    image_key = f"{unit.unit_type.name.lower()}_{unit.player}"
                    btn.config(image=self.images.get(image_key, ''), text="", relief=tk.FLAT)
                    
                    # Draw yellow HP bar with value inside
                    hp_canvas.delete("all")
                    hp_percentage = (unit.hp / unit.max_hp)
                    bar_length = int(self.hp_bar_width * hp_percentage)
                    r = max(9, self.hp_bar_height // 2)
                    if bar_length > 0:
                        hp_canvas.create_rectangle(0, 0, bar_length, self.hp_bar_height, fill='#FFD600', outline='', width=0)
                        hp_canvas.create_oval(0, 0, r*2, self.hp_bar_height, fill='#FFD600', outline='')
                        if bar_length > r:
                            hp_canvas.create_oval(bar_length-r*2, 0, bar_length, self.hp_bar_height, fill='#FFD600', outline='')
                    hp_text = f"{unit.hp}/{unit.max_hp}"
                    hp_canvas.create_text(self.hp_bar_width//2, self.hp_bar_height//2, text=hp_text, fill='black', font=('Segoe UI', max(9, self.hp_bar_height//2), 'bold'))
                    hp_canvas.grid()
                else:
                    btn.config(image='', text="", relief=tk.FLAT)
                    hp_canvas.delete("all")
                    hp_canvas.grid_remove()
                
                # Update button style based on valid actions
                if self.game_engine.selected_unit:
                    if (x, y) in self.game_engine.valid_moves:
                        btn.config(bg="#a5d6a7", activebackground="#81c784")
                    elif (x, y) in self.game_engine.valid_attacks:
                        btn.config(bg="#ef9a9a", activebackground="#e57373")
                    elif (x, y) in self.game_engine.valid_heals:
                        # Check if target can be healed
                        target_unit = self.game_engine.get_unit_at((x, y))
                        if (target_unit and 
                            target_unit.hp < target_unit.max_hp and 
                            self.game_engine.selected_unit.hp > HEALER_HEAL_COST):
                            btn.config(bg="#b3e5fc", activebackground="#4fc3f7")
                        else:
                            btn.config(bg="#eeeeee", activebackground="#eeeeee")
                    else:
                        btn.config(bg=self.tile_colors[(x + y) % 2], activebackground="#90caf9")
                else:
                    btn.config(bg=self.tile_colors[(x + y) % 2], activebackground="#90caf9")
                    
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
                    self.game_engine.attack_unit(position)  # end_turn is called inside attack_unit
                elif position in self.game_engine.valid_heals:
                    self.game_engine.heal_unit(position)    # end_turn is called inside heal_unit
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
        
    def show_win_popup(self, winner):
        popup = tk.Toplevel(self.root)
        popup.title("Game Over!")
        popup.geometry("350x180")
        popup.configure(bg="#f5f5f5")
        popup.transient(self.root)
        popup.grab_set()
        
        msg = f"Player {winner} Wins!"
        label = tk.Label(popup, text=msg, font=("Arial", 24, "bold"), fg="#388e3c", bg="#f5f5f5")
        label.pack(pady=30)
        
        btn = tk.Button(popup, text="OK", font=("Arial", 14), bg="#4caf50", fg="white", relief=tk.RAISED, command=popup.destroy)
        btn.pack(pady=10)
        
        # Center the popup
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def update_display(self):
        """Update the entire game display."""
        self.update_board()
        self.update_info_panel()
        
        # If game has started, hide troop panel
        if self.game_engine.state != GameState.PLACEMENT_PHASE:
            self.troop_frame.grid_remove()
        else:
            self.troop_frame.grid()
        
        # Show win popup if game is over
        if self.game_engine.state == GameState.GAME_OVER:
            self.show_win_popup(self.game_engine.winner)
            
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