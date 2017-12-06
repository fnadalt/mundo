#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_MultiTexCoord0;

void main() {
    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
    gl_TexCoord[0]=p3d_MultiTexCoord0;
}
