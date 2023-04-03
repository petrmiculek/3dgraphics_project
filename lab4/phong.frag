#version 330 core

// fragment position and normal of the fragment, in WORLD coordinates
// (you can also compute in VIEW coordinates, your choice! rename variables)
in vec3 w_position, w_normal;   // in world coodinates

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

// output fragment color for OpenGL
out vec4 out_color;

void main() {
    // print k_a
    // out_color = vec4(k_a, 1);


    // TODO: compute Lambert illumination
    // == Kd * dot(n, l)
    // where n is the normal 
    // l is the light direction 
    // Kd is the diffuse material property=color

    // normal was denormalized in the vertex shader
    vec3 n = normalize(w_normal); // world normal normalized
    vec3 l = normalize(light_dir); // world light direction normalized

    // out_color = vec4(w_normal, 1);

    // without clamping
    // tmp = dot(n, light_dir);  // surprisingly, nothing breaks 
    
    // imo not necessary
    // vec4 n4 = vec4(n, 0); // zero for normal, because we do not want to apply translations, we only want the rotation
    // vec4 l4 = vec4(light_dir, 0);
    // tmp = max(0, dot(n4, l4));  

    vec3 diffusion = k_d * max(0, dot(n, -l));

    vec3 view = normalize(w_camera_position - w_position); // normalize the vector, not the positions

    vec3 reflected3 = reflect(l, n);  
    // reflect expects the light vector as incident (coming to the point)

    // dot(r, v)
    float dot_rv = max(0, dot(reflected3, view));

    // ks * dot(r, v)^s
    vec3 specular = k_s * pow(dot_rv, s);
    
    out_color = vec4(diffusion + k_a + specular, 0);

    // make sure you're using a material that has all of the light components ready in the .mtl
    // (and the object you're showing is using this material)
}
