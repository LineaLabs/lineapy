import numpy as np
import gym
from gym.wrappers import Monitor

env = gym.make("Pong-v0")
env = Monitor(env, "./video", force=True)
env.seed(42)
env.reset()


def frame_preprocessing(observation_frame):
    observation_frame = observation_frame[35:195]
    observation_frame = observation_frame[::2, ::2, 0]
    observation_frame[observation_frame == 144] = 0
    observation_frame[observation_frame == 109] = 0
    observation_frame[observation_frame != 0] = 1
    return observation_frame.astype(float)


rng = np.random.default_rng(seed=12288743)
D = 80 * 80
H = 200
model = {}
model["W1"] = rng.standard_normal(size=(H, D)) / np.sqrt(D)
model["W2"] = rng.standard_normal(size=H) / np.sqrt(H)


def policy_forward(x, model):
    h = np.dot(model["W1"], x)
    h[h < 0] = 0
    logit = np.dot(model["W2"], h)
    p = sigmoid(logit)
    return p, h


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def policy_backward(eph, epdlogp, model):
    dW2 = np.dot(eph.T, epdlogp).ravel()
    dh = np.outer(epdlogp, model["W2"])
    dh[eph <= 0] = 0
    dW1 = np.dot(dh.T, epx)
    return {"W1": dW1, "W2": dW2}


xs = []
hs = []
dlogps = []
drs = []
decay_rate = 0.99
grad_buffer = {k: np.zeros_like(v) for k, v in model.items()}
rmsprop_cache = {k: np.zeros_like(v) for k, v in model.items()}
gamma = 0.99


def discount_rewards(r, gamma):
    discounted_r = np.zeros_like(r)
    running_add = 0
    for t in reversed(range(0, r.size)):
        if r[t] != 0:
            running_add = 0
        running_add = running_add * gamma + r[t]
        discounted_r[t] = running_add
    return discounted_r


max_episodes = 3
batch_size = 3
learning_rate = 0.0001
render = False
observation = env.reset()
prev_x = None
running_reward = None
reward_sum = 0
episode_number = 0


def update_input(prev_x, cur_x, D):
    if prev_x is not None:
        x = cur_x - prev_x
    else:
        x = np.zeros(D)
    return x


while episode_number < max_episodes:
    if render:
        env.render()
    cur_x = frame_preprocessing(observation).ravel()
    x = update_input(prev_x, cur_x, D)
    prev_x = cur_x
    aprob, h = policy_forward(x, model)
    action = 2 if rng.uniform() < aprob else 3
    xs.append(x)
    hs.append(h)
    y = 1 if action == 2 else 0
    dlogps.append(y - aprob)
    observation, reward, done, info = env.step(action)
    reward_sum += reward
    drs.append(reward)
    if done:
        episode_number += 1
        epx = np.vstack(xs)
        eph = np.vstack(hs)
        epdlogp = np.vstack(dlogps)
        epr = np.vstack(drs)
        xs = []
        hs = []
        dlogps = []
        drs = []
        discounted_epr = discount_rewards(epr, gamma)
        discounted_epr -= np.mean(discounted_epr)
        discounted_epr /= np.std(discounted_epr)
        epdlogp *= discounted_epr
        grad = policy_backward(eph, epdlogp, model)
        for k in model:
            grad_buffer[k] += grad[k]
        if episode_number % batch_size == 0:
            for k, v in model.items():
                g = grad_buffer[k]
                rmsprop_cache[k] = (
                    decay_rate * rmsprop_cache[k] + (1 - decay_rate) * g ** 2
                )
                model[k] += learning_rate * g / (np.sqrt(rmsprop_cache[k]) + 1e-05)
                grad_buffer[k] = np.zeros_like(v)
        running_reward = (
            reward_sum
            if running_reward is None
            else running_reward * 0.99 + reward_sum * 0.01
        )
        print(
            "Resetting the Pong environment. Episode total reward: {} Running mean: {}".format(
                reward_sum, running_reward
            )
        )
        reward_sum = 0
        observation = env.reset()
        prev_x = None
    if reward != 0:
        print(
            "Episode {}: Game finished. Reward: {}...".format(episode_number, reward)
            + ("" if reward == -1 else " POSITIVE REWARD!")
        )
linea_artifact_value = model
