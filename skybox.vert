#version 330 core

uniform mat4 view;
uniform mat4 projection;

layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

void main() {
    TexCoords = aPos;
    gl_position = projection * view * vec4(aPos, 1);
}