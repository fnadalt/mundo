#
#
# VERTEX SHADER
#
#
VS_MAIN_INICIO="""
void main() {
"""
VS_MAIN_COMUN="""
    PositionW=p3d_ModelMatrix*p3d_Vertex;
"""
VS_MAIN_VIEW="""
    PositionV=p3d_ModelViewMatrix*p3d_Vertex;
    Normal=normalize(p3d_NormalMatrix*p3d_Normal);
"""
VS_MAIN_SOMBRA="""
    for(int i=0;i<p3d_LightSource.length();++i){
        sombra[i]=p3d_LightSource[i].shadowViewMatrix * PositionV;
    }
"""
VS_MAIN_TEX="""
    texcoord=p3d_MultiTexCoord0;
"""
VS_MAIN_TIPO_TERRENO="""
    // terreno
    info_tipo=info_tipo_terreno;
    tangent=vec4(normalize(p3d_NormalMatrix*Tangent.xyz),Tangent.w);
"""
VS_MAIN_TERRENO_COLOR_DEBUG="""
    // terreno color debug
    color_vtx=Color;
"""
VS_MAIN_VERTEX="""
    Position=p3d_Vertex; // fog y cielo
"""
VS_MAIN_POSITION="""
    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
"""
VS_MAIN_VERTEX_PROJ="""
    PositionP=gl_Position; // agua
"""
VS_MAIN_FIN="""
}
"""

