#version 330 core

in vec3 TexCoords;
out vec4 out_color;
uniform samplerCube skybox;

void main() {
    out_color = texture(skybox, TexCoords);
}
