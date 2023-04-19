from os.path import join
import OpenGL.GL as GL
import numpy as np
from PIL import Image
from core import VertexArray, Node
import random

# Source: https://learnopengl.com/In-Practice/2D-Game/Particles

class SmokeList:
    # Class to keep hold of all smoke particles. Should be OK
    def __init__(self, particles, shader):
        self.particles = particles
        self.firstUnused = 0
        self.particleList = np.empty(particles, dtype=object)
        for i in range(0, self.particles):
            np.insert(self.particleList, i, Smoke(shader))

    def findFirstUnused(self):
        # This is OK
        for i in range(self.firstUnused, self.particles):
            if (self.particleList[i].life <= 0.0):
                self.firstUnused = i
                return self.particleList[self.firstUnused]

        for i in range(0, self.firstUnused):
            if (self.particleList[i].life <= 0.0):
                self.firstUnused = i
                return self.particleList[self.firstUnused]

        return None   

    def respawnParticle(self, offset, newParticles = 2):
        # newParticles means how many particles we want to revitalise. Set default to same as in source.
        for i in range(0, newParticles):
            unused = self.findFirstUnused()
            if (unused):
                r = random.uniform(0.0, 100.0) # TODO: does this make sense?
                rColor = 0.5 + (r % 100) / 100.0
                unused.Position = offset + r + unused.Position
                unused.Color = np.array([rColor, rColor, rColor, 1.0])
                unused.Life = 1.0
                unused.Velocity = unused.Velocity * 0.1

    def update(self, dt):
        # Updates all particles in the list. 
        # Should be OK
        for particle in self.particleList:
            particle.Life -= dt 
            if (particle.Life > 0.0):
                particle.Position -= particle.Velocity * dt
                particle.Color.a -= dt * 2.5


class Smoke(Node):
    # Class for smoke particle
    # Init should be OK
    def __init__(self, shader):
        super().__init__()

        self.Life = 1.0
        self.Velocity = np.array([0.0, 0.05, 0.0])
        self.Color = np.array([random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), 1.0])
        self.Position = np.array([random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0)])
        self.Vertices = np.array([1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0])

        self.shader = shader
        self.vertex_array = VertexArray(shader, dict(position=self.Vertices))
        self.texture = self.load_smokemap(self.Vertices)
        # todo save as node.children

        # Get Uniform location of shader program
        names = ['diffuse_map', 'offset', 'color', 'projection']
        self.loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}

    @staticmethod
    def load_smokemap(self):
        # Uncertain about if it's working, but everything is according to source
        self.vbo = np.array([])
        texture_smokemap = GL.glGenTextures(1)
        GL.glGenVertexArrays(1, self.vertex_array)
        GL.glGenBuffers(1, self.vbo)
        GL.glBindVertexArray(self.vertex_array)
        # fill mesh buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(self.vertices), self.vertices, GL.GL_STATIC_DRAW)
        # set mesh attributes
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 4, 0)
        GL.glBindVertexArray(0)
        return texture_smokemap

    def draw(self, **other_uniforms):
        # Draw the particles. Should be OK
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE)
        GL.glUseProgram(self.shader.glid)
        if (self.Life > 0.0):
            GL.glUniform2f(self.loc['offset'], self.Position[0], self.Position[1])
            GL.glUniform4fv(self.loc['color'], 1, GL.GL_TRUE, other_uniforms['color'])
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture) # TODO: Not sure about GL_TEXTURE_2D?????
            GL.glBindVertexArray(self.vertex_array)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
            GL.glBindVertexArray(0)
        
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
