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
VS_MAIN_NORMAL_MAP="""
    tangent=vec4(normalize(p3d_NormalMatrix*p3d_Tangent.xyz),p3d_Tangent.w);
"""
VS_MAIN_TIPO_TERRENO="""
    // terreno
    info_tipo=info_tipo_terreno;
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
uniform sampler2D p3d_Texture1; // normal map generico, terreno y agua
"""
FS_TEX_2="""
uniform sampler2D p3d_Texture2; // agua, y terreno?
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
FS_FUNC_TRANSFORM_LUZ_NORMAL_MAP="""
vec3 transform_luz_normal_map(vec3 vec_luz)
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
vec4 ds_generico(int iLightSource, vec3 normal)
{
    vec4 color;
    vec3 s=p3d_LightSource[iLightSource].position.xyz-(PositionV.xyz*p3d_LightSource[iLightSource].position.w);
    vec3 l=%(FUNC_LIGHT_VEC_TRANSFORM)s
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
    %(FS_FUNC_LUZ_SOMBRA)s
    if(p3d_LightSource[iLightSource].position.w!=0.0){
        float distancia=length(s);
        float atenuacion=1.0/(p3d_LightSource[iLightSource].attenuation.x+p3d_LightSource[iLightSource].attenuation.y*distancia+p3d_LightSource[iLightSource].attenuation.z*distancia*distancia);
        color*=atenuacion;
    }
    return color;
}
vec4 ds_puntual(int i_luz_puntual, vec3 normal)
{
    vec4 color;
    vec4 luz_p_v=luz_puntual[i_luz_puntual].position;
    vec3 s=luz_p_v.xyz-PositionV.xyz;
    vec3 l=%(FUNC_LIGHT_VEC_TRANSFORM)s
    vec4 diffuse=clamp(p3d_Material.diffuse*luz_puntual[i_luz_puntual].diffuse*max(dot(normal,l),0),0,1);
    color=diffuse;
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-PositionV.xyz);
        vec3 r=normalize(-reflect(l, normal));
        color+=vec4(p3d_Material.specular,1.0) * luz_puntual[i_luz_puntual].specular * pow(max(dot(r,v),0),p3d_Material.shininess);
    }
    if(luz_puntual[i_luz_puntual].attenuation!=vec3(0,0,0)){
        float distancia=length(s);
        float atenuacion=1.0/(luz_puntual[i_luz_puntual].attenuation.x+luz_puntual[i_luz_puntual].attenuation.y*distancia+luz_puntual[i_luz_puntual].attenuation.z*distancia*distancia);
        color*=atenuacion;
    }
    return color;
}
"""
FS_FUNC_LUZ_SOMBRA="color*=shadow2DProj(p3d_LightSource[iLightSource].shadowMap, sombra[iLightSource]);"
FS_FUNC_TEX_GENERICO="""
// generico
vec4 tex_generico(sampler2D textura){
    vec4 color_tex=vec4(0,0,0,0);
    color_tex+=%(FS_FUNC_TEX_LOOK_UP)s(textura, texcoord.st);
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
struct TiposTerreno 
{
    int base;
    int superficie;
};
const TiposTerreno tipos_terreno[12]=TiposTerreno[](TiposTerreno(2,2),TiposTerreno(2,3),TiposTerreno(7,7),TiposTerreno(7,7),
                                                    TiposTerreno(2,1),TiposTerreno(3,1),TiposTerreno(3,5),TiposTerreno(3,5),
                                                    TiposTerreno(2,1),TiposTerreno(4,6),TiposTerreno(4,6),TiposTerreno(4,6)
                                                    ); 
vec2 obtener_texcoord_terreno(float tipo_terreno, bool normal_map)
{
    //
    const int escala=2; // deberia ser una constante externa
    vec2 _texcoord=fract(PositionW.xy/escala)/4.0;
    _texcoord.s=clamp(_texcoord.s,0.0005,0.9995); // pfpfpfpfpff!!!
    _texcoord.t=clamp(_texcoord.t,0.0005,0.9995); //
    //
    if(tipo_terreno==1){ // nieve
        _texcoord+=vec2(0.00,0.75);
    } else if(tipo_terreno==2){ // tundra
        _texcoord+=vec2(0.00,0.50);
    } else if(tipo_terreno==3){ // tierra seca
        _texcoord+=vec2(0.00,0.25);
    } else if(tipo_terreno==4){ // tierra humeda
        _texcoord+=vec2(0.00,0.00);
    } else if(tipo_terreno==5){ // pasto seco
        _texcoord+=vec2(0.50,0.75);
    } else if(tipo_terreno==6){ // pasto humedo
        _texcoord+=vec2(0.50,0.50);
    } else if(tipo_terreno==7){ // arena seca
        _texcoord+=vec2(0.50,0.25);
    } else if(tipo_terreno==8){ // arena humeda
        _texcoord+=vec2(0.50,0.00);
    }
    //
    if(normal_map) _texcoord.s+=0.25;
    //
    return _texcoord;
}
/*
vec4 tex_terreno_0()
{
    //
    vec2 pos=vec2(info_tipo.x*4,info_tipo.y*3);
    vec2 celda0=vec2(int(pos.x),int(pos.y));
    vec2 punto_medio0=vec2(celda0.x+0.5,celda0.y+0.5);
    vec2 distancia0=pos-punto_medio0;
    ivec2 delta_celda0=ivec2((distancia0.x<0?-1:1),(distancia0.y<0?-1:1));
    vec2 celda1;
    float distancia;
    float factor_transicion=0.0;
    if(abs(distancia0.x)>abs(distancia0.y)){
        celda1=vec2(clamp(celda0.x+delta_celda0.x,0,3),celda0.y);
        distancia=abs(distancia0.x);
    } else {
        celda1=vec2(celda0.y,clamp(celda0.y+delta_celda0.y,0,2));
        distancia=abs(distancia0.y);
    }
    //
    TiposTerreno tipos0=tipos_terreno[int(celda0.y*4+celda0.x)];
    float tipo0=tipos0.base;
    //
    vec4 color0=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipo0,false));
    //
    vec4 color=color0;
    //
    if(distancia>0.3){
        TiposTerreno tipos1=tipos_terreno[int(celda1.y*4+celda1.x)];
        float tipo1=tipos1.base;
        vec4 color1=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipo1,false));
        factor_transicion=(distancia-0.3)/((0.5-0.3)*2.0);
        color=mix(color0,color1,factor_transicion);
    }
    //
    return color;
}
*/
vec4 tex_terreno(bool normal_map)
{
    //
    vec2 pos=vec2(((info_tipo.x-0.2)/0.8)*3,info_tipo.y*2);
    //vec2 pos=fract(Position.xy/32);
    //pos.x=((pos.x-0.2)/0.8)*3;
    //pos.y*=2;
    vec2 entero=vec2(int(pos.x),int(pos.y));
    vec2 fracc=vec2(fract(pos.x),fract(pos.y));
    vec2 fracc_rnd=vec2(round(fracc.x),round(fracc.y));
    vec2 idx_tabla_0=vec2(entero.x+fracc_rnd.x,entero.y+fracc_rnd.y);
    vec2 idx_tabla_1=idx_tabla_0;
    vec2 distancias=vec2(fracc_rnd.x-fracc.x,fracc_rnd.y-fracc.y);
    float distancia;
    if(abs(distancias.x)>abs(distancias.y)){
        float fracc_rnd_op=(int(fracc_rnd.x)+1)%%2;
        idx_tabla_1.x=entero.x+fracc_rnd_op;
        distancia=abs(distancias.x);
    } else {
        float fracc_rnd_op=(int(fracc_rnd.y)+1)%%2;
        idx_tabla_1.y=entero.y+fracc_rnd_op;
        distancia=abs(distancias.y);
    }
    //
    float factor_ruido=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,vec2(texcoord.s,-texcoord.t)).r;
    //
    vec4 color0;
    //
    TiposTerreno tipos0=tipos_terreno[int(idx_tabla_0.y*4+idx_tabla_0.x)];
    float f0=clamp(0.2+distancia-(factor_ruido*2.0-1.0),0.0,1.0);
    if(f0<0.40){
        color0=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos0.base,normal_map));
    } else if(f0>0.50){
        color0=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos0.superficie,normal_map));
    } else {
        f0=(f0-0.40)/(0.50-0.40);
        vec4 color00=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos0.base,normal_map));
        vec4 color01=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos0.superficie,normal_map));
        color0=mix(color00,color01,f0);
    }
    //
    vec4 color=color0;
    //color=vec4(1,0,0,1);
    //
    if(distancia>0.45){
        //
        TiposTerreno tipos1=tipos_terreno[int(idx_tabla_1.y*4+idx_tabla_1.x)];
        float f1=clamp(0.2+distancia-(factor_ruido*2.0-1.0),0.0,1.0);
        vec4 color1;
        if(f1<0.40){
            color1=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos1.base,normal_map));
        } else if(f1>0.50){
            color1=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos1.superficie,normal_map));
        } else {
            f1=(f1-0.40)/(0.50-0.40);
            vec4 color10=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos1.base,normal_map));
            vec4 color11=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture0,obtener_texcoord_terreno(tipos1.superficie,normal_map));
            color1=mix(color10,color11,f1);
        }
        //
        float factor_transicion=(distancia-0.45)/((0.50-0.45)*2.0);
        factor_transicion=clamp((factor_transicion+factor_ruido*2.0-1.0),0.0,1.0);
        if(factor_transicion<0.45){
            color=color0;
        } else if(factor_transicion>0.50) {
            color=color1;
        } else {
            color=mix(color0,color1,((factor_transicion-0.45)/(0.50-0.45)));
        }
        //color=(color0*(1.0-factor_transicion))+(color1*factor_transicion);
    }
    //
    //color=vec4(factor_ruido,factor_ruido,factor_ruido,1.0);
    //if(f0==-1) color=vec4(1,0,0,1);
    return color;
}
"""
FS_FUNC_NORMAL_MAP_TERRENO="""
// normal map terreno
/*vec3 normal_map_terreno()
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
}*/
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
    vec2 tc=texcoord.st*75.0;
    vec2 distorted_texcoords=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture2,vec2(tc.s+move_factor, tc.t)).rg*0.1;
    distorted_texcoords=tc.st+vec2(distorted_texcoords.x,distorted_texcoords.y+move_factor);
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
    vec3 view_vector=normalize(cam_pos-PositionV.xyz);
    float refractive_factor=dot(view_vector,vec3(0.0,0.0,1.0)); // abs()? esto era no más, parece
    refractive_factor=pow(abs(refractive_factor),0.9); // renderiza negro ante ciertos desplazamientos de la superficie de agua, habria que corregir. abs()!
    //
    vec4 color_normal=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture3,distorted_texcoords*1.5);
    vec3 normal=vec3(color_normal.r*2.0-1.0,color_normal.g*2.0-1.0,color_normal.b);
    normal=normalize(normal);
    //
    //vec3 reflected_light=reflect(normalize(posicion_sol-PositionW.xyz),normal);
    vec3 s=normalize(posicion_sol-PositionW.xyz);
    vec3 reflected_light=(2.0*dot(s,normal)*normal)-s;
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
        int cantidad_luces_genericas=p3d_LightSource.length();
        vec3 _normal=%(FUNC_NORMAL_SOURCE)s;
        for(int i=0; i<cantidad_luces_genericas; ++i)
        {
            if(p3d_LightSource[i].color.a!=0.0)
            {
                color+=ds_generico(i,_normal);
            }
        }
        int cantidad_luces_puntuales=luz_puntual.length();
        for(int i=0; i<cantidad_luces_puntuales; ++i)
        {
            if(luz_puntual[i].color.a!=0.0)
            {
                color+=ds_puntual(i,_normal);
            }
        }
        color+=amb();
