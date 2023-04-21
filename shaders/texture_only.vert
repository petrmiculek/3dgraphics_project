#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec3 position;

// layout (location = 0) in vec3 aPos;

// out vec3 TexCoords;



out vec2 frag_tex_coords;

void main() {
    gl_Position = projection * view * model * vec4(position, 1);  // aPos
    frag_tex_coords = (model * vec4(position, 1)).xz;  // texture projected from above, works for grass (not for bunny)
    // TexCoords = aPos;
}
