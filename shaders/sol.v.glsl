#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_MultiTexCoord0;

varying vec4 wpos;
varying vec4 vpos;

void main() {
    wpos=p3d_ModelMatrix*p3d_Vertex;
    vpos=p3d_ModelViewProjectionMatrix*p3d_Vertex;
    gl_Position=vpos;
    gl_TexCoord[0]=p3d_MultiTexCoord0;
}
