#version 120

const vec4 ColorNoche=vec4(0.0, 0.0, 0.2, 1.0);
const vec4 ColorAmanecer=vec4(0.95, 0.75, 0.2, 1.0);
const vec4 ColorDia=vec4(0.9, 1.0, 1.0, 1.0);
const vec4 ColorAtardecer=vec4(0.95, 0.65, 0.3, 1.0);

uniform vec3 posicion_sol;

varying vec4 vpos;

vec4 color_2()
{
    vec3 v=normalize(vpos.xyz);
    vec3 l=normalize(posicion_sol);
    float a=(dot(v,l)+1.0)/2.0;
    vec4 color=mix(ColorNoche,ColorDia,a);
    return color;
}

void main()
{
    vec4 color_final=color_2();
    color_final.a=1.0;
    gl_FragColor=color_final;
}