"""
FS_MAIN_LUZ_SOMBRA="""
        float factor_sombra=shadow2DProj(textura_sombra_0, sombra_0).r; // 120: shadow2DProj?
        color*=factor_sombra>0.0?factor_sombra:1.0;
"""
FS_MAIN_LUZ_BLANCA="color+=vec4(1.0,1.0,1.0,1.0);"
FS_MAIN_TEX_GENERICO="""
        // textura: generico
        vec4 color_tex=tex_generico(p3d_Texture0);
        color*=color_tex;
"""
FS_MAIN_TEX_TERRENO="""
        // textura: terreno
        color*=tex_terreno(false);
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
FS_MAIN_PROF_AGUA="""
        if(PositionW.z<altitud_agua){
            float altitud_oscuridad=altitud_agua-7.5;
            color*=pow(max(PositionW.z-altitud_oscuridad,0.0)/(altitud_agua-altitud_oscuridad),2); // pow(), caro?
        }
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
FUNC_NORMAL_SOURCE_NORMAL_MAP_GENERICO="(tex_generico(p3d_Texture1).rgb*2.0-1.0)"
FUNC_NORMAL_SOURCE_NORMAL_MAP_TERRENO="(tex_terreno(true).rgb*2.0-1.0)"
FUNC_LIGHT_VEC_TRANSFORM_VTX="normalize(s);"
FUNC_LIGHT_VEC_TRANSFORM_NORMAL_MAP="transform_luz_normal_map(s);"
