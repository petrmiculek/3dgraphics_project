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

in vec3 w_position, w_normal;   // in world coodinates

in float distance;

// colors
vec4 rock = vec4(0.3, 0.25, 0.20, 1);
vec3 fog = vec3(0.5, 0.5, 0.7);

void main() {
    /*
    ======================================
    mostly the same as texture_phong.frag
    ======================================
    */

    // texture mapping
    vec4 tex = texture(diffuse_map, frag_tex_coords);

    float rock_min = 4;
    if (w_position.y > rock_min) {
        float ratio = (w_position.y - rock_min) / 10;
        tex = tex * (1 - ratio) + rock * ratio;
    }

    // shading
    vec3 n = normalize(w_normal); // world normal normalized
    vec3 l = normalize(light_dir); // world light direction normalized

    vec3 diffusion = tex.xyz * max(0, dot(n, -l));
    vec3 view = normalize(w_camera_position - w_position); // normalize the vector, not the positions
    vec3 reflected3 = reflect(l, n);
    // dot(r, v)
    float dot_rv = max(0, dot(reflected3, view));
    // Fresnel effect
    // = fix for black areas
    float fresnel = pow(1.0 - dot_rv, 5.0);
    float mix_fresnel = 0.01; // any nonzero value behaves just the same
//        dot_rv = mix(dot_rv, fresnel, mix_fresnel);
    dot_rv = dot_rv * (1 - mix_fresnel) + fresnel * (mix_fresnel);

    // ks * dot(r, v)^s
    vec3 specular = k_s * pow(dot_rv, s);

    out_color = vec4(diffusion + specular, 1);  // + k_a * tex.xyz
    //    /*
    // linearly blend color with fog color
    //    /*
    float fog_min = 50;
    float fog_max = 100;
    float disappearing_threshold = 150;
    // fog
    float fog_intensity = min(1, max((distance - fog_min) / (fog_max - fog_min), 0));
    out_color = mix(out_color, vec4(fog, 1), fog_intensity);
    // render distance
    float disappearing_factor = min(max(distance - fog_max, 0.0) / 10.0, 1);
    out_color.a = 1 - disappearing_factor;

    // enable if you want only the textures without shading
    //    out_color = tex;

    // out_color = vec4(w_normal, 1);
    // enable for normals visualization
    //    */
}
