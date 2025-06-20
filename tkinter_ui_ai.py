import tkinter as tk
from tkinter_ui import GridConquerUI
from game_engine import GameEngine
from constants import BOARD_SIZE, UnitType, GameState
import numpy as np
import random

class RLAgent:
    """
    Reinforcement Learning Agent for Grid Conquer.
    This class is ready for Q-learning, DQN, or PPO integration.
    For now, it uses a strong heuristic/minimax placeholder.
    """
    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine

    def choose_action(self):
        # Placeholder: Greedy attack, else move toward enemy crown
        valid_actions = self.get_all_valid_actions()
        # Prioritize attacks
        for (unit, action_type, target) in valid_actions:
            if action_type == 'attack':
                return (unit, action_type, target)
        # Otherwise, move toward enemy crown
        for (unit, action_type, target) in valid_actions:
            if action_type == 'move':
                return (unit, action_type, target)
        # Otherwise, heal if possible
        for (unit, action_type, target) in valid_actions:
            if action_type == 'heal':
                return (unit, action_type, target)
        return None

    def get_all_valid_actions(self):
        actions = []
        for unit in self.game_engine.get_all_units():
            if unit.player == 2 and unit.alive:
                self.game_engine.selected_unit = unit
                self.game_engine.update_valid_actions()
                for move in self.game_engine.valid_moves:
                    actions.append((unit, 'move', move))
                for attack in self.game_engine.valid_attacks:
                    actions.append((unit, 'attack', attack))
                for heal in self.game_engine.valid_heals:
                    actions.append((unit, 'heal', heal))
        self.game_engine.selected_unit = None
        self.game_engine.update_valid_actions()
        return actions

class GridConquerUIAI(GridConquerUI):
    def __init__(self):
        super().__init__()
        self.ai_agent = RLAgent(self.game_engine)
        self.is_ai_turn = False
        self.root.after(100, self.check_ai_turn)

    def check_ai_turn(self):
        if self.game_engine.state == GameState.PLAYER_2_TURN:
            self.is_ai_turn = True
            self.root.after(500, self.ai_move)
        else:
            self.is_ai_turn = False
        self.root.after(100, self.check_ai_turn)

    def ai_move(self):
        if self.game_engine.state != GameState.PLAYER_2_TURN:
            return
        action = self.ai_agent.choose_action()
        if action is None:
            self.game_engine.end_turn()
            self.update_display()
            return
        unit, action_type, target = action
        self.game_engine.selected_unit = unit
        self.game_engine.update_valid_actions()
        if action_type == 'attack':
            self.game_engine.attack_unit(target)
        elif action_type == 'move':
            self.game_engine.move_unit(target)
            self.game_engine.end_turn()
        elif action_type == 'heal':
            self.game_engine.heal_unit(target)
        self.update_display()

if __name__ == "__main__":
    game = GridConquerUIAI()
    game.run() 