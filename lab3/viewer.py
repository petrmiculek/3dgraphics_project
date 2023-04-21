#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys  # for system arguments

# External, non built-in modules
import OpenGL.GL as GL  # standard Python OpenGL wrapper
import numpy as np  # all matrix manipulations & OpenGL args
import glfw  # lean window system wrapper for OpenGL

from core import Shader, Mesh, Viewer, Node, load
from transform import translate, identity, rotate, scale


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """

    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

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


class Cylinder(Node):
    """ Very simple cylinder based on provided load function """

    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader))  # just load cylinder from file


# -------------- main program and scene setup --------------------------------

def main():
    viewer = Viewer()
    shader = Shader("color.vert", "color.frag")

    axis = Axis(shader)

    scaling = 0.2
    t_arm = translate(y=+0.4) @ scale(x=0.2, y=1, z=0.2) @ scale(scaling)
    t_forearm = translate(y=+0.8) @ scale(x=0.1, y=1, z=0.1) @ scale(scaling)

    cylinder_obj = Cylinder(shader)
    theta = 45.0  # base horizontal rotation angle
    phi1 = 45.0  # arm angle
    phi2 = 20.0  # forearm angle
    if True:

        # make a thin cylinder
        forearm_shape = Node([cylinder_obj], transform=t_forearm)
        # forearm_shape.add()  # shape of forearm

        # make a thin cylinder
        arm_shape = Node(children=[forearm_shape, cylinder_obj], transform=t_arm)
        # arm_shape.add(cylinder_obj)  # shape of arm

        # make a flat cylinder
        base_shape = Node(children=[arm_shape, cylinder_obj], transform=scale(scaling))
        # base_shape.add(cylinder_obj)  # shape of robot base

        transform_forearm = Node(transform=translate(x=0.25) @ rotate((0, 0, 1), phi2))  #
        transform_forearm.add(forearm_shape)

        transform_arm = Node(transform=rotate((0, 0, 1), phi1))  #
        transform_arm.add(arm_shape, transform_forearm)

        transform_base = Node(transform=rotate((0, 1, 0), theta))
        transform_base.add(base_shape, transform_arm)

        viewer.add(transform_base)
        viewer.add(axis)

    else:
        cylinder = Node([cylinder_obj])
        cylinder.transform = cylinder.transform @ scale(0.2, 1, 0.2)

        # 2 branches coming out of the top of the cylinder
        # thinner, rotated, translated to begin at the top of the trunk
        t_b11 = rotate(angle=30, axis=(1, 0, 0))  # @ translate(0, 1, 0) # @ scale(0.5, 1, 0.5)
        t_b12 = rotate(angle=-30, axis=(1, 0, 0))  # @ translate(0, 1, 0) # @ scale(0.5, 1, 0.5)
        cylinder.add(Node([cylinder_obj], transform=t_b11))
        cylinder.add(Node([cylinder_obj], transform=t_b12))
        viewer.add(cylinder)

    viewer.run()

    # this still needs animation from:
    # https://franco.gitlabpages.inria.fr/3dgraphics/practical3.html#optional-exercise-keyboard-control


if __name__ == '__main__':
    main()  # main function keeps variables locally scoped
