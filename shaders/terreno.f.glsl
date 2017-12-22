#version 130

varying vec4 vposmodelo;
varying vec4 vpos;
varying vec3 normal;
flat in float info_tipo;
smooth in float info_tipo_factor;

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

/*
        altitud_interv_a_t    altitud_tierra            altitud_interv_t_p  0
        altitud_pasto           altitud_interv_p_n    altitud_nieve         0
        altura_sobre_agua  AlturaMaxima           altitud_agua          0
        0                             0                              0                            0
*/
uniform mat3 data;

uniform vec4 water_clipping;

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
    vec4 _color0;
    vec4 _color1;
    //
    float tipo0=floor(info_tipo/10);
    float tipo1=mod(info_tipo,10);
    //
    if(tipo0==1){
        _color0=texture2D(p3d_Texture3, gl_TexCoord[0].st);
    } else if(tipo0==2){
        _color0=texture2D(p3d_Texture1, gl_TexCoord[0].st);
    } else if(tipo0==3){
        _color0=texture2D(p3d_Texture2, gl_TexCoord[0].st);
    } else if(tipo0==4){
        _color0=texture2D(p3d_Texture1, gl_TexCoord[0].st);
    } else if(tipo0==5){
        _color0=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    } else {
        _color0=vec4(0,0,0,1);
    }
    if(tipo1==1){
        _color1=texture2D(p3d_Texture3, gl_TexCoord[0].st);
    } else if(tipo1==2){
        _color1=texture2D(p3d_Texture1, gl_TexCoord[0].st);
    } else if(tipo1==3){
        _color1=texture2D(p3d_Texture2, gl_TexCoord[0].st);
    } else if(tipo1==4){
        _color1=texture2D(p3d_Texture1, gl_TexCoord[0].st);
    } else if(tipo1==5){
        _color1=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    } else {
        _color1=vec4(1,1,1,1);
    }
    //
    if(info_tipo_factor==0.0){
        _color=_color0;
    } else if(info_tipo_factor==1.0){
        _color=_color1;
    } else {
        _color=info_tipo_factor<0.5?_color0:_color1;
    }
    //
    _color.a=1.0;
    return _color;
}

void main()
{
    if((water_clipping.z>0 && vposmodelo.z<data[2][2]) || (water_clipping.z<0 && vposmodelo.z>data[2][2])){
        discard;
    } else {
    
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
}
