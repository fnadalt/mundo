from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class GeneradorShader:

    # clases
    ClaseNulo=0
    ClaseGenerico=1
    ClaseTerreno=2
    ClaseAgua=3
    ClaseCielo=4
    ClaseSol=5
    
    def __init__(self, clase, nodo):
        # referencias:
        self.nodo=nodo
        # variables externas:
        self.clase=clase
        self._altitud_agua=0.0
        self._posicion_sol=Vec3(0, 0, 0)
        self.plano_recorte_agua=Vec4(0, 0, 0, 0)
        self.plano_recorte_agua_inv=Vec4(0, 0, 0, 0)
        # variables internas:
        self._cantidad_texturas=0
        
    def generar_aplicar(self):
        # generico
        if self.clase==GeneradorShader.ClaseGenerico:
            shader=self._generar_generico()
        # aplicar shader
        prioridad=1000
        self.nodo.setShader(shader, prioridad)
        self.nodo.setShaderInput("altitud_agua", self._altitud_agua, prioridad)
        self.nodo.setShaderInput("posicion_sol", self._posicion_sol, prioridad)
        if self.plano_recorte_agua!=Vec4(0, 0, 0, 0):
            self.nodo.setShaderInput("plano_recorte_agua", self.plano_recorte_agua, prioridad)
        self.nodo.setShaderInput("periodo", 0.0, prioridad)
        self.nodo.setShaderInput("offset_periodo", 0.0, prioridad)
        self.nodo.setShaderInput("color_cielo_base_inicial", Vec4(0, 0, 0, 0), prioridad)
        self.nodo.setShaderInput("color_cielo_base_final", Vec4(0, 0, 0, 0), prioridad)
        self.nodo.setShaderInput("color_halo_sol_inicial", Vec4(0, 0, 0, 0), prioridad)
        self.nodo.setShaderInput("color_halo_sol_final", Vec4(0, 0, 0, 0), prioridad)

    def activar_textura(self, indice):
        if indice>self._cantidad_texturas:
            log.error("textura de indice %i, ya esta activada"%indice)
            return
        self._cantidad_texturas+=1

    def activar_recorte_agua(self, direccion, altitud_agua):
        self.plano_recorte_agua=Vec4(direccion[0], direccion[1], direccion[2], altitud_agua)
        self.plano_recorte_agua=Vec4(direccion[0], direccion[1], -direccion[2], altitud_agua)

    def _generar_generico(self):
        # texto
        texto_vs=""
        texto_fs=""
        # texturas
        texto_vs_attrib_tc=""
        texto_vs_main_tc=""
        texto_fs_unif_tc=""
        texto_fs_func_tex_0=""
        texto_fs_func_tex_1=""
        texto_fs_main_tex_0=""
        if self._cantidad_texturas>0:
            texto_vs_attrib_tc=VS_ATTR_TC
            texto_vs_main_tc=VS_MAIN_TC
            texto_fs_main_tex_0=FS_MAIN_TEX_0
            for i in range(self._cantidad_texturas):
                texto_fs_unif_tc+=FS_UNIF_TC%{"indice_textura":i}
                texto_fs_func_tex_1+=FS_FUNC_TEX_1%{"indice_textura":i}
            texto_fs_func_tex_0=FS_FUNC_TEX_0%{"FS_FUNC_TEX_1":texto_fs_func_tex_1}
        # plano_recorte_agua
        texto_fs_unif_clip=""
        texto_fs_main_clip_0=""
        texto_fs_main_clip_1=""
        if self.plano_recorte_agua!=Vec4(0, 0, 0, 0):
            texto_fs_unif_clip=FS_UNIF_CLIP
            texto_fs_main_clip_0=FS_MAIN_CLIP_0
            texto_fs_main_clip_1=FS_MAIN_CLIP_1
        # vs
        texto_vs+=VS_ATTR_0%{"VS_ATTR_TC":texto_vs_attrib_tc}
        texto_vs+=VS_UNIF_0
        texto_vs+=VS_VAR_0
        texto_vs+=VS_MAIN_0%{"VS_MAIN_TC":texto_vs_main_tc}
        # fs
        texto_fs+=FS_UNIF_0%{"FS_UNIF_TC":texto_fs_unif_tc}
        texto_fs+=FS_UNIF_1%{"FS_UNIF_CLIP":texto_fs_unif_clip}
        texto_fs+=FS_VAR_0
        texto_fs+=FS_FUNC_ADS
        texto_fs+=texto_fs_func_tex_0
        texto_fs+=FS_MAIN_0%{"FS_MAIN_TEX_0":texto_fs_main_tex_0, "FS_MAIN_CLIP_0":texto_fs_main_clip_0, "FS_MAIN_CLIP_1":texto_fs_main_clip_1}
        # archivos
        with open("shaders/vs.glsl", "w+") as arch_vs:
            arch_vs.write(texto_vs)
        with open("shaders/fs.glsl", "w+") as arch_fs:
            arch_fs.write(texto_fs)
        # shader
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/vs.glsl", fragment="shaders/fs.glsl")
        return shader

