#version 330 core

in vec3 position;
out vec3 tex_coords;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    mat4 pv = projection * view;
    // homogeneous coordinates should project the skybox to infinity - so we set the w component to 0
    // 0 did not work, so we set it to 0.1
    pv[3] = vec4(0, 0, 0, 0.1);
    gl_Position = pv * vec4(position, 1);
    tex_coords = position;// skybox is centered at the camera, so we can use the vertex position as the tex coords
}
