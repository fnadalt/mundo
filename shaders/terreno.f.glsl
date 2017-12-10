#version 120

varying vec4 vposmodelo;
varying vec4 vpos;
varying vec3 normal;
varying float interv;
varying float temp;

uniform struct {
    vec4 ambient;
} p3d_LightModel;

uniform struct {
    vec4 ambient;
    vec4 diffuse;
    vec4 emission;
    vec3 specular;
    float shininess;
    vec4 baseColor;
    float roughness;
    float metallic;
    float refractiveIndex;
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

uniform vec4 p3d_ClipPlane[2];

/*
        altitud_interv_a_t    altitud_tierra            altitud_interv_t_p  0
        altitud_pasto           altitud_interv_p_n    altitud_nieve         0
        altura_sobre_agua  0                              0                            0
        0                             0                              0                            0
*/
uniform mat3 data;

uniform sampler2D p3d_Texture0; // arena
uniform sampler2D p3d_Texture1; // tierra
uniform sampler2D p3d_Texture2; // pasto
uniform sampler2D p3d_Texture3; // nieve

vec4 diff_spec(int iLightSource)
{
    //
    vec3 s=normalize(p3d_LightSource[iLightSource].position.xyz-(vpos.xyz*p3d_LightSource[iLightSource].position.w));
    //vec3 v=normalize(-vpos.xyz);
    //vec3 r=normalize(-reflect(s, normal));
    //
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(normal,s),0),0,1);
    //vec4 specular=vec4(p3d_Material.specular,1.0) * p3d_LightSource[iLightSource].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    //
    vec4 ds=diffuse;//+specular;
    return ds;
}

vec4 texture_color(in float altitud)
{
    vec4 _color;
    //
    float altitud_corregida=altitud+(temp*data[2][0]);
    //
    if(altitud_corregida>data[1][2]){
        _color=texture2D(p3d_Texture3, gl_TexCoord[0].st);
    } else if(altitud_corregida>data[1][1]){
        if(interv<0.0){
            _color=texture2D(p3d_Texture3, gl_TexCoord[0].st);
        } else {
            _color=texture2D(p3d_Texture2, gl_TexCoord[0].st);
        }
    } else if(altitud_corregida>data[1][0]){
        _color=texture2D(p3d_Texture2, gl_TexCoord[0].st);
    } else if(altitud_corregida>data[0][2]){
        if(interv<0.0){
            _color=texture2D(p3d_Texture2, gl_TexCoord[0].st);
        } else {
            _color=texture2D(p3d_Texture1, gl_TexCoord[0].st);
        }
    } else if(altitud_corregida>data[0][1]){
        _color=texture2D(p3d_Texture1, gl_TexCoord[0].st);
    } else if(altitud_corregida>data[0][0]){
        if(interv<0.0){
            _color=texture2D(p3d_Texture1, gl_TexCoord[0].st);
        } else {
            _color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
        }
    } else {
        _color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    }
    //
    return _color;
}

void main()
{
    
    if(dot(p3d_ClipPlane[0],vpos)<0.0){
        gl_FragColor=vec4(1,1,1,1);
    }

    vec4 tex_color=texture_color(vposmodelo.z);
    
    vec4 diff_spec_sum=vec4(0,0,0,0);
    int cnt=p3d_LightSource.length();
    for(int i=0; i<cnt; ++i)
    {
        diff_spec_sum+=diff_spec(i);
    }

    vec4 componente_ambiental=normalize(p3d_LightModel.ambient)*p3d_Material.ambient;
    vec4 tex_color_ads=tex_color*(diff_spec_sum+componente_ambiental);
    
    tex_color_ads.a=1.0;
    gl_FragColor=tex_color_ads;
}
