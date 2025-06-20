from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from grid_conquer_env import GridConquerEnv

# Create the environment with rendering enabled
env = make_vec_env(lambda: GridConquerEnv(render_mode="human"), n_envs=1)

# Load the trained model
model = DQN.load("grid_conquer_dqn")

# Play a single episode
obs = env.reset()
done = False
total_reward = 0

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, rewards, dones, infos = env.step(action)
    done = dones[0]
    total_reward += rewards[0]
    env.render()  # Call render for visualization

print(f"Total reward: {total_reward}")
