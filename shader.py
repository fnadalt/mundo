from panda3d.core import *

import os, os.path

import logging
log=logging.getLogger(__name__)

# globales
shaders=dict() # {tipo:shader,...}
_altitud_agua=None
_plano_recorte_agua=Vec4(0, 0, 1, 0)
_plano_recorte_agua_inv=Vec4(0, 0, -1, 0)

class GeneradorShader:

    Version="120"

    # clases
    ClaseNulo="nulo"
    ClaseGenerico="generico"
    ClaseTerreno="terreno"
    ClaseAgua="agua"
    ClaseCielo="cielo"
    ClaseSol="sol"
    ClaseSombra="sombra"

    @staticmethod
    def iniciar(altitud_agua, plano_recorte_agua):
        global _altitud_agua, _plano_recorte_agua, _plano_recorte_agua_inv
        if _altitud_agua!=None:
            log.warning("GeneradorShader ya iniciado")
            return
        _altitud_agua=altitud_agua
        _plano_recorte_agua=plano_recorte_agua
        _plano_recorte_agua_inv=Vec4(-_plano_recorte_agua[0], -_plano_recorte_agua[1], -_plano_recorte_agua[2], -_altitud_agua)

    @staticmethod
    def aplicar(nodo, tipo, prioridad):
        #
        if _altitud_agua==None:
            raise Exception("GeneradorShader: no se especifico _altitud_agua")
        #
        global shaders
        shader=None
        if not tipo in shaders:
            log.info("cargar shader tipo %s"%tipo)
            generador=GeneradorShader(tipo)
            generador.nodo=nodo
            generador.prioridad=prioridad
            shader=generador.generar()
            shaders[tipo]=shader
        shader=shaders[tipo]
        nodo.setShader(shader, prioridad)
        #
        nodo.setShader(shader, priority=prioridad)
        nodo.setShaderInput("posicion_sol", Vec3(0, 0, 0), priority=prioridad)
        nodo.setShaderInput("pos_pivot_camara", Vec3(0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_luz_ambiental", Vec4(1, 1, 0.93, 1.0), priority=prioridad)
        nodo.setShaderInput("offset_periodo_cielo", 0.0, priority=prioridad)
        nodo.setShaderInput("color_cielo_base_inicial", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_cielo_base_final", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_halo_sol_inicial", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_halo_sol_final", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("plano_recorte_agua", _plano_recorte_agua, priority=prioridad)
        nodo.setShaderInput("distancia_fog_minima", 70.0, priority=prioridad)
        nodo.setShaderInput("distancia_fog_maxima", 120.0, priority=prioridad)
        nodo.setShaderInput("tinte_fog", Vec4(1, 1, 1, 1), priority=prioridad)

    def __init__(self, clase):
        # referencias:
        self.nodo=None
        # variables externas:
        self.prioridad=0
        # variables internas:
        self._clase=clase

    def generar(self):
        # texto
        texto_vs="#version %s\n"%GeneradorShader.Version
        texto_fs="#version %s\n"%GeneradorShader.Version
        # vs
        texto_vs+=VS_COMUN
        if self._clase!=GeneradorShader.ClaseCielo:
            texto_vs+=VS_TEX
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                texto_vs+=VS_POS_VIEW
                texto_vs+=VS_SOMBRA
            if self._clase==GeneradorShader.ClaseAgua or self._clase==GeneradorShader.ClaseSombra:
                texto_vs+=VS_POS_PROJ
            elif self._clase==GeneradorShader.ClaseTerreno:
                texto_vs+=VS_TIPO_TERRENO
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_vs+=VS_POS_MODELO
        texto_vs+=VS_MAIN_INICIO
        texto_vs+=VS_MAIN_COMUN
        if self._clase!=GeneradorShader.ClaseCielo:
            texto_vs+=VS_MAIN_TEX
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                texto_vs+=VS_MAIN_VIEW
                texto_vs+=VS_MAIN_SOMBRA
            if self._clase==GeneradorShader.ClaseTerreno:
                texto_vs+=VS_MAIN_TIPO_TERRENO
        texto_vs+=VS_MAIN_POSITION
        if self._clase==GeneradorShader.ClaseAgua or self._clase==GeneradorShader.ClaseSombra:
            texto_vs+=VS_MAIN_VERTEX_PROJ
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_vs+=VS_MAIN_VERTEX
        texto_vs+=VS_MAIN_FIN
        # fs
        texto_fs+=FS_COMUN
        if self._clase!=GeneradorShader.ClaseCielo:
            if self._clase!=GeneradorShader.ClaseSombra:
                texto_fs+=FS_TEX_0
                texto_fs+=FS_POS_VIEW
            if self._clase==GeneradorShader.ClaseTerreno:
                texto_fs+=FS_TERRENO
            if self._clase==GeneradorShader.ClaseAgua:
                texto_fs+=FS_TEX_123
                texto_fs+=FS_POS_PROJ
                texto_fs+=FS_AGUA
                texto_fs+=FS_FUNC_AGUA
            if self._clase==GeneradorShader.ClaseSombra:
                texto_fs+=FS_POS_PROJ
            if self._clase==GeneradorShader.ClaseTerreno or self._clase==GeneradorShader.ClaseGenerico:
                texto_fs+=FS_LUZ
                texto_fs+=FS_FUNC_LUZ
                if self._clase==GeneradorShader.ClaseTerreno:
                    texto_fs+=FS_FUNC_TEX_TERRENO
                else:
                    texto_fs+=FS_FUNC_TEX_GENERICO
            elif self._clase==GeneradorShader.ClaseSol:
                texto_fs+=FS_FUNC_SOL
            elif self._clase==GeneradorShader.ClaseSombra:
                texto_fs+=FS_FUNC_SOMBRA
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                texto_fs+=FS_FOG
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_fs+=FS_POS_MODELO
            texto_fs+=FS_FUNC_CIELO
        texto_fs+=FS_MAIN_INICIO
        if self._clase!=GeneradorShader.ClaseAgua and self._clase!=GeneradorShader.ClaseCielo:
            texto_fs+=FS_MAIN_CLIP_INICIO
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_fs+=FS_MAIN_CIELO_FOG
        if self._clase==GeneradorShader.ClaseCielo:
            texto_fs+=FS_MAIN_CIELO
        else:
            if self._clase==GeneradorShader.ClaseGenerico or self._clase==GeneradorShader.ClaseTerreno:
                texto_fs+=FS_MAIN_LUZ
                if self._clase==GeneradorShader.ClaseGenerico:
                    texto_fs+=FS_MAIN_TEX_GENERICO
                else: # terreno
                    texto_fs+=FS_MAIN_TEX_TERRENO
            elif self._clase==GeneradorShader.ClaseAgua:
                texto_fs+=FS_MAIN_AGUA
            elif self._clase==GeneradorShader.ClaseSol:
                texto_fs+=FS_MAIN_SOL
            elif self._clase==GeneradorShader.ClaseSombra:
                texto_fs+=FS_MAIN_SOMBRA
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                texto_fs+=FS_MAIN_FOG_FACTOR
            if self._clase==GeneradorShader.ClaseAgua:
                texto_fs+=FS_MAIN_ALPHA_AGUA
            else:
                if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                    texto_fs+=FS_MAIN_FOG_COLOR
                if self._clase==GeneradorShader.ClaseGenerico:
                    texto_fs+=FS_MAIN_ALPHA_TEX_GENERICO
                else:
                    texto_fs+=FS_MAIN_ALPHA
        texto_fs+=FS_MAIN_COLOR
        if self._clase!=GeneradorShader.ClaseAgua and self._clase!=GeneradorShader.ClaseCielo:
            texto_fs+=FS_MAIN_CLIP_FIN
        texto_fs+=FS_MAIN_FIN
        # archivos
        ruta_archivo_vs="shaders/vs.%s.glsl"%self._clase
        ruta_archivo_fs="shaders/fs.%s.glsl"%self._clase
        #
        if not os.path.exists(ruta_archivo_vs):
            log.info("generando archivo shader %s..."%ruta_archivo_vs)
            with open(ruta_archivo_vs, "w+") as arch_vs:
                arch_vs.write(texto_vs)
        if not os.path.exists(ruta_archivo_fs):
            log.info("generando archivo shader %s..."%ruta_archivo_fs)
            with open(ruta_archivo_fs, "w+") as arch_fs:
                arch_fs.write(texto_fs)
        # shader
        shader=Shader.load(Shader.SL_GLSL, vertex=ruta_archivo_vs, fragment=ruta_archivo_fs)
        return shader

#
#
# VERTEX SHADER
#
#
VS_COMUN="""
attribute vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
varying vec4 PositionW; // clip
"""
VS_TEX="""
attribute vec4 p3d_MultiTexCoord0; // generico, terreno, agua, sol
"""
VS_POS_MODELO="""
varying vec4 Position; // fog y cielo
"""
VS_POS_VIEW="""
attribute vec3 p3d_Normal;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
varying vec4 PositionV; // luz, fog
varying vec3 Normal;
"""
VS_SOMBRA="""
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
varying vec4 sombra[8];
"""
VS_POS_PROJ="""
varying vec4 PositionP; // agua
"""
VS_TIPO_TERRENO="""
attribute float info_tipo_terreno;
varying float info_tipo;
varying float info_tipo_factor;
"""
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
    gl_TexCoord[0]=p3d_MultiTexCoord0;
"""
VS_MAIN_TIPO_TERRENO="""
    // terreno
    info_tipo=floor(info_tipo_terreno);
    info_tipo_factor=fract(info_tipo_terreno);
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
FS_COMUN="""
const float TamanoHalo=0.85;
varying vec4 PositionW; // clip
// comun
uniform vec3 posicion_sol;
uniform vec4 plano_recorte_agua;
uniform vec3 pos_pivot_camara;
uniform vec4 color_luz_ambiental;
uniform float offset_periodo_cielo;
uniform vec4 color_cielo_base_inicial;
uniform vec4 color_cielo_base_final;
uniform vec4 color_halo_sol_inicial;
uniform vec4 color_halo_sol_final;
"""
FS_TEX_0="""
uniform sampler2D p3d_Texture0; // !cielo
"""
FS_TEX_123="""
uniform sampler2D p3d_Texture1; // agua
uniform sampler2D p3d_Texture2; // agua
uniform sampler2D p3d_Texture3; // agua
"""
FS_POS_MODELO="""
varying vec4 Position; // cielo
"""
FS_POS_VIEW="""
varying vec4 PositionV; // luz, fog
varying vec3 Normal;
"""
FS_POS_PROJ="""
varying vec4 PositionP; // agua
"""
FS_FOG="""
uniform float distancia_fog_minima;
uniform float distancia_fog_maxima;
uniform vec4 tinte_fog;
"""
FS_LUZ="""
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
} p3d_LightSource[8];
varying vec4 sombra[8];
"""
FS_AGUA="""
uniform float move_factor;
uniform vec3 cam_pos;
const float shine_damper=20.0;
const float reflectivity=0.6;
"""
FS_TERRENO="""
varying float info_tipo;
varying float info_tipo_factor;
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
    color*=shadow2DProj(p3d_LightSource[iLightSource].shadowMap, sombra[iLightSource]);
    if(p3d_LightSource[iLightSource].position.w!=0.0){
        float distancia=length(s);
        float atenuacion=1.0/(p3d_LightSource[iLightSource].attenuation.x+p3d_LightSource[iLightSource].attenuation.y*distancia+p3d_LightSource[iLightSource].attenuation.z*distancia*distancia);
        color*=atenuacion;
    }
    return color;
}
"""
FS_FUNC_TEX_GENERICO="""
// generico
vec4 tex_generico(){
    vec4 color_tex=vec4(0,0,0,0);
    color_tex+=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    return color_tex;
}
"""
FS_FUNC_TEX_AGUA="""
    color_tex+=texture2D(p3d_Texture1, gl_TexCoord[0].st); // agua
    color_tex+=texture2D(p3d_Texture2, gl_TexCoord[0].st); // agua
    color_tex+=texture2D(p3d_Texture3, gl_TexCoord[0].st); // agua
"""
FS_FUNC_TEX_TERRENO="""
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
        _color0=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0,0.5));
    } else if(tipo0==2){
        _color0=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0.5,0.5));
    } else if(tipo0==3){
        _color0=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0);
    } else if(tipo0==4){
        _color0=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0.5,0.5));
    } else if(tipo0==5){
        _color0=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0.5,0));
    } else {
        _color0=vec4(0,0,0,1);
    }
    if(tipo1==1){
        _color1=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0,0.5));
    } else if(tipo1==2){
        _color1=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0.5,0.5));
    } else if(tipo1==3){
        _color1=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0);
    } else if(tipo1==4){
        _color1=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0.5,0.5));
    } else if(tipo1==5){
        _color1=texture2D(p3d_Texture0, gl_TexCoord[0].st/2.0+vec2(0.5,0));
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
    vec2 distorted_texcoords=texture2D(p3d_Texture2,vec2(gl_TexCoord[0].s+move_factor, gl_TexCoord[0].t)).rg*0.1;
    distorted_texcoords=gl_TexCoord[0].st+vec2(distorted_texcoords.x,distorted_texcoords.y+move_factor);
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
    vec3 view_vector=normalize(cam_pos);
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
        vec4 color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
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
