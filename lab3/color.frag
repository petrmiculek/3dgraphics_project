#version 330 core

// receiving interpolated color for fragment shader
in vec3 fragment_color;

// output fragment color for OpenGL
out vec4 out_color;

uniform float alpha;

void main() {
    out_color = vec4(fragment_color, alpha);
//    if (alpha < 0.2) {
//        out_color.x = 1.0;
//        out_color.a = 1.0;
//    }
}
