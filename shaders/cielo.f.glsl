#version 120

const float TamanoHalo=0.85;

uniform float altitud_agua;
uniform vec3 posicion_sol;
uniform int periodo;
uniform float offset_periodo;
uniform vec4 color_base_inicial;
uniform vec4 color_base_final;
uniform vec4 color_halo_inicial;
uniform vec4 color_halo_final;

uniform vec4 water_clipping;

varying vec4 pos_vertex;
varying vec4 wpos_vertex;

vec4 color_1()
{
    vec4 color_base=mix(color_base_inicial,color_base_final,offset_periodo);

    vec3 v=normalize(pos_vertex.xyz+vec3(0,0,100));
    vec3 l=normalize(posicion_sol);
    float a=(dot(v,l)+1.0)/2.0;
    
    vec4 color;
    if(abs(a)>TamanoHalo){
        vec4 color_halo=mix(color_halo_inicial,color_halo_final,offset_periodo);
        float factor=(abs(a)-TamanoHalo)/(1.0-TamanoHalo);
        color=mix(color_base,color_halo,factor);
    } else {
        color=color_base;
    }

    return color;
}

void main()
{
    if(water_clipping.z<0.0 && wpos_vertex.z<water_clipping.w){
        discard;
    } else {
        vec4 color=color_1();
        color.a=1.0;
        gl_FragColor=color;
    }
}
