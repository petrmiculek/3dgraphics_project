#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_tex_coords; // x,y
out vec4 out_color;

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d;

// ambient light
uniform vec3 k_a;

// specular light
uniform vec3 k_s;

// shininess
uniform float s;

// world camera position
uniform vec3 w_camera_position;

// own variables
float tmp;

in vec3 w_position, w_normal;   // in world coodinates

in float distance;


void main() {
    vec3 fog = vec3(0.5, 0.5, 0.7);
    // texture mapping
    vec4 tex = texture(diffuse_map, frag_tex_coords);

    // shading
    vec3 n = normalize(w_normal); // world normal normalized
    vec3 l = normalize(light_dir); // world light direction normalized

    vec3 diffusion = tex.xyz * max(0, dot(n, -l));

    vec3 view = normalize(w_camera_position - w_position); // normalize the vector, not the positions

    vec3 reflected3 = reflect(l, n);
    // dot(r, v)
    float dot_rv = max(0, dot(reflected3, view));

    // ks * dot(r, v)^s
    vec3 specular = k_s * pow(dot_rv, s);

    out_color = vec4(k_a + diffusion + specular, 0);

    // linearly blend color with fog color
    float fog_threshold = 200;
    // fog intensity scales linearly 0 to 1 with distance 0 to 200, capped at 1
    float fog_intensity = min(1, distance / fog_threshold);
    out_color = mix(out_color, vec4(fog, 0), fog_intensity);

    // enable if you want only the textures without shading
//    out_color = tex;

//    out_color = vec4(w_normal, 0);
    // enable for normals visualization

}
