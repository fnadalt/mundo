#version 130

const float TamanoHalo=0.85;
in vec4 PositionW; // clip
// comun
uniform float altitud_agua;
uniform vec3 posicion_sol;
uniform vec4 plano_recorte_agua;
uniform vec3 pos_pivot_camara;
uniform vec4 color_luz_ambiental;
uniform float offset_periodo_cielo;
uniform vec4 color_cielo_base_inicial;
uniform vec4 color_cielo_base_final;
uniform vec4 color_halo_sol_inicial;
uniform vec4 color_halo_sol_final;

in vec4 Position; // cielo

uniform sampler2D p3d_Texture0; // !cielo
in vec4 texcoord;

in vec4 PositionV; // luz, fog
in vec3 Normal;
uniform mat4 p3d_ModelViewMatrix; // sin uso?

/*uniform struct {
    vec4 ambient;
} p3d_LightModel;*/
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
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
}  p3d_LightSource[4];

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
    samplerCube shadowMap;
    mat4 shadowViewMatrix;
}  luz_omni[4];
in vec4 sombra[4];

// generico y terreno
vec4 amb()
{
    return color_luz_ambiental*p3d_Material.ambient;
}
vec4 ds_generico(int iLightSource, vec3 normal)
{
    vec4 color;
    vec3 s=p3d_LightSource[iLightSource].position.xyz-(PositionV.xyz*p3d_LightSource[iLightSource].position.w);
    vec3 l=normalize(s);
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(normal,l),0),0,1);
    color=diffuse;
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-PositionV.xyz);
        vec3 r=normalize(-reflect(l, normal)); //(2.0*dot(s, normal)*normal-s)
        color+=vec4(p3d_Material.specular,1.0) * p3d_LightSource[iLightSource].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    }
    if(p3d_LightSource[iLightSource].spotCosCutoff>0.0){
        float spotEffect = dot(normalize(p3d_LightSource[iLightSource].spotDirection), -l);
        if(spotEffect>p3d_LightSource[iLightSource].spotCosCutoff){
            color*=pow(spotEffect, p3d_LightSource[iLightSource].spotExponent);
        } else {
            color=vec4(0,0,0,0);
        }
    }
    
    if(p3d_LightSource[iLightSource].position.w!=0.0){
        float distancia=length(s);
        float atenuacion=1.0/(p3d_LightSource[iLightSource].attenuation.x+p3d_LightSource[iLightSource].attenuation.y*distancia+p3d_LightSource[iLightSource].attenuation.z*distancia*distancia);
        color*=atenuacion;
    }
    return color;
}
vec4 ds_puntual(int i_luz_omni, vec3 normal)
{
    vec4 color;
    vec4 luz_p_v=luz_omni[i_luz_omni].position;
    vec3 s=luz_p_v.xyz-PositionV.xyz;
    vec3 l=normalize(s);
    vec4 diffuse=clamp(p3d_Material.diffuse*luz_omni[i_luz_omni].diffuse*max(dot(normal,l),0),0,1);
    color=diffuse;
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-PositionV.xyz);
        vec3 r=normalize(-reflect(l, normal));
        color+=vec4(p3d_Material.specular,1.0) * luz_omni[i_luz_omni].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    }
    if(luz_omni[i_luz_omni].attenuation!=vec3(0,0,0)){
        float distancia=length(s);
        float atenuacion=1.0/(luz_omni[i_luz_omni].attenuation.x+luz_omni[i_luz_omni].attenuation.y*distancia+luz_omni[i_luz_omni].attenuation.z*distancia*distancia);
        color*=atenuacion;
    }
    return color;
}

// generico
vec4 tex_generico(sampler2D textura){
    vec4 color_tex=vec4(0,0,0,0);
    color_tex+=texture(textura, texcoord.st);
    return color_tex;
}

uniform float distancia_fog_minima;
uniform float distancia_fog_maxima;
uniform vec4 tinte_fog;

// cielo y fog
vec4 cielo()
{
    vec4 color_base=mix(color_cielo_base_inicial,color_cielo_base_final,offset_periodo_cielo);
    vec3 d=normalize(posicion_sol-pos_pivot_camara);
    vec3 v=normalize(Position.xyz);
    float a=(dot(v,d)+1.0)/2.0;
    vec4 color;
    if(abs(a)>TamanoHalo){
        vec4 color_halo=mix(color_halo_sol_inicial,color_halo_sol_final,offset_periodo_cielo);
        float factor=(abs(a)-TamanoHalo)/(1.0-TamanoHalo);
        color=mix(color_base,color_halo,factor);
    } else {
        color=color_base;
    }
    color.a=1.0;
    return color;
}

void main()
{
    vec4 color=vec4(0,0,0,0);

    if (PositionW.x*plano_recorte_agua.x + PositionW.y*plano_recorte_agua.y + PositionW.z*plano_recorte_agua.z - plano_recorte_agua.w <= 0) {
        discard;
    } else {

        // cielo y fog
        vec4 color_cielo=cielo();

        // luz: generico y terreno
        int cantidad_luces_genericas=p3d_LightSource.length();
        vec3 _normal=Normal;
        for(int i=0; i<cantidad_luces_genericas; ++i)
        {
            if(p3d_LightSource[i].color.a!=0.0)
            {
                color+=ds_generico(i,_normal);
            }
        }
        int cantidad_luces_puntuales=luz_omni.length();
        for(int i=0; i<cantidad_luces_puntuales; ++i)
        {
            if(luz_omni[i].color.a!=0.0)
            {
                color+=ds_puntual(i,_normal);
            }
        }
        color+=amb();

        // textura: generico
        vec4 color_tex=tex_generico(p3d_Texture0);
        color*=color_tex;

        // fog: generico, terreno y agua
        float fog_factor=clamp((distancia_fog_maxima-abs(PositionV.z))/(distancia_fog_maxima-distancia_fog_minima),0.0,1.0);

        color=mix(color_cielo*tinte_fog,color,fog_factor);

        if(PositionW.z<altitud_agua){
            float altitud_oscuridad=altitud_agua-7.5;
            color*=pow(max(PositionW.z-altitud_oscuridad,0.0)/(altitud_agua-altitud_oscuridad),2); // pow(), caro?
        }

        color.a=color_tex.a;

        gl_FragColor=color;

    }

}
