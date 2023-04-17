import OpenGL.GL as GL              # standard Python OpenGL wrapper
from PIL import Image               # load texture maps
import numpy as np


# -------------- OpenGL Texture Wrapper ---------------------------------------
class Texture:
    """ Helper class to create and automatically destroy textures """
    def __init__(self, tex_file, wrap_mode=GL.GL_REPEAT,
                 mag_filter=GL.GL_LINEAR, min_filter=GL.GL_LINEAR_MIPMAP_LINEAR,
                 tex_type=GL.GL_TEXTURE_2D):
        self.glid = GL.glGenTextures(1)
        self.type = tex_type
        try:
            # imports image as a numpy array in exactly right format
            tex = Image.open(tex_file).convert('RGBA')
            GL.glBindTexture(tex_type, self.glid)
            GL.glTexImage2D(tex_type, 0, GL.GL_RGBA, tex.width, tex.height,
                            0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex.tobytes())
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_S, wrap_mode)
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_T, wrap_mode)
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MIN_FILTER, min_filter)
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MAG_FILTER, mag_filter)
            GL.glGenerateMipmap(tex_type)
            print(f'Loaded texture {tex_file} ({tex.width}x{tex.height}'
                  f' wrap={str(wrap_mode).split()[0]}'
                  f' min={str(min_filter).split()[0]}'
                  f' mag={str(mag_filter).split()[0]})')
        except FileNotFoundError:
            print("ERROR: unable to load texture file %s" % tex_file)

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)


# -------------- Textured mesh decorator --------------------------------------
class Textured:
    """ Drawable mesh decorator that activates and binds OpenGL textures """
    def __init__(self, drawable, **textures):
        self.drawable = drawable
        self.textures = textures

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        for index, (name, texture) in enumerate(self.textures.items()):
            GL.glActiveTexture(GL.GL_TEXTURE0 + index)
            GL.glBindTexture(texture.type, texture.glid)
            uniforms[name] = index
        self.drawable.draw(primitives=primitives, **uniforms)


class Skybox:
    ''' Draw the skybox class.
        Source: https://learnopengl.com/Advanced-OpenGL/Cubemaps
        
    '''
    def __init__(self, tex_files, tex_type=GL.GL_TEXTURE_CUBE_MAP):
        self.glid = GL.glGenTextures(1)
        self.bindTex = GL.glBindTexture(tex_type, self.glid)
        self.type = tex_type
        try:
            tex = Image.open(tex_files).convert('RGBA').resize((512,512))
            for i in range(0, 6): #len(tex_files)
                # imports image as a numpy array in exactly right format
                # tex here and make it loop through list in tex_files
                GL.glBindTexture(tex_type, self.glid)
                GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGBA, tex.width, tex.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex.tobytes())
            
            GL.glTexParameterf(tex_type, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE) 
            GL.glTexParameterf(tex_type, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameterf(tex_type, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE) 
            GL.glTexParameterf(tex_type, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST) 
            GL.glTexParameterf(tex_type, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST) 

        except FileNotFoundError:
            print("ERROR: unable to load skybox texture file %s" % tex_files)

    def draw(self, primitives=GL.GL_TRIANGLES, tex_type=GL.GL_TEXTURE_CUBE_MAP, **uniforms):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(False)

        GL.glUseProgram(self.shader.glid)

        GL.glBindTexture(tex_type, 0)
        GL.glDrawArrays(primitives, 0, 36)
        GL.glDepthMask(True)
        GL.glEnable(GL.GL_DEPTH_TEST)
