#version 120
// comun
attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

attribute vec4 p3d_MultiTexCoord0; // generico, terreno, agua, sol

varying vec4 Position; // cielo

varying vec4 PositionV; // luz, fog
varying vec3 Normal;

uniform mat4 p3d_ModelMatrix;
varying vec4 PositionW; // clip

varying vec4 PositionP; // agua

// terreno
attribute float info_tipo_terreno;
varying float info_tipo;
varying float info_tipo_factor;

void main() {
    Position=p3d_Vertex; // cielo
    PositionV=p3d_ModelViewMatrix*p3d_Vertex;
    PositionW=p3d_ModelMatrix*p3d_Vertex;
    Normal=normalize(p3d_NormalMatrix*p3d_Normal);
    gl_TexCoord[0]=p3d_MultiTexCoord0;

    // terreno
    info_tipo=floor(info_tipo_terreno);
    info_tipo_factor=fract(info_tipo_terreno);

    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
    PositionP=gl_Position; // agua
}
