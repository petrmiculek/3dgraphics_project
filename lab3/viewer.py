#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import glfw                         # lean window system wrapper for OpenGL

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
'''
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    # default color shader
    shader = Shader("color.vert", "color.frag")

    # place instances of our basic objects
    viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader)])
    if len(sys.argv) < 2:
        scaling = 0.2
        t1 = translate(x=+2 * scaling) @ scale(scaling)
        viewer.add(Axis(shader))
        viewer.add(Node(children=[Cylinder(shader)], transform=t1))
        viewer.add(Node(children=[Triangle(shader)], transform=translate(x=-1 * scaling) @ scale(scaling)))
        print('Usage:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
              ' format supported by assimp.' % (sys.argv[0],))

    # start rendering loop
    viewer.run()
'''

'''
def main():
        viewer = Viewer()
        shader = Shader("color.vert", "color.frag")
        scaling = 0.2
        t_arm = translate(y=+2 * scaling) @ scale(x=0.3, y=1, z=0.3) # @ scale(scaling)
        t_forearm = translate(y=+3 * scaling) @ scale(x=0.5, y=1, z=0.5) # @ scale(scaling)

        # ---- let's make our shapes ---------------------------------------
        # think about it: we can re-use the same cylinder instance!
        cylinder = Cylinder(shader)

        # make a thin cylinder
        forearm_shape = Node(transform=t_forearm)
        forearm_shape.add(cylinder)                 # shape of forearm
        
        # make a thin cylinder
        arm_shape = Node(children=[forearm_shape], transform=t_arm)
        arm_shape.add(cylinder)                     # shape of arm
        
        # make a flat cylinder
        base_shape = Node(children=[arm_shape], transform=scale(scaling))
        base_shape.add(cylinder)                    # shape of robot base

        viewer.add(base_shape)

        axis = Axis(shader)
        # transform_arm = Node(transform=rotate((...), phi1))
        # transform_arm.add(arm_shape, transform_forearm)
        # transform_arm.add(axis)        
        
        viewer.run()
'''
def main():
    viewer = Viewer()
    shader = Shader("color.vert", "color.frag")
    scaling = 0.2
    t_arm = translate(y=+0.6) @ scale(x=0.1, y=1, z=0.1) @ scale(scaling)
    t_forearm = translate(y=+1) @ scale(x=0.2, y=1, z=0.2) @ scale(scaling)

    # ---- let's make our shapes ---------------------------------------
    # base_shape = ...
    # arm_shape = ...
    # forearm_shape = ...
        # ---- let's make our shapes ---------------------------------------
    # think about it: we can re-use the same cylinder instance!
    cylinder = Cylinder(shader)

    # make a thin cylinder
    forearm_shape = Node(transform=t_forearm)
    forearm_shape.add(cylinder)                 # shape of forearm
    
    # make a thin cylinder
    arm_shape = Node(children=[forearm_shape], transform=t_arm)
    arm_shape.add(cylinder)                     # shape of arm
    
    # make a flat cylinder
    base_shape = Node(children=[arm_shape], transform=scale(scaling))
    base_shape.add(cylinder)                    # shape of robot base


    # ---- construct our robot arm hierarchy ---------------------------
    theta = 45.0        # base horizontal rotation angle
    phi1 = 45.0         # arm angle
    phi2 = 20.0         # forearm angle
    axis = Axis(shader)
    transform_forearm = Node(transform=translate(x=0.25) @ rotate(((0, 0, 1)), phi2)) # 
    transform_forearm.add(forearm_shape)

    transform_arm = Node(transform=rotate(((0, 0, 1)), phi1))  # 
    transform_arm.add(arm_shape, transform_forearm)

    transform_base = Node(transform=rotate(((0, 1, 0)), theta))
    transform_base.add(base_shape, transform_arm)

    viewer.add(transform_base)
    viewer.add(axis)
    
    viewer.run()

if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