#
#
# VERTEX SHADER
#
#
# attributes
VS_ATTR_0="""#version 120
attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute vec4 p3d_Color;
%(VS_ATTR_TC)s
"""
VS_ATTR_TC="attribute vec4 p3d_MultiTexCoord0;"
# uniforms
VS_UNIF_0="""
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
"""
# varying
VS_VAR_0="""
varying vec4 Position;
varying vec3 Normal;
"""
# main
VS_MAIN_0="""
void main() {
    Position=p3d_ModelViewMatrix*p3d_Vertex;
    Normal=normalize(p3d_NormalMatrix*p3d_Normal);
    %(VS_MAIN_TC)s
    gl_Position=p3d_ModelViewProjectionMatrix*gl_Vertex;
}
"""
VS_MAIN_TC="gl_TexCoord[0]=p3d_MultiTexCoord0;\n"

#
#
# FRAGMENT SHADER
#
#
# uniforms
FS_UNIF_0="""#version 120
%(FS_UNIF_TC)s
uniform mat4 p3d_ViewMatrix;
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
"""
FS_UNIF_1="""
uniform int periodo;
uniform float offset_periodo;
uniform vec4 color_cielo_base_inicial;
uniform vec4 color_cielo_base_final;
uniform vec4 color_halo_sol_inicial;
uniform vec4 color_halo_sol_final;
uniform float altitud_agua;
uniform vec3 posicion_sol;
%(FS_UNIF_CLIP)s
"""
FS_UNIF_CLIP="uniform vec4 plano_recorte_agua;"
FS_UNIF_TC="uniform sampler2D p3d_Texture%(indice_textura)i;\n"
# varying
FS_VAR_0="""
varying vec4 Position;
varying vec3 Normal;
"""
FS_VAR_CLIP="varying vec4 PlanoAgua;"
# ads
FS_FUNC_ADS="""
vec4 amb()
{
    return p3d_LightModel.ambient*p3d_Material.ambient;
}
vec4 ds(int iLightSource)
{
    vec3 s=p3d_LightSource[iLightSource].position.xyz-(Position.xyz*p3d_LightSource[iLightSource].position.w);
    vec3 l=normalize(s);
    vec4 diffuse=clamp(p3d_Material.diffuse*p3d_LightSource[iLightSource].diffuse*max(dot(Normal,l),0),0,1);
    if(p3d_Material.specular!=vec3(0,0,0)){
        vec3 v=normalize(-Position.xyz);
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
"""
FS_FUNC_TEX_0="""
vec4 tex(){
    vec4 color_tex=vec4(0,0,0,0);
    %(FS_FUNC_TEX_1)s
    return color_tex;
}
"""
FS_FUNC_TEX_1="color_tex+=texture2D(p3d_Texture%(indice_textura)i, gl_TexCoord[0].st);\n"
# main
FS_MAIN_0="""
void main()
{
    %(FS_MAIN_CLIP_0)s
        vec4 suma_ds=vec4(0,0,0,0);
        int cantidad_luces=p3d_LightSource.length();
        for(int i=0; i<cantidad_luces; ++i)
        {
            suma_ds+=ds(i);
        }
        vec4 color_ads=(amb()+suma_ds);
        %(FS_MAIN_TEX_0)s
        color_ads.a=1.0;
        gl_FragColor=color_ads;
    %(FS_MAIN_CLIP_1)s
}
"""
FS_MAIN_TEX_0="color_ads*=tex();"
FS_MAIN_CLIP_0="""
    vec4 plano_rec=p3d_ViewMatrix*plano_recorte_agua;
    if (dot(plano_recorte_agua, Position) < 0) {
        discard;
    } else {
"""
FS_MAIN_CLIP_1="""
    }
"""
