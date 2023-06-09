#version 330 core
in vec2 TexCoords;
in vec4 ParticleColor;
out vec4 color;

uniform sampler2D diffuse_map;

void main()
{
    color = (texture(diffuse_map, TexCoords) * ParticleColor);
}
