#!/usr/bin/env python3
# standard library imports
import sys
# external libraries
import numpy as np  # all matrix manipulations & OpenGL args

# local imports
from core import Shader, Viewer, load, Node
from objects import TexturedMesh, Axis, TexturedPlaneShaded
from transform import translate, scale, rotate
from skybox import Skybox


# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    shader_axis = Shader("shaders/axis.vert", "shaders/axis.frag")
    shader = Shader("shaders/texture.vert", "shaders/texture.frag")
    shader_grass = Shader("shaders/texture_old.vert", "shaders/texture_old.frag")
    shader_skybox = Shader("shaders/skybox.vert", "shaders/skybox.frag")
    # shader_smoke = Shader("shaders/smoke.vert", "shaders/smoke.frag")
    light_dir = (0, -1, 0)

    ''' Bunny '''
    bunny = load("assets/bunny.obj", shader, light_dir=light_dir)[0]
    viewer.add(bunny)

    ''' Command line-provided models '''
    # viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader, light_dir=light_dir)])

    ''' Axis '''
    """
    a debug tool to understand the coordinate system
    red = x = right, green = y = up, blue = z = forward
    """
    axis = Node([Axis(shader_axis)], transform=translate(0, 0, 0) @ scale(5))
    viewer.add(axis)

    ''' Smoke '''
    # smokeList = SmokeList(500, shader_smoke)
    # TODO: How to update the smokelist particles with smokeList.update(0.05)?
    # viewer.add(smokeList)

    ''' Skybox '''
    skybox = Skybox(shader_skybox)
    viewer.add(skybox)

    ''' Grass '''
    if False:  # not to be used in the final version
        # when using the old shader (shader_grass), the grass has a correct texture mapping, but there is no shading
        # new shader (shader) has no texture mapping, but has shading
        grass = Node([TexturedPlaneShaded(shader, "assets/grass.png", light_dir=light_dir)], transform=rotate(angle=270) @ translate(0, 0, -0.5))
        viewer.add(grass)

    ''' Terrain '''
    # todo make terrain a class
    # Don't forget to run the generate_terrain.py script to generate the terrain file
    terrain = np.load('assets/terrain.npz')
    terrain_vertices = terrain['vertices']
    # no indices
    terrain_normals = terrain['normals']
    terrain_grid = terrain['grid']
    x, z = terrain_grid.shape
    height_at_center = terrain_grid[x // 2, z // 2] + 0.5
    shift_x, shift_z = x // 2, z // 2  # these are moved to 0,0, making the terrain centered.
    terrain_shift = translate(-shift_x, -height_at_center, -shift_z)

    # Add terrain to the scene
    terrain_grass = TexturedMesh(shader, terrain_vertices, "assets/grass.png", light_dir=light_dir, normals=terrain_normals)
    terrain_node = Node([terrain_grass], transform=terrain_shift)  # shift terrain to be centered
    viewer.add(terrain_node)

    # terrain bounds in scene coordinates
    x_min, z_min = 0 - shift_x, 0 - shift_z
    x_max, z_max = x - shift_x, z - shift_z

    def place(obj, coords):
        """
        Place an object on the terrain at the given coordinates
        terrain is shifted (horizontally) by (-shift_x, -shift_z)

        :param obj: object to place
        :param coords: (x, z) coordinates in scene coordinates
        """
        x, z = int(coords[0]), int(coords[1])
        # x, z = x - shift_x, z - shift_z  # shift terrain to be centered
        if x < x_min or x > x_max or z < z_min or z > z_max:
            x = np.clip(x, x_min, x_max)
            z = np.clip(z, z_min, z_max)
            print(f"Placing object: coords ({x}, {z}) out of bounds, clipping to ({x}, {z}).", file=sys.stderr)

        # terrain_grid height at (x, z) is terrain_mesh height at (x + shift_x, z + shift_z)
        y = terrain_grid[x + shift_x, z + shift_z]
        obj.transform = translate(x, y, z) @ translate(y=-height_at_center)
        # object might end up inside the terrain - temporary solution: whole terrain is shifted down by 0.5

    ''' Water/Lava '''
    # todo
    # water level = 25% quantile of the terrain heights
    water_level = np.quantile(terrain_grid, 0.25)

    lava_level = np.quantile(terrain_grid, 0.95)
    # todo lava only inside the volcano

    ''' Wooden box '''
    box_wooden_obj = load('assets/cube.obj', shader, light_dir=light_dir)[0]
    box_node = Node([box_wooden_obj])
    place(box_node, (2, 2))
    viewer.add(box_node)

    """
    At some point we need to move the camera
    
    # These are not exactly what we need, but still helpful
    print(f"{viewer.trackball.distance=}")
    print(f"{viewer.trackball.pos2d=}")
    """


    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()  # main function keeps variables locally scoped
    # TODO
    """
    - terrain:
        - generation can run on the fly
        - make into a class
        - grass texture mapping is wrong
        - remove regular grid artifacts
        
    - volcano needs an inside wall - there is one, with only a few triangles
    - what is our Team number? mentioned here: https://franco.gitlabpages.inria.fr/3dgraphics/project.html
    - print list of controls at the start of the program
    """
