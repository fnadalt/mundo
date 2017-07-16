#version 130

in vec4 p3d_Vertex;
in vec4 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  gl_TexCoord[0] = p3d_MultiTexCoord0;
}
