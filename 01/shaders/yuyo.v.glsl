#version 130

in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
out vec4 PositionW; // clip

in vec4 p3d_MultiTexCoord0; // generico, terreno, agua, sol
out vec4 texcoord; // generico, terreno, agua, sol

in vec3 p3d_Normal;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
out vec4 PositionV; // luz, fog
out vec3 Normal;


uniform struct {
    vec4 color;
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    vec4 position;
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;
    vec3 attenuation;
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
}  p3d_LightSource[4];
out vec4 sombra[4];

out vec4 Position; // fog y cielo

void main() {

    PositionW=p3d_ModelMatrix*p3d_Vertex;

    texcoord=p3d_MultiTexCoord0;

    PositionV=p3d_ModelViewMatrix*p3d_Vertex;
    Normal=normalize(p3d_NormalMatrix*p3d_Normal);

    for(int i=0;i<p3d_LightSource.length();++i){
        sombra[i]=p3d_LightSource[i].shadowViewMatrix * PositionV;
    }

    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;

    Position=p3d_Vertex; // fog y cielo

}
