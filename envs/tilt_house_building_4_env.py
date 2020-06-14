from copy import deepcopy
import pybullet as pb
from helping_hands_rl_envs.envs.pybullet_env import PyBulletEnv
from helping_hands_rl_envs.envs.pybullet_tilt_env import PyBulletTiltEnv
from helping_hands_rl_envs.simulators.pybullet.robots.kuka_float_pick import KukaFloatPick
from helping_hands_rl_envs.simulators import constants
import numpy.random as npr
import numpy as np

def createTiltHouseBuilding4Env(simulator_base_env, config):
  class TiltHouseBuilding4Env(PyBulletTiltEnv):
    def __init__(self, config):
      if simulator_base_env is PyBulletEnv:
        super().__init__(config)
        self.block_scale_range = (0.6, 0.6)
        self.min_block_size = self.block_original_size * self.block_scale_range[0]
        self.max_block_size = self.block_original_size * self.block_scale_range[1]
      else:
        raise ValueError('Bad simulator base env specified.')
      self.simulator_base_env = simulator_base_env
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
      obj_dict = {
        constants.ROOF: 1,
        constants.BRICK: 1,
        constants.CUBE: 4
      }
      self.resetWithTiltAndObj(obj_dict)
      return self._getObservation()

    def _checkTermination(self):
      blocks = list(filter(lambda x: self.object_types[x] == constants.CUBE, self.objects))
      bricks = list(filter(lambda x: self.object_types[x] == constants.BRICK, self.objects))
      roofs = list(filter(lambda x: self.object_types[x] == constants.ROOF, self.objects))

      level1_blocks = list(filter(self._isObjOnGround, blocks))
      if len(level1_blocks) != 2:
        return False

      level2_blocks = list(set(blocks) - set(level1_blocks))
      return self._checkOnTop(level1_blocks[0], bricks[0]) and \
             self._checkOnTop(level1_blocks[1], bricks[0]) and \
             self._checkOnTop(bricks[0], level2_blocks[0]) and \
             self._checkOnTop(bricks[0], level2_blocks[1]) and \
             self._checkOnTop(level2_blocks[0], roofs[0]) and \
             self._checkOnTop(level2_blocks[1], roofs[0]) and \
             self._checkOriSimilar([bricks[0], roofs[0]]) and \
             self._checkInBetween(bricks[0], level1_blocks[0], level1_blocks[1]) and \
             self._checkInBetween(roofs[0], level2_blocks[0], level2_blocks[1]) and \
             self._checkInBetween(bricks[0], level2_blocks[0], level2_blocks[1])


  def _thunk():
    return TiltHouseBuilding4Env(config)

  return _thunk