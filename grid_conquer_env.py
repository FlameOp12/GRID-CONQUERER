import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game_engine import GameEngine
from constants import GameState


class GridConquerEnv(gym.Env):
    def __init__(self):
        super(GridConquerEnv, self).__init__()
        self.game_engine = GameEngine()

        # Define the action space
        max_units = 10  # Adjust based on the number of units
        board_size = 8
        num_action_types = 3  # Move, attack, heal
        self.action_space = spaces.Discrete(max_units * (board_size ** 2) * num_action_types)

        # Define the observation space
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(8, 8, 3),  # 8x8 grid with features (type, player, health)
            dtype=np.float32,
        )

        self.np_random = None

    def reset(self, seed=None, options=None):
        """Reset the environment."""
        # Set the seed
        if seed is not None:
            self.seed(seed)

        # Initialize a new game state
        self.game_engine = GameEngine()
        self.game_engine.start_game()  # Ensure units are set up
        return self._get_state(), {}

    def step(self, action):
        """
        Perform an action in the environment.
        """
        action_tuple = self._decode_action(action)

        if action_tuple is None:
            reward, done = -10, False  # Penalty for invalid action
        else:
            reward, done = self._take_action(action_tuple)

        # Get the updated state
        next_state = self._get_state()

        # Gymnasium requires `terminated` and `truncated`. For simplicity, you can treat `truncated` as False.
        terminated = done
        truncated = False  # Adjust if you have specific truncation logic

        return next_state, reward, terminated, truncated, {}

    def render(self, mode="human"):
        """Render the environment (optional)."""
        pass  # Add rendering logic if needed

    def _get_state(self):
        """Return the current state of the game."""
        state = np.zeros((8, 8, 3), dtype=np.float32)
        for unit in self.game_engine.get_all_units():
            x, y = unit.position
            state[x, y] = [unit.unit_type.value, unit.player, unit.hp / unit.max_hp]
        return state

    def _decode_action(self, action):
        """
        Decode action ID into (unit, action_type, target_position).
        The action space encodes:
        - Unit index
        - Action type (move, attack, heal)
        - Target position
        """
        max_units = len(self.game_engine.get_all_units())
        board_size = 8
        num_action_types = 3

        # Validate the action
        if action >= max_units * (board_size ** 2) * num_action_types:
            return None

        # Decode the action
        unit_index = action // (board_size ** 2 * num_action_types)
        action_type_index = (action // (board_size ** 2)) % num_action_types
        position_id = action % (board_size ** 2)
        target_x, target_y = divmod(position_id, board_size)

        # Get the unit
        unit = list(self.game_engine.get_all_units())[unit_index] if unit_index < max_units else None

        if not unit:
            return None

        # Map action type index to action name
        action_type = ["move", "attack", "heal"][action_type_index]

        return unit, action_type, (target_x, target_y)

    def _take_action(self, action_tuple):
        """
        Execute the action and compute the reward.
        """
        unit, action_type, target = action_tuple

        if action_type == "move":
            success = self.game_engine.move_unit(target)
        elif action_type == "attack":
            success = self.game_engine.attack_unit(target)
        elif action_type == "heal":
            success = self.game_engine.heal_unit(target)
        else:
            success = False

        # Calculate the reward
        reward = 10 if success else -1  # Adjust based on game logic
        done = self.game_engine.state == GameState.GAME_OVER

        return reward, done

    def seed(self, seed=None):
        """Set the random seed for the environment."""
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        return [seed]
