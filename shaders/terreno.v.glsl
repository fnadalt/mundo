#version 120

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Normal;
attribute vec4 p3d_MultiTexCoord0; // arena
attribute vec4 p3d_MultiTexCoord1; // tierra
attribute vec4 p3d_MultiTexCoord2; // pasto
attribute vec4 p3d_MultiTexCoord3; // nieve
uniform mat4 p3d_ModelViewProjectionMatrix;

varying float altitud;
varying float angulo_normal;

void main() {

    altitud=p3d_Vertex.z;
    angulo_normal=dot(p3d_Normal.xyz,vec3(0.0,1.0,0.0));

    gl_Position=p3d_ModelViewProjectionMatrix * p3d_Vertex;

    gl_TexCoord[0]=p3d_MultiTexCoord0*128.0;
    gl_TexCoord[1]=p3d_MultiTexCoord1*4.0;
    gl_TexCoord[2]=p3d_MultiTexCoord2*64.0;
    gl_TexCoord[3]=p3d_MultiTexCoord3*16.0;
}
