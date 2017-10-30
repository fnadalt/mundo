#version 120

uniform sampler2D p3d_Texture0; // reflection
uniform sampler2D p3d_Texture1; // refraction
uniform sampler2D p3d_Texture2; // dudv
uniform sampler2D p3d_Texture3; // normal

varying vec4 vpos;
varying vec2 texcoords;

varying vec3 to_cam_vec;
varying vec3 from_light_vec;

uniform float move_factor;
uniform vec3 light_color;

const float shine_damper=20.0;
const float reflectivity=0.6;

void main()
{
    //
    vec2 ndc= ( vpos.xy / vpos.w ) / 2.0 + 0.5;
    vec2 texcoord_reflejo=vec2(ndc.x,1.0-ndc.y);
    vec2 texcoord_refraccion=ndc;

    //
    vec2 distorted_texcoords=texture2D(p3d_Texture2,vec2(texcoords.x+move_factor, texcoords.y)).rg*0.1;
    distorted_texcoords=texcoords+vec2(distorted_texcoords.x,distorted_texcoords.y+move_factor);
    vec2 total_distortion=(texture2D(p3d_Texture2,distorted_texcoords).rg*2.0-1.0)*0.01;
    
    //
    texcoord_reflejo+=total_distortion;
    texcoord_reflejo=clamp(texcoord_reflejo,0.001,0.999);
    texcoord_refraccion+=total_distortion;
    texcoord_refraccion=clamp(texcoord_refraccion,0.001,0.999);

    //
    vec4 color_reflection=texture2D(p3d_Texture0, texcoord_reflejo);
    vec4 color_refraction=texture2D(p3d_Texture1, texcoord_refraccion);
    
    //
    vec3 view_vector=normalize(to_cam_vec);
    float refractive_factor=abs(dot(view_vector,vec3(0.0,1.0,0.0))); // abs()? esto era no más, parece
    refractive_factor=pow(refractive_factor,0.9); // renderiza negro ante ciertos desplazamientos de la superficie de agua, habria que corregir. abs()!
    
    //
    vec4 color_normal=texture2D(p3d_Texture3,distorted_texcoords);
    vec3 normal=vec3(color_normal.r*2.0-1.0,color_normal.g,color_normal.b*2.0-1.0);
    normal=normalize(normal);
    
    //
    vec3 reflected_light=reflect(normalize(from_light_vec),normal);
    float specular=max(dot(reflected_light,view_vector), 0.0);
    specular=pow(specular,shine_damper);
    vec3 specular_highlights=light_color * specular * reflectivity;
    
    //
    vec4 color=mix(color_reflection,color_refraction,refractive_factor);
    color=mix(color, vec4(0.0,0.3,0.5,1.0),0.2) + vec4(specular_highlights,0.0);
    
    //
    gl_FragColor=color;
    //gl_FragColor=color_reflection;
}
