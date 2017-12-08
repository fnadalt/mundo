#version 120

//uniform sampler2D p3d_Texture0;

uniform struct {
    vec4 ambient;
} p3d_LightModel;

uniform struct {
    vec4 ambient;
    vec4 diffuse;
    vec4 emission;
    vec3 specular;
    float shininess;
} p3d_Material;

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
    //sampler2DShadow shadowMap;
    //mat4 shadowViewMatrix;
} p3d_LightSource[8];

void main()
{
    //vec4 tex_color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    gl_FragColor=p3d_LightModel.ambient*p3d_Material.ambient;
}
