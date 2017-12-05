#version 120

const float TamanoHalo=0.99;

uniform vec3 posicion_sol;
uniform int periodo;
uniform float offset_periodo;
uniform vec4 color_base_inicial;
uniform vec4 color_base_final;
uniform vec4 color_halo_inicial;
uniform vec4 color_halo_final;

varying vec4 vpos;

vec4 color_2()
{
    vec4 color_base=mix(color_base_inicial,color_base_final,offset_periodo);

    vec3 v=normalize(vpos.xyz+vec3(0,0,175));
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
    vec4 color=color_2();
    color.a=1.0;
    gl_FragColor=color;
}
