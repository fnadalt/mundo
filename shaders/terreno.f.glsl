#version 120

varying vec3 normal;
varying vec3 vpos;

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
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
} p3d_LightSource[8];

uniform sampler2D p3d_Texture0; // arena
uniform sampler2D p3d_Texture1; // tierra
uniform sampler2D p3d_Texture2; // pasto
uniform sampler2D p3d_Texture3; // nieve

vec4 phong(int iLightSource)
{
    vec3 s=normalize(p3d_LightSource[iLightSource].position.xyz-(vpos*p3d_LightSource[iLightSource].position.w));
    vec3 v=normalize(-vpos);
    vec3 r=normalize(-reflect(s, normal));
    //
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(normal,s),0),0,1);
    vec4 specular=vec4(p3d_Material.specular,1.0) * p3d_LightSource[iLightSource].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    //
    return diffuse+specular;
}

void main()
{
    gl_FragColor=p3d_LightModel.ambient * p3d_Material.ambient;
    
    for(int i=0; i<8; ++i)
    {
        gl_FragColor+=phong(i);
    }
    
    gl_FragColor.a=1.0;
}
