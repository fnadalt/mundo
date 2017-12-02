#version 120

varying vec4 vposmodelo;
varying vec3 vpos;
varying vec3 normal;
varying float interv;

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

uniform mat3 intervalos_tipos_terreno;

uniform sampler2D p3d_Texture0; // arena
uniform sampler2D p3d_Texture1; // tierra
uniform sampler2D p3d_Texture2; // pasto
uniform sampler2D p3d_Texture3; // nieve

vec4 diff_spec(int iLightSource)
{
    //
    vec3 s=normalize(p3d_LightSource[iLightSource].position.xyz-(vpos*p3d_LightSource[iLightSource].position.w));
    //vec3 v=normalize(-vpos);
    //vec3 r=normalize(-reflect(s, normal));
    //
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(normal,s),0),0,1);
    //vec4 specular=vec4(p3d_Material.specular,1.0) * p3d_LightSource[iLightSource].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    //
    vec4 ds=diffuse;//+specular;
    return ds;
}

vec4 texture_color(in float altura)
{
    vec4 color;
    if(altura>intervalos_tipos_terreno[1][2]){
        color=texture2D(p3d_Texture3, gl_TexCoord[0].st);
    } else if(altura>intervalos_tipos_terreno[1][1]){
        if(interv<0.0){
            color=texture2D(p3d_Texture3, gl_TexCoord[0].st);
        } else {
            color=texture2D(p3d_Texture2, gl_TexCoord[0].st);
        }
    } else if(altura>intervalos_tipos_terreno[1][0]){
        color=texture2D(p3d_Texture2, gl_TexCoord[0].st);
    } else if(altura>intervalos_tipos_terreno[0][2]){
        if(interv<0.0){
            color=texture2D(p3d_Texture2, gl_TexCoord[0].st);
        } else {
            color=texture2D(p3d_Texture1, gl_TexCoord[0].st);
        }
    } else if(altura>intervalos_tipos_terreno[0][1]){
        color=texture2D(p3d_Texture1, gl_TexCoord[0].st);
    } else if(altura>intervalos_tipos_terreno[0][0]){
        if(interv<0.0){
            color=texture2D(p3d_Texture1, gl_TexCoord[0].st);
        } else {
            color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
        }
    } else {
        color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    }
    //
    return color;
}

void main()
{
    vec4 tex_color=texture_color(vposmodelo.z);
    
    vec4 diff_spec_sum=vec4(0,0,0,0);
    int cnt=p3d_LightSource.length();
    for(int i=0; i<cnt; ++i)
    {
        diff_spec_sum+=diff_spec(i);
    }
    //
    vec4 tex_color_ads=tex_color*(diff_spec_sum+p3d_Material.ambient*p3d_LightModel.ambient);
    
    gl_FragColor=tex_color_ads;
    gl_FragColor.a=1.0;
}
