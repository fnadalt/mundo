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
        # componentes:
        self.shader=None
        # variables externas:
        self.prioridad_shader=1
        self.cantidad_texturas=0
        self.plano_recorte_agua=Vec4(0, 0, 0, 0)
        self.plano_recorte_agua_inv=Vec4(0, 0, 0, 0)
        # variables internas:
        self._clase=clase
        self._altitud_agua=0.0
        self._posicion_sol=Vec3(0, 0, 0)
        
    def generar_aplicar(self):
        # generar
        self.shader=self._generar()
        # aplicar shader
        self.nodo.setShader(self.shader, priority=self.prioridad_shader)
        self.nodo.setShaderInput("altitud_agua", self._altitud_agua, priority=self.prioridad_shader)
        self.nodo.setShaderInput("posicion_sol", self._posicion_sol, priority=self.prioridad_shader)
        self.nodo.setShaderInput("pos_pivot_camara", Vec3(0, 0, 0), priority=self.prioridad_shader)
        if self.plano_recorte_agua!=Vec4(0, 0, 0, 0):
            self.nodo.setShaderInput("plano_recorte_agua", self.plano_recorte_agua, priority=self.prioridad_shader)

    def activar_recorte_agua(self, direccion, altitud_agua):
        self.plano_recorte_agua=Vec4(direccion[0], direccion[1], direccion[2], altitud_agua)
        self.plano_recorte_agua_inv=Vec4(-direccion[0], -direccion[1], -direccion[2], -altitud_agua)

    def invertir_plano_recorte_agua(self):
        tmp=self.plano_recorte_agua
        self.plano_recorte_agua=self.plano_recorte_agua_inv
        self.plano_recorte_agua_inv=tmp

    def _generar(self):
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
        if self.cantidad_texturas>0:
            texto_vs_attrib_tc=VS_ATTR_TC
            texto_vs_main_tc=VS_MAIN_TC
            texto_fs_main_tex_0=FS_MAIN_TEX_0
            for i in range(self.cantidad_texturas):
                texto_fs_unif_tc+=FS_UNIF_TC%{"indice_textura":i}
                texto_fs_func_tex_1+=FS_FUNC_TEX_1%{"indice_textura":i}
            if self._clase==GeneradorShader.ClaseTerreno:
                texto_fs_func_tex_0=FS_FUNC_TEX_TERRENO
            else:
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
        if self._clase==GeneradorShader.ClaseTerreno:
            texto_vs+=VS_ATTR_TERRENO
            texto_vs+=VS_VAR_TERRENO
        if self.plano_recorte_agua!=Vec4(0, 0, 0, 0) or self._clase==GeneradorShader.ClaseCielo or self._clase==GeneradorShader.ClaseSol:
            texto_vs+=VS_VAR_POSITIONW
        if self._clase==GeneradorShader.ClaseCielo:
            texto_vs+=VS_VAR_POSITION
        if self._clase==GeneradorShader.ClaseAgua:
            texto_vs+=VS_VAR_POSITIONP
        #
        texto_vs+=VS_MAIN_0%{"VS_MAIN_TC":texto_vs_main_tc}
        if self.plano_recorte_agua!=Vec4(0, 0, 0, 0) or self._clase==GeneradorShader.ClaseCielo or self._clase==GeneradorShader.ClaseSol:
            texto_vs+=VS_MAIN_POSITIONW
        if self._clase==GeneradorShader.ClaseTerreno:
            texto_vs+=VS_MAIN_TERRENO
        elif self._clase==GeneradorShader.ClaseCielo:
            texto_vs+=VS_MAIN_POSITION
        elif self._clase==GeneradorShader.ClaseAgua:
            texto_vs+=VS_MAIN_POSITIONP
        texto_vs+=VS_MAIN_1
        # fs
        texto_fs+="#version 120\n"
        if self._clase!=GeneradorShader.ClaseCielo and self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseAgua:
            texto_fs+=FS_UNIF_0%{"FS_UNIF_TC":texto_fs_unif_tc}
        if self._clase==GeneradorShader.ClaseSol or self._clase==GeneradorShader.ClaseAgua:
            texto_fs+=texto_fs_unif_tc
        texto_fs+=FS_UNIF_1%{"FS_UNIF_CLIP":texto_fs_unif_clip}
        if self._clase==GeneradorShader.ClaseCielo:
            texto_fs+=FS_UNIF_CIELO
            texto_fs+=FS_CONST_CIELO
        elif self._clase==GeneradorShader.ClaseAgua:
            texto_fs+=FS_UNIF_CIELO
            texto_fs+=FS_UNIF_AGUA
            texto_fs+=FS_CONST_AGUA
        texto_fs+=FS_VAR_0
        if self._clase==GeneradorShader.ClaseTerreno:
            texto_fs+=FS_VAR_TERRENO
        if self.plano_recorte_agua!=Vec4(0, 0, 0, 0) or self._clase==GeneradorShader.ClaseCielo or self._clase==GeneradorShader.ClaseSol:
            texto_fs+=FS_VAR_POSITIONW
        if self._clase==GeneradorShader.ClaseCielo:
            texto_fs+=FS_VAR_POSITION
        elif self._clase==GeneradorShader.ClaseAgua:
            texto_fs+=FS_VAR_POSITIONP
        #
        if self._clase!=GeneradorShader.ClaseCielo and self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseAgua:
            texto_fs+=FS_FUNC_ADS
        if self._clase!=GeneradorShader.ClaseCielo:
            texto_fs+=texto_fs_func_tex_0
        #
        if self._clase==GeneradorShader.ClaseCielo:
            texto_fs+=FS_MAIN_0_CIELO%{"FS_MAIN_CLIP_0":texto_fs_main_clip_0, "FS_MAIN_CLIP_1":texto_fs_main_clip_1}
        elif self._clase==GeneradorShader.ClaseSol:
            texto_fs+=FS_MAIN_0_SOL%{"FS_MAIN_CLIP_0":texto_fs_main_clip_0, "FS_MAIN_CLIP_1":texto_fs_main_clip_1}
        elif self._clase==GeneradorShader.ClaseAgua:
            texto_fs+=FS_MAIN_0_AGUA
        else:
            texto_fs+=FS_MAIN_0%{"FS_MAIN_LUCES":FS_MAIN_LUCES,"FS_MAIN_TEX_0":texto_fs_main_tex_0, "FS_MAIN_CLIP_0":texto_fs_main_clip_0, "FS_MAIN_CLIP_1":texto_fs_main_clip_1}
        texto_fs+=FS_MAIN_1
        # archivos
        ruta_archivo_vs="shaders/vs.%i.glsl"%self._clase
        ruta_archivo_fs="shaders/fs.%i.glsl"%self._clase
        with open(ruta_archivo_vs, "w+") as arch_vs:
            arch_vs.write(texto_vs)
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
# attributes
VS_ATTR_0="""#version 120
attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute vec4 p3d_Color;
%(VS_ATTR_TC)s
"""
VS_ATTR_TC="attribute vec4 p3d_MultiTexCoord0;"
VS_ATTR_TERRENO="""
attribute float info_tipo_terreno;
"""
# uniforms
VS_UNIF_0="""
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
"""
# varying
VS_VAR_0="""
varying vec4 PositionV;
varying vec3 Normal;
"""
VS_VAR_TERRENO="""
varying float info_tipo;
varying float info_tipo_factor;
"""
VS_VAR_POSITIONW="varying vec4 PositionW;\n"
VS_VAR_POSITIONP="varying vec4 PositionP;\n"
VS_VAR_POSITION="varying vec4 Position;\n"
# main
VS_MAIN_0="""
void main() {
    PositionV=p3d_ModelViewMatrix*p3d_Vertex;
    Normal=normalize(p3d_NormalMatrix*p3d_Normal);
    %(VS_MAIN_TC)s
    gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;
"""
VS_MAIN_1="""
}
"""
VS_MAIN_TC="gl_TexCoord[0]=p3d_MultiTexCoord0;\n"
VS_MAIN_POSITIONW="PositionW=p3d_ModelMatrix*p3d_Vertex;\n"
VS_MAIN_POSITIONP="PositionP=gl_Position;\n"
VS_MAIN_POSITION="Position=p3d_Vertex;\n"
VS_MAIN_TERRENO="""
    info_tipo=floor(info_tipo_terreno);
    info_tipo_factor=fract(info_tipo_terreno);
"""

