#version 120

attribute vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_MultiTexCoord0; // generico, terreno, agua, sol
varying vec4 texcoord; // generico, terreno, agua, sol

attribute vec3 p3d_Normal;
uniform mat3 p3d_NormalMatrix;
varying vec3 Normal;

void main() {
    
    texcoord=p3d_MultiTexCoord0;
    
    Normal=p3d_NormalMatrix*p3d_Normal;

    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;

}