#
#
# FRAGMENT SHADER
#
#
FS_TEX_1="""
uniform sampler2D p3d_Texture1; // terreno y agua
"""
FS_TEX_2="""
uniform sampler2D p3d_Texture2; // terreno y agua
"""
FS_TEX_3="""
uniform sampler2D p3d_Texture3; // agua
"""
FS_FOG="""
uniform float distancia_fog_minima;
uniform float distancia_fog_maxima;
uniform vec4 tinte_fog;
"""
FS_AGUA="""
uniform float move_factor;
uniform vec3 cam_pos;
const float shine_damper=20.0;
const float reflectivity=0.6;
"""
FS_FUNC_TRANSFORM_LUZ_NORMAL_MAP_TERRENO="""
vec3 transform_luz_normal_map_terreno(vec3 vec_luz)
{
    vec3 binormal=cross(Normal,tangent.xyz)*tangent.w;
    mat3 M=mat3(tangent.x,binormal.x,Normal.x,
                tangent.y,binormal.y,Normal.y,
                tangent.z,binormal.z,Normal.z);
    return normalize(M*vec_luz);
}
"""
FS_FUNC_LUZ="""
// generico y terreno
vec4 amb()
{
    return color_luz_ambiental*p3d_Material.ambient;
}
vec4 ds(int iLightSource, vec3 normal)
{
    vec4 color;
    vec3 s=p3d_LightSource[iLightSource].position.xyz-(PositionV.xyz*p3d_LightSource[iLightSource].position.w);
    vec3 l=%(FUNC_LIGHT_VEC_TRANSFORM)s
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(normal,l),0),0,1);
    color=diffuse;
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-PositionV.xyz);
        vec3 r=normalize(-reflect(s, normal));
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
    %(FS_FUNC_LUZ_SOMBRA)s
    if(p3d_LightSource[iLightSource].position.w!=0.0){
        float distancia=length(s);
        float atenuacion=1.0/(p3d_LightSource[iLightSource].attenuation.x+p3d_LightSource[iLightSource].attenuation.y*distancia+p3d_LightSource[iLightSource].attenuation.z*distancia*distancia);
        color*=atenuacion;
    }
    return color;
}
"""
FS_FUNC_LUZ_SOMBRA="color*=shadow2DProj(p3d_LightSource[iLightSource].shadowMap, sombra[iLightSource]);"
FS_FUNC_TEX_GENERICO="""
// generico
vec4 tex_generico(){
    vec4 color_tex=vec4(0,0,0,0);
    color_tex+=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0, texcoord.st);
    return color_tex;
}
"""
FS_FUNC_TEX_AGUA="""
    color_tex+=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1, texcoord.st); // agua
    color_tex+=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture2, texcoord.st); // agua
    color_tex+=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture3, texcoord.st); // agua
"""
FS_FUNC_TEX_TERRENO="""
// terreno
vec2 obtener_texcoord_terreno(float tipo_terreno, bool normal_map)
{
    //
    const int escala=1; // deberia ser una constante externa
    vec2 texcoord=fract(PositionW.xy+vec2(tipo_terreno/7,tipo_terreno/11)/escala)/4.0;
    texcoord.s=clamp(texcoord.s,0.0005,0.9995); // pfpfpfpfpff!!!
    texcoord.t=clamp(texcoord.t,0.0005,0.9995); //
    //
    const float corte_terreno_superficie=0.49; // deberia ser una constante externa
    if(info_tipo.z<corte_terreno_superficie){
        if(tipo_terreno==2){
            tipo_terreno=1;
        } else if(tipo_terreno==3){
            tipo_terreno=5;
        } else if(tipo_terreno==4){
            tipo_terreno=6;
        }
    }
    //
    if(tipo_terreno==1){ // nieve
        texcoord+=vec2(0.00,0.75);
    } else if(tipo_terreno==2){ // tundra
        texcoord+=vec2(0.00,0.50);
    } else if(tipo_terreno==3){ // tierra seca
        texcoord+=vec2(0.00,0.25);
    } else if(tipo_terreno==4){ // tierra humeda
        texcoord+=vec2(0.00,0.00);
    } else if(tipo_terreno==5){ // pasto seco
        texcoord+=vec2(0.50,0.75);
    } else if(tipo_terreno==6){ // pasto humedo
        texcoord+=vec2(0.50,0.50);
    } else if(tipo_terreno==7){ // arena seca
        texcoord+=vec2(0.50,0.25);
    } else if(tipo_terreno==8){ // arena humeda
        texcoord+=vec2(0.50,0.00);
    }
    //
    if(normal_map) texcoord.s+=0.25;
    //
    return texcoord;
}
const float factor_piso=0.47;
const float factor_techo=0.51;
float calcular_factor(){
    float factor=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,texcoord.st).r;
    if(factor<factor_piso){
        factor=0.0;
    } else if(factor>factor_techo){
        factor=1.0;
    } else {
        factor=(factor-factor_piso)/(factor_techo-factor_piso);
    }
    return factor;
}
//uniform int osg_FrameNumber;
vec4 tex_terreno()
{
    //
    vec2 tc0=obtener_texcoord_terreno(info_tipo.x,false);
    vec2 tc1=obtener_texcoord_terreno(info_tipo.y,false);
    //
    vec4 _color;
    vec4 _color0=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0, tc0);
    vec4 _color1=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0, tc1);
    //
    float factor=calcular_factor();
    if(factor==0.0){
        _color=_color0;
    } else if(factor==1.0){
        _color=_color1;
    } else {
        _color=mix(_color0,_color1,factor);
    }
    //
    return _color;
}
"""
FS_FUNC_NORMAL_MAP_TERRENO="""
// normal map terreno
vec3 normal_map_terreno()
{
    //
    vec2 tc0=obtener_texcoord_terreno(info_tipo.x,true);
    vec2 tc1=obtener_texcoord_terreno(info_tipo.y,false);
    //
    vec3 normal;
    vec3 normal0=texture(p3d_Texture0,tc0).rgb*2.0-1.0;
    vec3 normal1=texture(p3d_Texture0,tc1).rgb*2.0-1.0;
    //
    float factor=calcular_factor();
    if(factor==0.0){
        normal=normal0;
    } else if(factor==1.0){
        normal=normal1;
    } else {
        normal=mix(normal0,normal1,factor);
    }
    //
    return normal;
}
"""
FS_FUNC_AGUA="""
// agua
vec4 agua()
{
    vec4 color=vec4(0,0,0,0);
    //
    vec2 ndc=(PositionP.xy/PositionP.w)/2.0+0.5;
    vec2 texcoord_reflejo=vec2(ndc.x,1.0-ndc.y);
    vec2 texcoord_refraccion=ndc;
    //
    vec2 distorted_texcoords=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture2,vec2(texcoord.s+move_factor, texcoord.t)).rg*0.1;
    distorted_texcoords=texcoord.st+vec2(distorted_texcoords.x,distorted_texcoords.y+move_factor);
    vec2 total_distortion=(%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture2,distorted_texcoords).rg*2.0-1.0)*0.01;
    //
    texcoord_reflejo+=total_distortion;
    texcoord_reflejo=clamp(texcoord_reflejo,0.001,0.999);
    texcoord_refraccion+=total_distortion;
    texcoord_refraccion=clamp(texcoord_refraccion,0.001,0.999);
    //
    vec4 color_reflection=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0, texcoord_reflejo);
    vec4 color_refraction=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1, texcoord_refraccion);
    // ok so far
    vec3 view_vector=normalize(cam_pos);
    float refractive_factor=dot(view_vector,vec3(0.0,0.0,1.0)); // abs()? esto era no más, parece
    refractive_factor=pow(refractive_factor,0.9); // renderiza negro ante ciertos desplazamientos de la superficie de agua, habria que corregir. abs()!
    //
    vec4 color_normal=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture3,distorted_texcoords*1.5);
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
"""
FS_FUNC_CIELO="""
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
"""
FS_FUNC_SOL="""
// sol
vec4 sol()
{
    if(distance(posicion_sol,PositionW.xyz)>20.0){
        return vec4(0,0,0,1);
    } else {
        vec4 color=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0, texcoord.st);
        return color;//*2*(color.a - 0.5);
    }
}
"""
FS_FUNC_SOMBRA="""
// sombra
vec4 sombra()
{
    vec4 color;
    vec4 posp=normalize(PositionP);
    float prof=(posp.z/posp.w)*0.5+0.5;
    color=vec4(prof,prof,prof,1.0);
    return color;
}
"""
FS_MAIN_INICIO="""
void main()
{
    vec4 color=vec4(0,0,0,0);
"""
FS_MAIN_CLIP_INICIO="""
    if (PositionW.x*plano_recorte_agua.x + PositionW.y*plano_recorte_agua.y + PositionW.z*plano_recorte_agua.z - plano_recorte_agua.w <= 0) {
        discard;
    } else {
"""
FS_MAIN_LUZ="""
        // luz: generico y terreno
        int cantidad_luces=p3d_LightSource.length();
        for(int i=0; i<cantidad_luces; ++i)
        {
            color+=ds(i,%(FUNC_NORMAL_SOURCE)s);
        }
        color+=amb();
"""
FS_MAIN_LUZ_BLANCA="color+=vec4(1.0,1.0,1.0,1.0);"
FS_MAIN_TEX_GENERICO="""
        // textura: generico
        vec4 color_tex=tex_generico();
        color*=color_tex;
"""
FS_MAIN_TEX_TERRENO="""
        // textura: terreno
        color*=tex_terreno();
"""
FS_MAIN_TEX_TERRENO_COLOR_DEBUG="""
        color=color_vtx; // terreno color debug
"""
FS_MAIN_AGUA="""
        // agua
        color=agua();
"""
FS_MAIN_SOL="""
        // sol
        color=sol();
"""
FS_MAIN_SOMBRA="""
        // sombra
        color=sombra();
"""
FS_MAIN_CIELO_FOG="""
        // cielo y fog
        vec4 color_cielo=cielo();
"""
FS_MAIN_FOG_FACTOR="""
        // fog: generico, terreno y agua
        float fog_factor=clamp((distancia_fog_maxima-abs(PositionV.z))/(distancia_fog_maxima-distancia_fog_minima),0.0,1.0);
"""
FS_MAIN_FOG_COLOR="""
        color=mix(color_cielo*tinte_fog,color,fog_factor);
"""
FS_MAIN_CIELO="""
        color=color_cielo;
"""
FS_MAIN_ALPHA="""
        color.a=1.0;
"""
FS_MAIN_ALPHA_TEX_GENERICO="""
        color.a=color_tex.a;
"""
FS_MAIN_ALPHA_AGUA="""
        color.a=1.0-fog_factor;
"""
FS_MAIN_COLOR="""
        gl_FragColor=color;
"""
FS_MAIN_CLIP_FIN="""
    }
"""
FS_MAIN_FIN="""
}
"""

#
#
# OTRO
#
#
FUNC_NORMAL_SOURCE_VTX="Normal"
FUNC_NORMAL_SOURCE_NORMAL_MAP_TERRENO="normal_map_terreno()"
FUNC_LIGHT_VEC_TRANSFORM_VTX="normalize(s);"
FUNC_LIGHT_VEC_TRANSFORM_NORMAL_MAP_TERRENO="transform_luz_normal_map_terreno(s);"
