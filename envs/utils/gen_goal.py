import copy as cp
import random
import numpy as np
from helping_hands_rl_envs.simulators import constants
import pybullet as pb


class NoValidPositionException(Exception):
    pass


class GenGoal:

    ONE_BLOCK = "1b"
    TWO_BLOCKS = "2b"
    BRICK = "1l"
    TRIANGLE = "1r"
    ROOF = "2r"
    CHARS = [ONE_BLOCK, TWO_BLOCKS, BRICK, TRIANGLE, ROOF]

    class Stack:

        def __init__(self, levels):

            self.levels = levels

        def gen(self):

            for level in self.levels:
                level.gen()

    class Level:

        MAX_BLOCK_SIZE = 0.03
        ZERO_ROT = pb.getQuaternionFromEuler([0., 0., 0])

        def __init__(self, level_type, env, height, below_level=None):

            self.type = level_type
            self.env = env
            self.height = height
            self.below_level = below_level

        def gen(self):

            if self.below_level is None:
                self.gen_bottom_()
            else:
                self.gen_above_()

        def gen_bottom_(self):

            padding = self.MAX_BLOCK_SIZE * 1.5
            pos1 = self.env._getValidPositions(padding, 0, [], 1)[0]

            if self.type == GenGoal.TWO_BLOCKS:
                min_dist = 2.1 * self.MAX_BLOCK_SIZE
                max_dist = 2.2 * self.MAX_BLOCK_SIZE

                sample_range = [[pos1[0] - 0.005, pos1[0] + 0.005],
                                [pos1[1] - max_dist, pos1[1] + max_dist]]

                pos2 = None
                for i in range(100):
                    try:
                        pos2 = self.env._getValidPositions(
                            padding, min_dist, [pos1], 1, sample_range=sample_range
                        )[0]
                    except Exception:
                        continue
                    dist = np.linalg.norm(np.array(pos1) - np.array(pos2))
                    if min_dist < dist < max_dist:
                        break

                self.env.generateObject(
                    (pos1[0], pos1[1], self.MAX_BLOCK_SIZE / 2),
                    self.ZERO_ROT, constants.CUBE
                )

                self.env.generateObject(
                    (pos2[0], pos2[1], self.MAX_BLOCK_SIZE / 2),
                    self.ZERO_ROT, constants.CUBE
                )

                self.position = (pos1, pos2)
            else:
                obj = None
                if self.type == GenGoal.ONE_BLOCK:
                    obj = constants.CUBE
                elif self.type == GenGoal.TRIANGLE:
                    obj = constants.TRIANGLE
                elif self.type == GenGoal.BRICK:
                    obj = constants.BRICK
                elif self.type == GenGoal.ROOF:
                    obj = constants.ROOF

                self.env.generateObject(
                    [pos1[0], pos1[1], self.MAX_BLOCK_SIZE / 2],
                    pb.getQuaternionFromEuler([0., 0., 0.]),
                    obj
                )

                self.position = pos1

        def gen_above_(self):

            offset = (self.MAX_BLOCK_SIZE / 2)

            if self.below_level.type == GenGoal.ONE_BLOCK:

                pos = self.below_level.position

                if self.type == GenGoal.ONE_BLOCK:
                    obj = constants.CUBE
                elif self.type == GenGoal.TRIANGLE:
                    obj = constants.TRIANGLE
                else:
                    raise ValueError("Unknown object.")

                self.env.generateObject(
                    (pos[0], pos[1], self.MAX_BLOCK_SIZE * self.height + offset),
                    self.ZERO_ROT, obj
                )

                self.position = pos

            elif self.below_level.type == GenGoal.TWO_BLOCKS:

                pos1 = self.below_level.position[0]
                pos2 = self.below_level.position[1]

                if self.type in [GenGoal.ONE_BLOCK, GenGoal.TRIANGLE]:

                    if self.type == GenGoal.ONE_BLOCK:
                        obj = constants.CUBE
                    else:
                        obj = constants.TRIANGLE

                    pos = random.choice([pos1, pos2])
                    self.env.generateObject(
                        (pos[0], pos[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, obj
                    )

                    self.position = pos

                elif self.type == GenGoal.TWO_BLOCKS:

                    self.env.generateObject(
                        (pos1[0], pos1[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, constants.CUBE
                    )

                    self.env.generateObject(
                        (pos2[0], pos2[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, constants.CUBE
                    )

                    self.position = (pos1, pos2)

                else:

                    if self.type == GenGoal.BRICK:
                        obj = constants.BRICK
                    elif self.type == GenGoal.ROOF:
                        obj = constants.ROOF
                    else:
                        raise ValueError("Unknown object.")

                    pos = np.mean(np.array([pos1, pos2]), axis=0)

                    self.env.generateObject(
                        (pos[0], pos[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, obj
                    )

                    self.position = pos

            elif self.below_level.type == GenGoal.BRICK:

                pos = self.below_level.position

                if self.type in [GenGoal.ONE_BLOCK, GenGoal.TRIANGLE]:

                    limits = [pos[1] - self.MAX_BLOCK_SIZE, pos[1] + self.MAX_BLOCK_SIZE]
                    new_pos = np.random.uniform(limits[0], limits[1])
                    new_pos = [pos[0], new_pos]

                    if self.type == GenGoal.ONE_BLOCK:
                        obj = constants.CUBE
                    else:
                        obj = constants.TRIANGLE

                    self.env.generateObject(
                        (new_pos[0], new_pos[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, obj
                    )

                    self.position = new_pos

                elif self.type == GenGoal.TWO_BLOCKS:

                    pos1 = [pos[0], pos[1] - self.MAX_BLOCK_SIZE]
                    pos2 = [pos[0], pos[1] + self.MAX_BLOCK_SIZE]

                    self.env.generateObject(
                        (pos1[0], pos1[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, constants.CUBE
                    )

                    self.env.generateObject(
                        (pos2[0], pos2[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, constants.CUBE
                    )

                    self.position = (pos1, pos2)

                else:

                    if self.type == GenGoal.BRICK:
                        obj = constants.BRICK
                    elif self.type == GenGoal.ROOF:
                        obj = constants.ROOF
                    else:
                        raise ValueError("Unknown object.")

                    self.env.generateObject(
                        (pos[0], pos[1], self.MAX_BLOCK_SIZE * self.height + offset),
                        self.ZERO_ROT, obj
                    )

                    self.position = pos

            else:

                raise ValueError("Unknown object.")

    def __init__(self, goal, env, additional_objects=True):

        self.goal = goal
        self.env = env
        self.additional_objects = additional_objects

        self.parse_goal_()

    def gen(self):
        # generate structure
        self.levels.gen()

        structure_objs = cp.copy(self.env.structure_objs)

        # I always want to have the same number of objects in the environment
        # this is for all possible structures of max_height=3, max_width=2 with a roof on top
        num_blocks = 4 - self.num_blocks
        num_bricks = 2 - self.num_bricks
        num_triangles = 1 - self.num_triangles
        num_roofs = 1 - self.num_roofs

        if self.additional_objects:
            for i in range(100):
                try:
                    if num_roofs > 0:
                        self.env._generateShapes(
                            constants.ROOF, num_roofs, random_orientation=self.env.random_orientation
                        )
                except Exception as e:
                    continue
                else:
                    break

            for i in range(100):
                try:
                    if num_bricks > 0:
                        self.env._generateShapes(
                            constants.BRICK, num_bricks, random_orientation=self.env.random_orientation
                        )
                except Exception as e:
                    continue
                else:
                    break

            for i in range(100):
                try:
                    if num_blocks > 0:
                        self.env._generateShapes(
                            constants.CUBE, num_blocks, random_orientation=self.env.random_orientation
                        )
                except Exception as e:
                    continue
                else:
                    break

            for i in range(100):
                try:
                    if num_triangles > 0:
                        self.env._generateShapes(
                            constants.TRIANGLE, num_triangles, random_orientation=self.env.random_orientation
                        )
                except Exception as e:
                    continue
                else:
                    break

            self.env.structure_objs = structure_objs
            self.env.num_obj = len(structure_objs)

        self.env.wait(50)

    def parse_goal_(self):

        self.num_blocks = 0
        self.num_bricks = 0
        self.num_triangles = 0
        self.num_roofs = 0

        self.levels = []

        assert len(self.goal) % 2 == 0

        for i in range(len(self.goal) // 2):
            chars = self.goal[i * 2: (i + 1) * 2]
            assert chars in self.CHARS

            if chars == self.ONE_BLOCK:
                self.num_blocks += 1
            elif chars == self.TWO_BLOCKS:
                self.num_blocks += 2
            elif chars == self.BRICK:
                self.num_bricks += 1
            elif chars == self.TRIANGLE:
                self.num_triangles += 1
            elif chars == self.ROOF:
                self.num_roofs += 1

            if i == 0:
                level = self.Level(chars, self.env, i, None)
            else:
                level = self.Level(chars, self.env, i, self.levels[-1])

            self.levels.append(level)

        self.levels = self.Stack(self.levels)

        self.height = len(self.levels.levels)
