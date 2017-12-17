#version 120

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute float info_tipo_terreno;

attribute vec4 p3d_MultiTexCoord0;

varying vec4 vposmodelo;
varying vec4 vpos;
varying vec3 normal;
varying float info_tipo;

uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    gl_TexCoord[0]=p3d_MultiTexCoord0;

    vposmodelo=p3d_Vertex;
    vpos=p3d_ModelViewMatrix*vposmodelo;
    normal=normalize(p3d_NormalMatrix*p3d_Normal);
    
    info_tipo=info_tipo_terreno;
    
    gl_Position=p3d_ModelViewProjectionMatrix * vposmodelo;
}
