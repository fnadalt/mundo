from glsl import *

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
varying vec4 texcoord; // generico, terreno, agua, sol
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
attribute vec3 info_tipo_terreno;
attribute vec4 Tangent;
varying vec3 info_tipo;
varying vec4 tangent;
"""
VS_TERRENO_COLOR_DEBUG="""
attribute vec4 Color;
varying vec4 color_vtx;
"""

#
#
# FRAGMENT SHADER
#
#
FS_FUNC_TEX_LOOK_UP="texture2D"
FS_COMUN="""
const float TamanoHalo=0.85;
varying vec4 PositionW; // clip
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
"""
FS_TEX_0="""
uniform sampler2D p3d_Texture0; // !cielo
varying vec4 texcoord;
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
FS_TERRENO="""
varying vec3 info_tipo;
varying vec4 tangent;
"""
FS_TERRENO_COLOR_DEBUG="""
varying vec4 color_vtx;
"""

#
#
# OTRO
#
#
FUNC_TEX_LOOK_UP="texture2D"
