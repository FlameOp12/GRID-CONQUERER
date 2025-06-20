import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import numpy as np
from typing import Tuple
from stable_baselines3 import DQN
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
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if isinstance(widget, ttk.Button) and hasattr(widget, 'grid_info'):
            grid_info = widget.grid_info()
            if grid_info:
                x, y = grid_info['column'], grid_info['row']
                self.master.handle_unit_placement(self.unit_type, (x, y))
        self.place_forget()


class GridConquerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grid Conquer")
        self.root.resizable(False, False)
        self.root.configure(bg="#e3f2fd")

        self.game_engine = GameEngine()
        self.model = DQN.load("grid_conquer_dqn.zip")  # Load pre-trained model

        # GUI Layout
        self.board_buttons = []
        self.images = {}
        self.cell_size = 80
        self.load_images()
        self.create_gui()

    def load_images(self):
        """Load all game images and resize them."""
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
                image = image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading image {filename}: {e}")

    def create_gui(self):
        """Set up the main GUI layout."""
        # Main Frames
        self.main_frame = tk.Frame(self.root, bg="#e3f2fd")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.board_frame = tk.Frame(self.main_frame, bg="#90caf9", bd=4, relief=tk.RIDGE)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10)

        self.info_frame = tk.Frame(self.main_frame, bg="#f5f5f5", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.info_frame.grid(row=0, column=1, padx=10, pady=10)

        # Create Board
        for y in range(BOARD_SIZE):
            row = []
            for x in range(BOARD_SIZE):
                btn = tk.Button(
                    self.board_frame,
                    bg="#e3f2fd",
                    command=lambda x=x, y=y: self.handle_click(x, y)
                )
                btn.grid(row=y, column=x, padx=2, pady=2, sticky="nsew")
                row.append(btn)
            self.board_buttons.append(row)

        # Game Info
        self.state_label = tk.Label(self.info_frame, text="Game State: Starting", font=("Arial", 14))
        self.state_label.pack(pady=10)

    def update_display(self):
        """Refresh the game board and info."""
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                unit = self.game_engine.get_unit_at((x, y))
                btn = self.board_buttons[y][x]
                if unit:
                    key = f"{unit.unit_type.name.lower()}_{unit.player}"
                    btn.config(image=self.images.get(key, ""))
                else:
                    btn.config(image="", bg="#e3f2fd")

        state_text = f"Player {self.game_engine.current_player}'s Turn"
        if self.game_engine.state == GameState.GAME_OVER:
            state_text = f"Game Over! Player {self.game_engine.winner} wins!"
        self.state_label.config(text=state_text)

    def handle_click(self, x: int, y: int):
        """Handle human player clicks."""
        if self.game_engine.state in [GameState.PLAYER_1_TURN, GameState.PLAYER_2_TURN]:
            self.game_engine.handle_click(x, y)  # Implement logic for human actions
            self.update_display()

            if self.game_engine.state == GameState.PLAYER_2_TURN:
                self.ai_take_turn()

    def ai_take_turn(self):
        """AI performs its turn."""
        if self.game_engine.state == GameState.PLAYER_2_TURN:
            obs = self.game_engine.get_state()
            action, _ = self.model.predict(obs, deterministic=True)
            x, y = self.decode_action(action)  # Implement `decode_action` to map action IDs to coordinates
            self.game_engine.select_unit((x, y))  # Select unit and perform action
            self.update_display()

    def decode_action(self, action: int) -> Tuple[int, int]:
        """Decode the action into (x, y) coordinates."""
        return action % BOARD_SIZE, action // BOARD_SIZE  # Adjust as per your encoding logic

    def run(self):
        """Start the GUI."""
        self.update_display()
        self.root.mainloop()


if __name__ == "__main__":
    game = GridConquerUI()
    game.run()
