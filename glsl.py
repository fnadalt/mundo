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
FS_TEX_23="""
uniform sampler2D p3d_Texture2; // agua
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
FS_FUNC_LUZ="""
// generico y terreno
vec4 amb()
{
    return color_luz_ambiental*p3d_Material.ambient;
}
vec4 ds(int iLightSource)
{
    vec4 color;
    vec3 s=p3d_LightSource[iLightSource].position.xyz-(PositionV.xyz*p3d_LightSource[iLightSource].position.w);
    vec3 l=normalize(s);
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(Normal,l),0),0,1);
    color=diffuse;
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-PositionV.xyz);
        vec3 r=normalize(-reflect(s, Normal));
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
// ruido
/*const int tamano_textura=512;
float ruido()
{
    float value=0.0;
    vec2 pos=texcoord.xy*tamano_textura*0.5;
    int pasos=4;
    float persistencia=0.85;
    float amplitud=1.0;
    float amplitud_total=0.0;
    for(int i_paso=pasos;pasos>0;--pasos){
        amplitud*=persistencia;
        amplitud_total+=amplitud;
        int periodo=1; //1<<(i_paso+4);
        for(int i_mult=1;i_mult<=i_paso;++i_mult){periodo*=(2*i_mult);}
        //
        float offset_x=pos.x/periodo;
        int indice_x0=int(mod(int(offset_x)*periodo,tamano_textura));
        offset_x=fract(offset_x);
        float offset_y=pos.y/periodo;
        int indice_y0=int(mod(int(offset_y)*periodo,tamano_textura));
        offset_y=fract(offset_y);
        int indice_x1=int(mod(indice_x0+periodo,tamano_textura));
        int indice_y1=int(mod(indice_y0+periodo,tamano_textura));
        float c00=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,vec2(indice_x0,indice_y0)/tamano_textura).r;
        float c10=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,vec2(indice_x1,indice_y0)/tamano_textura).r;
        float c01=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,vec2(indice_x0,indice_y1)/tamano_textura).r;
        float c11=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,vec2(indice_x1,indice_y1)/tamano_textura).r;
        float interp_x0=mix(c00,c10,offset_x);
        float interp_x1=mix(c01,c11,offset_x);
        float interp_y=mix(interp_x0,interp_x1,offset_y);
        value+=interp_y*amplitud;
    }
    //value/=amplitud_total;
    return value;
}*/
// terreno
//uniform int osg_FrameNumber;
vec4 tex_terreno()
{
    vec4 _color;
    vec4 _color0;
    vec4 _color1;
    //
    int tipo0=int(info_tipo.x); //floor(info_tipo/10);
    int tipo1=int(info_tipo.y); //mod(floor(info_tipo),10);
    float info_tipo_factor=info_tipo.z; //fract(info_tipo);
    int escala=8.0;
    vec2 tc=fract(PositionW.xy/escala)/4.0;
    //
    if(tipo0==1){ // nieve
        _color0=texture(p3d_Texture0, tc+vec2(0.00,0.75));
    } else if(tipo0==2){ // tundra
        _color0=texture(p3d_Texture0, tc+vec2(0.00,0.50));
    } else if(tipo0==3){ // tierra seca
        _color0=texture(p3d_Texture0, tc+vec2(0.00,0.25));
    } else if(tipo0==4){ // tierra humeda
        _color0=texture(p3d_Texture0, tc+vec2(0.00,0.00));
    } else if(tipo0==7){ // arena seca
        _color0=texture(p3d_Texture0, tc+vec2(0.50,0.25));
    } else {
        _color0=vec4(0,0,0,1);
    }
    if(tipo1==1){
        _color1=texture(p3d_Texture0, tc+vec2(0.00,0.75));
    } else if(tipo1==2){
        _color1=texture(p3d_Texture0, tc+vec2(0.00,0.50));
    } else if(tipo1==3){
        _color1=texture(p3d_Texture0, tc+vec2(0.00,0.25));
    } else if(tipo1==4){
        _color1=texture(p3d_Texture0, tc+vec2(0.00,0.00));
    } else if(tipo1==7){
        _color1=texture(p3d_Texture0, tc+vec2(0.50,0.25));
    } else {
        _color1=vec4(1,1,1,1);
    }
    //
    if(info_tipo_factor==0.0){
        _color=_color0;
    } else {
        float _ruido=%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,texcoord.st).r;
        //float mix_factor=0.5+0.5*cos(3.14159*osg_FrameNumber*0.003);
        _color=mix(_color0,_color1,_ruido>info_tipo_factor?1.0:0.0);
        //_color=_color0;
    }
    //_color=vec4(%(FS_FUNC_TEX_LOOK_UP)s(p3d_Texture1,texcoord.st).rgb,1.0);
    //
    //_color.a=1.0;
    return _color;
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
            color+=ds(i);
        }
        color+=amb();
"""
FS_MAIN_TEX_GENERICO="""
        // textura: generico
        vec4 color_tex=tex_generico();
        color*=color_tex;
"""
FS_MAIN_TEX_TERRENO="""
        // textura: terreno
        color*=tex_terreno();
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
