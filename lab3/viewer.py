#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

# External, non built-in modules
import OpenGL.GL as GL  # standard Python OpenGL wrapper
import numpy as np  # all matrix manipulations & OpenGL args
import glfw  # lean window system wrapper for OpenGL

from core import Shader, Mesh, Viewer, Node, load
from cactus import CactusBuilder
from transform import translate, identity


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """

    def __init__(self, shader, **uniforms):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, normal=col), **uniforms)

    def draw(self, primitives=GL.GL_LINES, **uniforms):
        super().draw(primitives=primitives, **uniforms)


class Triangle(Mesh):
    """Hello triangle object"""

    def __init__(self, shader):
        position = np.array(((0, .5, 0), (-.5, -.5, 0), (.5, -.5, 0)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
        self.color = (1, 1, 0)
        attributes = dict(position=position, color=color)
        super().__init__(shader, attributes=attributes)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, global_color=self.color, **uniforms)

    def key_handler(self, key):
        if key == glfw.KEY_C:
            self.color = (0, 0, 0)


def transform_axis(ax, t):
    """
    Apply a transformation to an axis.
    :param ax: axis to transform [3]
    :param t: transformation matrix [4x4]
    """
    return np.around(np.array([np.r_[ax, [0]]]) @ t, 4)[0, :3]
# -------------- main program and scene setup --------------------------------


def main():
    viewer = Viewer()
    scene = Node([], alpha=0.4)
    viewer.add(scene)
    shader = Shader("color.vert", "color.frag")

    angles = [
        [[], [0, 180], [0], [90]],  # 1
        [[0]],  # 2
        [[]]  # 3
    ]
    ''' Cactus '''
    offset = translate(x=-2, z=-1)
    offset_sum = identity() + translate(x=8, z=-4)

    cb = CactusBuilder(shader)

    for b1_angles in angles[0]:
        cact = cb.cactus([b1_angles, angles[1][0], angles[2][0]])
        offset_sum = offset_sum @ offset
        cact.apply(offset_sum)
        scene.add(cact)

    viewer.run()


if __name__ == '__main__':
    main()  # main function keeps variables locally scoped
