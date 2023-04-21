#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec3 position;
in vec3 normal;

in vec2 tex_coord;

out vec2 frag_tex_coords;

out vec3 w_position, w_normal;   // in world coordinates
out float distance;              // distance from camera to vertex
mat3 nit;


void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    // texture mapping
    frag_tex_coords = tex_coord; // position.xy;
//    frag_tex_coords = w_normal.xz;

    // shading
    nit = transpose(inverse(mat3(model)));

    w_position = (model * vec4(position, 1)).xyz;
    w_normal = (nit * normal);

    distance = length(gl_Position);
}
