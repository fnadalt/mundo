from glsl import *

#
#
# VERTEX SHADER
#
#
VS_COMUN="""
in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
out vec4 PositionW; // clip
"""
VS_TEX="""
in vec4 p3d_MultiTexCoord0; // generico, terreno, agua, sol
out vec4 texcoord; // generico, terreno, agua, sol
"""
VS_POS_MODELO="""
out vec4 Position; // fog y cielo
"""
VS_POS_VIEW="""
in vec3 p3d_Normal;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
out vec4 PositionV; // luz, fog
out vec3 Normal;
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
out vec4 sombra[8];
"""
VS_POS_PROJ="""
out vec4 PositionP; // agua
"""
VS_TIPO_TERRENO="""
in vec3 info_tipo_terreno;
in vec4 Tangent;
in vec4 Binormal;
flat out vec3 info_tipo;
out vec4 tangent;
out vec4 binormal;
"""
VS_TERRENO_COLOR_DEBUG="""
in vec4 Color;
out vec4 color_vtx;
"""

#
#
# FRAGMENT SHADER
#
#
FS_FUNC_TEX_LOOK_UP="texture"
FS_COMUN="""
const float TamanoHalo=0.85;
in vec4 PositionW; // clip
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
in vec4 texcoord;
"""
FS_POS_MODELO="""
in vec4 Position; // cielo
"""
FS_POS_VIEW="""
in vec4 PositionV; // luz, fog
in vec3 Normal;
"""
FS_POS_PROJ="""
in vec4 PositionP; // agua
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
in vec4 sombra[8];
"""
FS_TERRENO="""
flat in vec3 info_tipo;
in vec4 tangent;
in vec4 binormal;
"""
FS_TERRENO_COLOR_DEBUG="""
in vec4 color_vtx;
"""

#
#
# OTRO
#
#
FUNC_TEX_LOOK_UP="texture"
