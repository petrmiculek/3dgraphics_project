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
    shader = Shader("shaders/texture_phong.vert", "shaders/texture_phong.frag")
    shader_lava = Shader("shaders/terrain.vert", "shaders/texture_phong.frag")
    # shader_grass = Shader("shaders/texture_only.vert", "shaders/texture_only.frag")
    shader_terrain = Shader("shaders/terrain.vert", "shaders/terrain.frag")
    shader_skybox = Shader("shaders/skybox.vert", "shaders/skybox.frag")
    # shader_smoke = Shader("shaders/smoke.vert", "shaders/smoke.frag")
    light_dir = (0, -1, 0)
    scene = Node(light_dir=light_dir, k_a=[.2]*3)  # , k_s=[.2]*3, s=5
    viewer.add(scene)

    ''' Command line-provided models '''
    # scene.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader, light_dir=light_dir)])

    ''' Axis '''
    """
    a debug tool to understand the coordinate system
    red = x = right, green = y = up, blue = z = backward
    """
    axis = Node([Axis(shader_axis)], transform=translate(0, 0, 0) @ scale(5))
    scene.add(axis)

    ''' Smoke '''
    # smokeList = SmokeList(500, shader_smoke)
    # TODO: How to update the smokelist particles with smokeList.update(0.05)?
    # scene.add(smokeList)

    ''' Skybox '''
    skybox = Skybox(shader_skybox)
    scene.add(skybox)

    ''' Grass '''
    if False:  # not to be used in the final version
        # when using the old shader (shader_grass), the grass has a correct texture mapping, but there is no shading
        # new shader (shader) has no texture mapping, but has shading
        grass = Node([TexturedPlaneShaded(shader_grass, "assets/grass.png", light_dir=light_dir)],
                     transform=rotate(angle=270) @ translate(0, 0, -0.5))
        scene.add(grass)

    ''' Terrain '''
    # todo make terrain a class
    # Don't forget to run the generate_terrain.py script to generate the terrain file
    terrain = np.load('assets/terrain.npz')
    terrain_vertices = terrain['ground_vertices']
    # no indices
    terrain_normals = terrain['ground_normals']
    terrain_grid = terrain['ground_grid']
    x, z = terrain_grid.shape
    height_at_center = terrain_grid[x // 2, z // 2] + 0.5
    shift_x, shift_z = x // 2, z // 2  # these are moved to 0,0, making the terrain centered.
    terrain_shift = translate(-shift_x, -height_at_center, -shift_z)

    # Add terrain to the scene
    terrain_grass = TexturedMesh(shader_terrain, terrain_vertices, "assets/grass.png",
                                 normals=terrain_normals,)  # k_s=0,  k_d=(0.5, 0.5, 0.5)
    terrain_node = Node([terrain_grass], transform=terrain_shift)  # shift terrain to be centered
    scene.add(terrain_node)

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
        if x < x_min or x > x_max or z < z_min or z > z_max:
            x = np.clip(x, x_min, x_max)
            z = np.clip(z, z_min, z_max)
            print(f"Placing object: coords ({x}, {z}) out of bounds, clipping to ({x}, {z}).", file=sys.stderr)

        # terrain_grid height at (x, z) is terrain_mesh height at (x + shift_x, z + shift_z)
        y = terrain_grid[x + shift_x, z + shift_z]
        obj.apply(translate(x, y, z) @ translate(y=-height_at_center + 0.5))
        # object might end up inside the terrain - temporary solution: whole terrain is shifted down by 0.5


    ''' Water/Lava '''
    # todo
    # water level = 25% quantile of the terrain heights
    water_level = np.quantile(terrain_grid, 0.25)

    lava_vertices = terrain['lava_vertices']
    lava_normals = terrain['lava_normals']

    lava_center = np.array(lava_vertices.mean(axis=0), dtype=int)
    lx, ly, lz = lava_center
    # lava_center = (lx - shift_x, ly - height_at_center, lz - shift_z)


    lava = TexturedMesh(shader_lava, lava_vertices, "assets/lava.jpg", normals=lava_normals)
    lava_node = Node([lava], transform=terrain_shift)  #
    scene.add(lava_node)

    ''' Bunny '''
    bunny_obj = load("assets/bunny.obj", shader)[0]
    bunny = Node([bunny_obj], k_s=[.8]*3, s=5)  # bunny made shiny to verify the lighting
    place(bunny, (1, -8))
    scene.add(bunny)

    ''' Wooden box '''
    box_wooden_obj = load('assets/cube.obj', shader)[0]  # k_d=(.5, .5, .5)
    box_node = Node([box_wooden_obj])
    place(box_node, (2, 2))
    scene.add(box_node)

    """
    At some point we need to move the camera
    
    # These are not exactly what we need, but still helpful
    print(f"{viewer.trackball.distance=}")
    print(f"{viewer.trackball.pos2d=}")
    """

    ''' Tree '''
    if False:
        cylinder_obj = load('assets/cylinder.obj', shader_axis, light_dir=light_dir)[0]
        cylinder = Node([cylinder_obj])
        cylinder.apply(scale(0.2, 1, 0.2))

        # 2 branches coming out of the top of the cylinder
        # thinner, rotated, translated to begin at the top of the trunk
        t_b11 = translate(0, 1, 0) @ rotate(angle=30, axis=(1, 0, 0)) @ scale(0.5, 1, 0.5)
        t_b12 = translate(0, 1, 0) @ rotate(angle=-30, axis=(1, 0, 0)) @ scale(0.5, 1, 0.5)
        cylinder.add(Node([cylinder_obj], transform=t_b11))
        cylinder.add(Node([cylinder_obj], transform=t_b12))

        place(cylinder, (0, -2))

        scene.add(cylinder)


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
        
    - make fog move together with the camera (or some character?)
        
    - volcano needs an inside wall - there is one, with only a few triangles
    - what is our Team number? mentioned here: https://franco.gitlabpages.inria.fr/3dgraphics/project.html
    - print list of controls at the start of the program
    """


