#version 120

uniform sampler2D p3d_Texture0; // arena
uniform sampler2D p3d_Texture1; // tierra
uniform sampler2D p3d_Texture2; // pasto
uniform sampler2D p3d_Texture3; // nieve

uniform vec3 posicion_sol;
uniform vec4 color_sol;
uniform vec4 color_ambiente;

varying vec3 normal;

void main()
{
    // difuso
    vec4 color_arena=texture2D(p3d_Texture0, gl_TexCoord[0].st);    

    // sol
    vec3 vector_sol=normalize(posicion_sol);
    float angulo_luz=max(0.0, dot(normal,vector_sol));
    //angulo_luz=1.0;
    
    gl_FragColor=color_arena * angulo_luz;
}
