#version 120

attribute vec4 p3d_Vertex;
attribute vec4 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;

varying vec4 vpos;
varying vec2 texcoords;

void main() {
  vpos = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  gl_Position=vpos;
  gl_TexCoord[0] = p3d_MultiTexCoord0;
  texcoords = vec2(p3d_Vertex.x/2.0+0.5, p3d_Vertex.y/2.0+0.5);
}
