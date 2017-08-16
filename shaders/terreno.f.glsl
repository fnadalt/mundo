#version 120

uniform sampler2D p3d_Texture0; // arena
uniform sampler2D p3d_Texture1; // tierra
uniform sampler2D p3d_Texture2; // pasto
uniform sampler2D p3d_Texture3; // nieve

uniform vec3 intensidad_sol;

varying float altitud;
varying float angulo_normal;
varying vec3 normal;
varying vec4 posicion;
varying vec4 posicion_sol;
varying vec4 color;

void obtener_color_tex(out vec4 color)
{
    vec4 difuso=vec4(0.0,0.0,0.0,0.0);
    vec4 color_arena=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    vec4 color_tierra=texture2D(p3d_Texture1, gl_TexCoord[1].st);
    vec4 color_pasto=texture2D(p3d_Texture2, gl_TexCoord[2].st);
    vec4 color_nieve=texture2D(p3d_Texture3, gl_TexCoord[3].st);
    if(altitud>0.6){
        difuso=color_nieve;
    } else if(altitud>0.46){
        difuso=color_pasto;
    } else if(altitud>0.42){
        difuso=color_tierra;
    } else {
        difuso=color_arena;
    }
    color=difuso;
}

void main()
{
    //
    vec4 color_tex;
    obtener_color_tex(color_tex);
    
    //
    vec3 light_v=posicion_sol.xyz-posicion.xyz;
    vec3 color_debug=max(dot(normalize(light_v),normalize(normal)),0.0) * vec3(1,1,1);
    
    //
    gl_FragColor=vec4(color_debug, 1.0);
}
