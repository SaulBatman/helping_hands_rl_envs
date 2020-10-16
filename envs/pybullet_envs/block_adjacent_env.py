import numpy as np

from helping_hands_rl_envs.envs.pybullet_envs.pybullet_env import PyBulletEnv
from helping_hands_rl_envs.simulators import constants

def createBlockAdjacentEnv(config):
  class BlockAdjacentEnv(PyBulletEnv):
    ''''''
    def __init__(self, config):
      super(BlockAdjacentEnv, self).__init__(config)

      self.random_orientation = config['random_orientation'] if 'random_orientation' in config else False
      self.num_obj = config['num_objects'] if 'num_objects' in config else 1
      self.reward_type = config['reward_type'] if 'reward_type' in config else 'sparse'

    def step(self, action):
      self.takeAction(action)
      self.wait(100)
      obs = self._getObservation(action)
      done = self._checkTermination()
      reward = 1.0 if done else 0.0

      if not done:
        done = self.current_episode_steps >= self.max_steps or not self.isSimValid()
      self.current_episode_steps += 1

      return obs, reward, done

    def reset(self):
      ''''''
      super(BlockAdjacentEnv, self).reset()
      self._generateShapes(constants.CUBE, self.num_obj, random_orientation=self.random_orientation)
      return self._getObservation()

    def _checkTermination(self):
      ''''''
      pos = np.array([o.getPosition() for o in self.objects])
      if (pos[:,2].max() - pos[:,2].min()) > 0.01: return False

      if np.allclose(pos[:,0], pos[0,0], atol=0.01):
        return np.abs(pos[:,1].max() - pos[:,1].min()) < self.max_block_size * 3.5
      elif np.allclose(pos[:,1], pos[0,1], atol=0.01):
        return np.abs(pos[:,0].max() - pos[:,0].min()) < self.max_block_size * 3.5
      else:
        return False

  def _thunk():
    return BlockAdjacentEnv(config)

  return _thunk