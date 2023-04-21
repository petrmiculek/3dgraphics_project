#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float time;

in vec3 position;
in vec3 normal;

in vec2 tex_coord;

out vec2 frag_tex_coords;

out vec3 w_position, w_normal;   // in world coordinates
out float distance;              // distance from camera to vertex
mat3 nit;


void main() {
    gl_Position = projection * view * model * vec4(position, 1);

    gl_Position.y += sin(time + position.x) * 1;
    // texture mapping
    frag_tex_coords = position.xz;

    // shading
    nit = transpose(inverse(mat3(model)));

    w_position = (model * vec4(position, 1)).xyz;
    w_normal = normalize(nit * normal);

    distance = length(w_position);
}
