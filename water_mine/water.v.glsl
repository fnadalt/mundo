#version 120

attribute vec4 p3d_Vertex;
attribute vec4 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;

varying vec4 vpos;

void main() {
  vpos = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  gl_Position=vpos;
  gl_TexCoord[0] = p3d_MultiTexCoord0;
}
