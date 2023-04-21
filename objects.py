# standard library
from itertools import cycle

# external libraries
import numpy as np
import glfw

# local imports
from core import Mesh
from texture import Textured, Texture
from OpenGL import GL as GL

"""
Since texture.py was provided in the labs, we keep it unchanged and add similar functionality to a separate file.
"""
class TexturedPlaneShaded(Textured):
    """ Adapted from texture.py """

    def __init__(self, shader, tex_file, **uniforms):
        # prepare texture modes cycling variables for interactive toggling
        self.wraps = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                            GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filters = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                              (GL.GL_LINEAR, GL.GL_LINEAR),
                              (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap, self.filter = next(self.wraps), next(self.filters)
        self.file = tex_file

        # setup plane mesh to be textured
        base_coords = ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0))
        scaled = 100 * np.array(base_coords, np.float32)
        indices = np.array((0, 1, 2, 0, 2, 3), np.uint32)
        normals = np.array(((0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)))
        mesh = Mesh(shader, attributes=dict(position=scaled, normal=normals), index=indices, **uniforms)

        # setup & upload texture to GPU, bind it to shader name 'diffuse_map'
        texture = Texture(tex_file, self.wrap, *self.filter)
        super().__init__(mesh, diffuse_map=texture)

    def key_handler(self, key):
        # cycle through texture modes on keypress of F6 (wrap) or F7 (filtering)
        self.wrap = next(self.wraps) if key == glfw.KEY_F6 else self.wrap
        self.filter = next(self.filters) if key == glfw.KEY_F7 else self.filter
        if key in (glfw.KEY_F6, glfw.KEY_F7):
            texture = Texture(self.file, self.wrap, *self.filter)
            self.textures.update(diffuse_map=texture)


class TexturedMesh(Textured):
    """ Textured object """

    def __init__(self, shader, mesh, tex_file, **uniforms):
        self.wrap, self.filter = GL.GL_REPEAT, (GL.GL_NEAREST, GL.GL_NEAREST)
        self.file = tex_file

        # setup plane mesh to be textured
        # no indices
        mesh = Mesh(shader, attributes=dict(position=mesh, normal=uniforms['normals']), **uniforms)

        # setup & upload texture to GPU, bind it to shader name 'diffuse_map'
        texture = Texture(tex_file, self.wrap, *self.filter)
        super().__init__(mesh, diffuse_map=texture)


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """

    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

    def draw(self, primitives=GL.GL_LINES, **uniforms):
        super().draw(primitives=primitives, **uniforms)
