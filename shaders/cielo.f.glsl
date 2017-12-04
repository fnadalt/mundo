#version 120

const int TamanoHalo=0.5;

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

    vec3 v=normalize(vpos.xyz);
    vec3 l=normalize(posicion_sol);
    float a=(dot(v,l)+1.0)/2.0;
    
    if(abs(a))<TamanoHalo){
    } else {
    }

    vec4 color=color_base;
    
    return color;
}

void main()
{
    vec4 color=color_2();
    color.a=1.0;
    gl_FragColor=color;
}
