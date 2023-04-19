#version 330 core

in vec3 tex_coords;
out vec4 out_color;
uniform samplerCube diffuse_map;

void main()
{
    out_color = texture(diffuse_map, tex_coords);
}

