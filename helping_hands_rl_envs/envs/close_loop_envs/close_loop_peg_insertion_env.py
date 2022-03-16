import pybullet as pb
import numpy as np

from helping_hands_rl_envs.pybullet.utils import constants
from helping_hands_rl_envs.envs.close_loop_envs.close_loop_env import CloseLoopEnv
from helping_hands_rl_envs.pybullet.utils import transformations
import helping_hands_rl_envs.pybullet.utils.object_generation as pb_obj_generation
#from helping_hands_rl_envs.planners.close_loop_block_picking_planner import CloseLoopBlockPickingPlanner

class CloseLoopPegInsertionEnv(CloseLoopEnv):
  def __init__(self, config):
    super().__init__(config)

  def initialize(self):
    super().initialize()

  def reset(self):
    self.resetPybulletWorkspace()
    self.robot.moveTo([self.workspace[0].mean(), self.workspace[1].mean(), 0.2], transformations.quaternion_from_euler(0, 0, 0))

    self.peg = pb_obj_generation.generatePeg([0.5,0,0.17], [0,1,0,1], 2.0)
    self.robot.closeGripper()

    self._generateShapes(constants.CUBE, 1, random_orientation=self.random_orientation)

    return self._getObservation()

  def _checkTermination(self):
    return False

def createCloseLoopPegInsertionEnv(config):
  return CloseLoopPegInsertionEnv(config)

if __name__ == '__main__':
  import matplotlib.pyplot as plt
  workspace = np.asarray([[0.2, 0.8],
                          [-0.3, 0.3],
                          [0.01, 0.50]])
  env_config = {'workspace': workspace, 'max_steps': 100, 'obs_size': 128, 'render': True, 'fast_mode': True,
                'seed': 2, 'action_sequence': 'pxyzr', 'num_objects': 1, 'random_orientation': False,
                'reward_type': 'step_left', 'simulate_grasp': True, 'perfect_grasp': False, 'robot': 'panda',
                'object_init_space_check': 'point', 'physics_mode': 'fast', 'object_scale_range': (1, 1), 'hard_reset_freq': 1000}
  planner_config = {'random_orientation': False, 'dpos': 0.05, 'drot': np.pi/8}
  env_config['seed'] = 1
  env = CloseLoopPegInsertionEnv(env_config)
  #planner = CloseLoopBlockPickingPlanner(env, planner_config)
  obs = env.reset()

  while True:
  #  action = planner.getNextAction()
    plt.imshow(obs[2].squeeze(), cmap='gray'); plt.show()
    obs, reward, done = env.step([0,0,0,0,0])
