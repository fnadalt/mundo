#version 120

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;

attribute vec4 p3d_MultiTexCoord0; // arena
attribute vec4 p3d_MultiTexCoord1; // tierra
attribute vec4 p3d_MultiTexCoord2; // pasto
attribute vec4 p3d_MultiTexCoord3; // nieve

varying vec3 vpos;
varying vec3 normal;

uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    gl_TexCoord[0]=p3d_MultiTexCoord0;
    gl_TexCoord[1]=p3d_MultiTexCoord1;
    gl_TexCoord[2]=p3d_MultiTexCoord2;
    gl_TexCoord[3]=p3d_MultiTexCoord3;
    
    normal=normalize(p3d_NormalMatrix*p3d_Normal);
    vpos=vec3(p3d_ModelViewMatrix*p3d_Vertex);
    
    gl_Position=p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
