from os.path import join
import OpenGL.GL as GL
import numpy as np
from PIL import Image
from core import VertexArray, Node

# todo redo with indices

# empty lines separate triangles of the cube
vertices = np.array((
    (-1.0, 1.0, -1.0),
    (-1.0, -1.0, -1.0),
    (1.0, -1.0, -1.0),

    (1.0, -1.0, -1.0),
    (1.0, 1.0, -1.0),
    (-1.0, 1.0, -1.0),

    (-1.0, -1.0, 1.0),
    (-1.0, -1.0, -1.0),
    (-1.0, 1.0, -1.0),

    (-1.0, 1.0, -1.0),
    (-1.0, 1.0, 1.0),
    (-1.0, -1.0, 1.0),

    (1.0, -1.0, -1.0),
    (1.0, -1.0, 1.0),
    (1.0, 1.0, 1.0),

    (1.0, 1.0, 1.0),
    (1.0, 1.0, -1.0),
    (1.0, -1.0, -1.0),

    (-1.0, -1.0, 1.0),
    (-1.0, 1.0, 1.0),
    (1.0, 1.0, 1.0),

    (1.0, 1.0, 1.0),
    (1.0, -1.0, 1.0),
    (-1.0, -1.0, 1.0),

    (-1.0, 1.0, -1.0),
    (1.0, 1.0, -1.0),
    (1.0, 1.0, 1.0),

    (1.0, 1.0, 1.0),
    (-1.0, 1.0, 1.0),
    (-1.0, 1.0, -1.0),

    (-1.0, -1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (1.0, -1.0, -1.0),

    (1.0, -1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (1.0, -1.0, 1.0)), 'f')

names_images = [
    "left.jpg", "right.jpg",
    "top.jpg", "bottom.jpg",
    "front.jpg", "back.jpg"
]
path_images = "assets/skybox"
list_paths = [join(path_images, filename) for filename in names_images]


class Skybox(Node):
    def __init__(self, shader_skybox):
        super().__init__()

        self.shader_skybox = shader_skybox
        self.texture = self.load_cubemap()
        # todo save as node.children
        self.vertex_array = VertexArray(shader_skybox, dict(position=vertices))

        # Get Uniform location of shader program
        names = ['view', 'projection']  # , 'model'
        self.loc = {n: GL.glGetUniformLocation(self.shader_skybox.glid, n) for n in names}

    @staticmethod
    def load_cubemap():
        texture_cubemap = GL.glGenTextures(1)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, texture_cubemap)

        for index, face_url in enumerate(list_paths):
            face = np.array(Image.open(face_url))
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + index, 0, GL.GL_RGB, face.shape[1],
                            face.shape[0], 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, face)

        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

        return texture_cubemap

    def draw(self, **other_uniforms):
        # todo work with node.draw()
        GL.glUseProgram(self.shader_skybox.glid)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthMask(GL.GL_FALSE)
        GL.glUniformMatrix4fv(self.loc['view'], 1, True, other_uniforms['view'])
        GL.glUniformMatrix4fv(self.loc['projection'], 1, True, other_uniforms['projection'])
        GL.glBindVertexArray(self.vertex_array.glid)
        GL.glEnableVertexAttribArray(0)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.texture)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
        GL.glDisableVertexAttribArray(0)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LESS)
