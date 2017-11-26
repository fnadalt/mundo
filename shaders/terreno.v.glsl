#version 120

uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute vec4 p3d_MultiTexCoord0; // arena
attribute vec4 p3d_MultiTexCoord1; // tierra
attribute vec4 p3d_MultiTexCoord2; // pasto
attribute vec4 p3d_MultiTexCoord3; // nieve

varying vec3 normal;

void main()
{
    gl_TexCoord[0]=p3d_MultiTexCoord0*1.0;
    normal=normalize(p3d_Normal);
    gl_Position=p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
