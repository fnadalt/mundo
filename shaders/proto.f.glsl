#version 120
uniform sampler2D p3d_Texture0; // !cielo
uniform sampler2D p3d_Texture1; // terreno y agua
uniform sampler2D p3d_Texture2; // terreno y agua
uniform sampler2D p3d_Texture3; // terreno y agua

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

// comun
uniform float altitud_agua;
uniform vec3 posicion_sol;
uniform vec4 plano_recorte_agua;
uniform vec3 pos_pivot_camara;
uniform float offset_periodo_cielo;
uniform vec4 color_cielo_base_inicial;
uniform vec4 color_cielo_base_final;
uniform vec4 color_halo_sol_inicial;
uniform vec4 color_halo_sol_final;
// fog
const float FogMin=50.0; // den ser uniforms para poder modificarse
const float FogMax=100.0;
// agregar uniform vec4 tinte_fog; // color scale
// quitar, usar tinte: uniform vec4 color_fog;

const float TamanoHalo=0.85;
varying vec4 Position; // cielo
varying vec4 PositionV; // !cielo
varying vec3 Normal; // !cielo
varying vec4 PositionW; // clip
varying vec4 PositionP; // agua

// terreno
varying float info_tipo;
varying float info_tipo_factor;

// generico y terreno
vec4 amb()
{
    return p3d_LightModel.ambient*p3d_Material.ambient;
}
vec4 ds_generico(int iLightSource)
{
    vec3 s=p3d_LightSource[iLightSource].position.xyz-(PositionV.xyz*p3d_LightSource[iLightSource].position.w);
    vec3 l=normalize(s);
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(Normal,l),0),0,1);
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-PositionV.xyz);
        vec3 r=normalize(-reflect(s, Normal));
        diffuse+=vec4(p3d_Material.specular,1.0) * p3d_LightSource[iLightSource].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    }
    if(p3d_LightSource[iLightSource].spotDirection!=vec3(0,0,0)){
        float spotEffect = dot(normalize(p3d_LightSource[iLightSource].spotDirection), -l);
        if(spotEffect>p3d_LightSource[iLightSource].spotCosCutoff){
            diffuse*=pow(spotEffect, p3d_LightSource[iLightSource].spotExponent);
            //diffuse*=textureProj(p3d_LightSource[iLightSource].shadowMap, shad[i]);
            diffuse/=dot(p3d_LightSource[iLightSource].attenuation, vec3(1, length(s), length(s) * length(s)));
        } else {
            diffuse=vec4(0,0,0,0);
        }
    }
    return diffuse;
}

// generico, terreno y agua
vec4 tex_generico(){
    vec4 color_tex=vec4(0,0,0,0);
    color_tex+=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    color_tex+=texture2D(p3d_Texture1, gl_TexCoord[0].st); // terreno y agua
    color_tex+=texture2D(p3d_Texture2, gl_TexCoord[0].st); // terreno y agua
    color_tex+=texture2D(p3d_Texture3, gl_TexCoord[0].st); // terreno y agua
    return color_tex;
}

// terreno
vec4 tex_terreno()
{
    vec4 _color;
    vec4 _color0;
    vec4 _color1;
    //
    float tipo0=floor(info_tipo/10);
    float tipo1=mod(floor(info_tipo),10);
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

// agua
vec4 agua()
{
    vec4 color=vec4(0,0,0,0);
    //
    vec2 ndc=(PositionP.xy/PositionP.w)/2.0+0.5;
    vec2 texcoord_reflejo=vec2(ndc.x,1.0-ndc.y);
    vec2 texcoord_refraccion=ndc;
    //
    vec2 distorted_texcoords=texture2D(p3d_Texture2,vec2(gl_TexCoord[0].s+factor_movimiento_agua, gl_TexCoord[0].t)).rg*0.1;
    distorted_texcoords=gl_TexCoord[0].st+vec2(distorted_texcoords.x,distorted_texcoords.y+factor_movimiento_agua);
    vec2 total_distortion=(texture2D(p3d_Texture2,distorted_texcoords).rg*2.0-1.0)*0.01;
    //
    texcoord_reflejo+=total_distortion;
    texcoord_reflejo=clamp(texcoord_reflejo,0.001,0.999);
    texcoord_refraccion+=total_distortion;
    texcoord_refraccion=clamp(texcoord_refraccion,0.001,0.999);
    //
    vec4 color_reflection=texture2D(p3d_Texture0, texcoord_reflejo);
    vec4 color_refraction=texture2D(p3d_Texture1, texcoord_refraccion);
    // ok so far
    vec3 view_vector=normalize(posicion_camara);
    float refractive_factor=dot(view_vector,vec3(0.0,0.0,1.0)); // abs()? esto era no más, parece
    refractive_factor=pow(refractive_factor,0.9); // renderiza negro ante ciertos desplazamientos de la superficie de agua, habria que corregir. abs()!
    //
    vec4 color_normal=texture2D(p3d_Texture3,distorted_texcoords*1.5);
    vec3 normal=vec3(color_normal.r*2.0-1.0,color_normal.g*2.0-1.0,color_normal.b);
    normal=normalize(normal);
    //
    vec3 reflected_light=reflect(normalize(PositionW.xyz-posicion_sol),normal);
    float specular=max(dot(reflected_light,view_vector), 0.0);
    specular=pow(specular,shine_damper);
    vec3 specular_highlights=vec4(1,1,1,1).rgb * specular * reflectivity;
    //
    color=mix(color_reflection,color_refraction,refractive_factor);
    color=mix(color, vec4(0.0,0.3,0.5,1.0),0.2) + vec4(specular_highlights,0.0);
    //
    return color;
}

// cielo y fog
vec4 cielo()
{
    vec4 color_base=mix(color_cielo_base_inicial,color_cielo_base_final,offset_periodo);
    vec3 d=normalize(posicion_sol-pos_pivot_camara);
    vec3 v=normalize(Position.xyz);
    float a=(dot(v,d)+1.0)/2.0;
    vec4 color;
    if(abs(a)>TamanoHalo){
        vec4 color_halo=mix(color_halo_sol_inicial,color_halo_sol_final,offset_periodo);
        float factor=(abs(a)-TamanoHalo)/(1.0-TamanoHalo);
        color=mix(color_base,color_halo,factor);
    } else {
        color=color_base;
    }
    color.a=1.0;
    return color;
}

// sol
vec4 sol()
{
    if(distance(posicion_sol,PositionW.xyz)>20.0){
        return vec4(0,0,0,1);
    } else {
        vec4 color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
        return color;//*2*(color.a - 0.5);
    }
}

void main()
{
    
    if (PositionW.x*plano_recorte_agua.x + PositionW.y*plano_recorte_agua.y + PositionW.z*plano_recorte_agua.z - plano_recorte_agua.w <= 0) {
        discard;
    } else {
        vec4 color=vec4(0,0,0,0);

        // luz: generico y terreno
        int cantidad_luces=p3d_LightSource.length();
        for(int i=0; i<cantidad_luces; ++i)
        {
            color+=ds_generico(i);
        }
        color+=amb();
        
        // textura: generico
        color*=tex_generico();
        
        // textura: terreno
        color*=tex_terreno();
        
        // agua
        color=agua();
        
        // cielo y fog
        vec4 color_cielo=cielo();
        
        // sol
        color=sol();
        
        // fog: generico, terreno y agua
        float fog_factor=clamp((FogMax-abs(PositionV.z))/(FogMax-FogMin),0.0,1.0);
        color=mix(color_cielo*tinte_fog,color,fog_factor);

        //
        color.a=1.0;
        gl_FragColor=color;
    
    }

}
