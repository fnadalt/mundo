#version 120

uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute vec4 p3d_MultiTexCoord0; // arena
attribute vec4 p3d_MultiTexCoord1; // tierra
attribute vec4 p3d_MultiTexCoord2; // pasto
attribute vec4 p3d_MultiTexCoord3; // nieve

uniform vec3 pos_sol;
uniform vec4 color_sol;
uniform mat4 M;

varying float altitud;
varying float angulo_normal;
varying vec3 normal;
varying vec4 posicion;
varying vec4 posicion_sol;
varying vec4 color;

void main2()
{
    gl_Position=p3d_ModelViewProjectionMatrix * p3d_Vertex;
    normal=normalize(p3d_NormalMatrix*gl_Normal);
    vec3 light_v=normalize(p3d_NormalMatrix*vec3(0.0,0.0,1.0));
    float nxDir=max(0.0,dot(normal,light_v));
    color=color_sol*nxDir;
}

void main() {
    altitud=p3d_Vertex.z;
    angulo_normal=dot(p3d_Normal,vec3(0.0,1.0,0.0));

    gl_TexCoord[0]=p3d_MultiTexCoord0*128.0;
    gl_TexCoord[1]=p3d_MultiTexCoord1*4.0;
    gl_TexCoord[2]=p3d_MultiTexCoord2*64.0;
    gl_TexCoord[3]=p3d_MultiTexCoord3*16.0;

    normal=normalize(vec4(transpose(M) * vec4(p3d_Normal,0.0)).xyz);
    posicion=p3d_ModelViewMatrix * p3d_Vertex;
    posicion_sol=vec4(pos_sol,1.0);
    gl_Position=p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
