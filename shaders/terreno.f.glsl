#version 120

uniform sampler2D p3d_Texture0; // arena
uniform sampler2D p3d_Texture1; // tierra
uniform sampler2D p3d_Texture2; // pasto
uniform sampler2D p3d_Texture3; // nieve

uniform vec3 intensidad_sol;

uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float brillo;

varying float altitud;
varying float angulo_normal;
varying vec3 normal;
varying vec3 posicion;
varying vec3 posicion_sol;

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

void ads(out vec3 color)
{
    vec3 n = normalize( normal );
    vec3 s = normalize( posicion_sol - posicion);
    vec3 v = normalize(vec3(-posicion));
    vec3 r = reflect( -s, n );
    color=intensidad_sol * ( Ka + Kd * max( dot(s, n), 0.0 ));// + Ks * pow( max( dot(r,v), 0.0 ), brillo ) );
}


void main()
{
    //
    //vec4 color_tex;
    //obtener_color_tex(color_tex);
    
    //
    //vec3 color_ads;
    //ads(color_ads);
    
    //
    vec3 color_debug=normal;
    
    //
    gl_FragColor=vec4(color_debug, 1.0);
}
