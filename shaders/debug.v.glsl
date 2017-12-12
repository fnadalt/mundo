#version 120

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
//attribute vec4 p3d_MultiTexCoord0;

varying vec4 vpos;

void main() {
    vpos=p3d_ModelViewMatrix*p3d_Vertex;
    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
    //gl_TexCoord[0]=p3d_MultiTexCoord0;
}
