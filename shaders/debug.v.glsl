#version 120

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewMatrixInverse;
uniform mat4 p3d_ModelViewProjectionMatrix;

uniform vec4 p3d_ClipPlane[1];

attribute vec4 p3d_Vertex;
//attribute vec4 p3d_MultiTexCoord0;

varying vec4 vpos;
varying vec4 vpos_inv;
varying vec4 clipo;

void main() {
    vpos=p3d_ModelViewMatrix*p3d_Vertex;
    vpos_inv=p3d_ModelViewMatrix*vec4(p3d_Vertex.x,p3d_Vertex.y,-p3d_Vertex.z,p3d_Vertex.w);
    clipo=p3d_ModelViewMatrixInverse*p3d_ClipPlane[0];
    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
    //gl_TexCoord[0]=p3d_MultiTexCoord0;
}
