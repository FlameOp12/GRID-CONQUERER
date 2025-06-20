from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from grid_conquer_env import GridConquerEnv

# Create the environment
env = GridConquerEnv()

# Wrap the environment
env = make_vec_env(lambda: env, n_envs=1)

# Define the DQN model
model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=1e-3,
    buffer_size=50000,
    learning_starts=1000,
    batch_size=32,
    target_update_interval=100,
    gamma=0.99,
)

# Train the model
model.learn(total_timesteps=100000)

# Save the model
model.save("grid_conquer_dqn")
