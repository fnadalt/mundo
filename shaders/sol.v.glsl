#version 120

attribute vec4 p3d_Vertex;
attribute vec4 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

varying vec4 wpos;

void main() {
    wpos=p3d_ModelMatrix*p3d_Vertex;
    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
    gl_TexCoord[0]=p3d_MultiTexCoord0;
}
