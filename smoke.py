from os.path import join
import OpenGL.GL as GL
import numpy as np
from PIL import Image
from core import VertexArray, Node
import random



class SmokeList:
    def __init__(self, particles, shader):
        self.particles = particles
        self.firstUnused = 0
        self.particleList = np.empty(particles, dtype=object)
        random.seed(5)

    def findFirstUnused(self):
        for i in range(self.firstUnused, self.particles):
            if (self.particleList[i].life <= 0.0):
                self.firstUnused = i
                return self.particleList[self.firstUnused]

        for i in range(0, self.firstUnused):
            if (self.particleList[i].life <= 0.0):
                self.firstUnused = i
                return self.particleList[self.firstUnused]

        return None   

    def respawnParticle(self, offset, newParticles):
        for i in range(0, newParticles):
            unused = self.findFirstUnused()
            if (unused):
                r = random.random() # TODO: correct to a randint(a, b)
                rColor = 0.5 + (r % 100) / 100.0
                unused.Position = offset + r + unused.Position
                unused.Color = (rColor, rColor, rColor, 1.0)
                unused.Life = 1.0
                unused.Velocity = unused.Velocity * 0.1


class Smoke(Node):
    def __init__(self, shader):
        super().__init__()

        self.life = 1.0

        self.shader = shader
        self.texture = self.load_cubemap()
        # todo save as node.children
        self.vertex_array = VertexArray(shader, dict(position=...))

        # Get Uniform location of shader program
        names = ['view', 'projection', 'model', 'blend_factor', 'skybox', 'skybox2', 'sky_color']
        self.loc = {n: GL.glGetUniformLocation(self.shader_skybox.glid, n) for n in names}

    @staticmethod
    def load_smokemap():
        texture_smokemap = GL.glGenTextures(1)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_smokemap)


        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + index, 0, GL.GL_RGB, face.shape[1],
                            face.shape[0], 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, face)

        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

        return texture_smokemap

    def draw(self, **other_uniforms):
        pass