#
#
# FRAGMENT SHADER
#
#
# uniforms
FS_UNIF_0="""
%(FS_UNIF_TC)s
uniform mat4 p3d_ModelViewMatrix;
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
uniform float altitud_agua;
uniform vec3 posicion_sol;
%(FS_UNIF_CLIP)s
"""
FS_UNIF_CIELO="""
uniform vec3 pos_pivot_camara;
uniform float offset_periodo;
uniform vec4 color_cielo_base_inicial;
uniform vec4 color_cielo_base_final;
uniform vec4 color_halo_sol_inicial;
uniform vec4 color_halo_sol_final;
"""
FS_UNIF_AGUA="""
uniform vec3 cam_pos;
uniform float move_factor;
"""
FS_UNIF_CLIP="uniform vec4 plano_recorte_agua;"
FS_UNIF_TC="uniform sampler2D p3d_Texture%(indice_textura)i;\n"
# constantes
FS_CONST_CIELO="const float TamanoHalo=0.85;\n"
FS_CONST_AGUA="""
const float shine_damper=20.0;
const float reflectivity=0.6;
"""
# varying
FS_VAR_0="""
varying vec4 PositionV;
varying vec3 Normal;
"""
FS_VAR_POSITIONW="varying vec4 PositionW;\n"
FS_VAR_POSITIONP="varying vec4 PositionP;\n"
FS_VAR_POSITION="varying vec4 Position;\n"
FS_VAR_TERRENO="""
varying float info_tipo;
varying float info_tipo_factor;
"""
# ads
FS_FUNC_ADS="""
vec4 amb()
{
    return p3d_LightModel.ambient*p3d_Material.ambient;
}
vec4 ds(int iLightSource)
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
"""
FS_FUNC_TEX_0="""
vec4 tex(){
    vec4 color_tex=vec4(0,0,0,0);
    %(FS_FUNC_TEX_1)s
    return color_tex;
}
"""
FS_FUNC_TEX_1="color_tex+=texture2D(p3d_Texture%(indice_textura)i, gl_TexCoord[0].st);\n"
FS_FUNC_TEX_TERRENO="""
vec4 tex()
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
"""
# main
FS_MAIN_0="""
void main()
{
    %(FS_MAIN_CLIP_0)s
        vec4 color=vec4(0,0,0,0);
        %(FS_MAIN_LUCES)s
        %(FS_MAIN_TEX_0)s
        color.a=1.0;
        gl_FragColor=color;
    %(FS_MAIN_CLIP_1)s
"""
FS_MAIN_1="""
}
"""
FS_MAIN_0_CIELO="""
void main()
{
    %(FS_MAIN_CLIP_0)s
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
        gl_FragColor=color;
    %(FS_MAIN_CLIP_1)s
"""
FS_MAIN_0_SOL="""
void main()
{
    if(distance(posicion_sol,PositionW.xyz)>20.0){
        gl_FragColor=vec4(0,0,0,1);
    } else {
    %(FS_MAIN_CLIP_0)s
        vec4 color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
        gl_FragColor=color;//*2*(color.a - 0.5);
    %(FS_MAIN_CLIP_1)s
    }
"""
FS_MAIN_0_AGUA="""
uniform mat4 p3d_ModelViewMatrix;
void main()
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
    gl_FragColor=color;
"""
FS_MAIN_TEX_0="color*=tex();"
FS_MAIN_LUCES="""
        int cantidad_luces=p3d_LightSource.length();
        for(int i=0; i<cantidad_luces; ++i)
        {
            color+=ds(i);
        }
        color+=amb();
"""
FS_MAIN_CLIP_0="""
    if (PositionW.x*plano_recorte_agua.x + PositionW.y*plano_recorte_agua.y + PositionW.z*plano_recorte_agua.z - plano_recorte_agua.w <= 0) {
        discard;
    } else {
"""
FS_MAIN_CLIP_1="""
    }
"""
