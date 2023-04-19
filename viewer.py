#!/usr/bin/env python3
# standard library imports
import sys
from itertools import cycle
# external libraries
import OpenGL.GL as GL  # standard Python OpenGL wrapper
import glfw  # lean window system wrapper for OpenGL
import numpy as np  # all matrix manipulations & OpenGL args

# local imports
from core import Shader, Viewer, Mesh, load, Node
from texture import Texture, Textured, TexturedPlane
from transform import translate, rotate, scale
from skybox import Skybox
from smoke import SmokeList, Smoke

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    shader = Shader("shaders/texture.vert", "shaders/texture.frag")
    shader_grass = Shader("shaders/texture_old.vert", "shaders/texture_old.frag")
    shader_skybox = Shader("shaders/skybox.vert", "shaders/skybox.frag")
    shader_smoke = Shader("shaders/smoke.vert", "shaders/smoke.frag")
    light_dir = (0, -1, 0)

    ''' Command line-provided models '''
    viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader, light_dir=light_dir)])

    ''' Grass '''
    grass = Node([TexturedPlane(shader_grass, "assets/grass.png")], transform=rotate(angle=270) @ translate(0, 0, -0.5))
    viewer.add(grass)

    ''' Wooden box '''
    # box_wooden = load('assets/cube.obj', shader_grass, light_dir=light_dir)[0]
    # viewer.add(box_wooden)

    ''' Bunny '''
    bunny = load("assets/bunny.obj", shader, light_dir=light_dir)[0]
    viewer.add(bunny)

    '''Smoke'''
    # smokeList = SmokeList(500, shader_smoke)
    # TODO: How to update the smokelist particles with smokeList.update(0.05)?
    # viewer.add(smokeList)

    ''' Skybox '''
    skybox = Skybox(shader_skybox)  # 'assets/skybox.jpg'
    viewer.add(skybox)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()  # main function keeps variables locally scoped
