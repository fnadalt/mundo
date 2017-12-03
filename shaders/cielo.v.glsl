#version 120

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;

varying vec4 vpos;

void main() {
    vpos=p3d_Vertex;
    gl_Position=p3d_ModelViewProjectionMatrix*vpos;
}
