#version 120

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute float intervalo;
attribute float temperatura;

attribute vec4 p3d_MultiTexCoord0;

varying vec4 vposmodelo;
varying vec4 vpos;
varying vec3 normal;
varying float interv;
varying float temp;

uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    gl_TexCoord[0]=p3d_MultiTexCoord0;

    vposmodelo=p3d_Vertex;
    vpos=p3d_ModelViewMatrix*vposmodelo;
    normal=normalize(p3d_NormalMatrix*p3d_Normal);
    
    interv=intervalo;
    temp=temperatura;
    
    gl_Position=p3d_ModelViewProjectionMatrix * vposmodelo;
}
