from glsl import *

#
#
#
#
#
STRUCT_LUZ_P3D="""
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
} """
STRUCT_LUZ_OMNI="""
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
} """

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
VS_COLOR_VERTEX="""
out vec4 vcolor;
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
/*%(STRUCT_LUZ_P3D)s p3d_LightSource[4];*/
out vec4 sombra[4];
"""%{"STRUCT_LUZ_P3D":STRUCT_LUZ_P3D} # ELIMINAR p3d_LightSource
VS_POS_PROJ="""
out vec4 PositionP; // agua
"""
VS_NORMAL_MAP="""
in vec4 p3d_Tangent;
out vec4 tangent;
"""
VS_TIPO_TERRENO="""
in vec3 info_tipo_terreno;
flat out vec3 info_tipo;
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
out vec4 color;
const float TamanoHalo=0.85;
in vec4 PositionW; // clip
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
"""
FS_COLOR_VERTEX="in vec4 vcolor;"
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
uniform mat4 p3d_ModelViewMatrix; // sin uso?
"""
FS_POS_PROJ="""
in vec4 PositionP; // agua
"""
FS_TERRENO="""
flat in vec3 info_tipo;
"""
FS_SOMBRA="""
in vec4 sombra[4];
"""
FS_NORMAL_MAP="""
in vec4 tangent;
"""
FS_TERRENO_COLOR_DEBUG="""
in vec4 color_vtx;
"""
FS_MAIN_INICIO_COLOR="color=vec4(0,0,0,0);"
FS_MAIN_COLOR="""
"""

#
#
# LUZ
#
#
LUZ="""
/*uniform struct {
    vec4 ambient;
} p3d_LightModel;*/
%(STRUCT_LUZ_P3D)s p3d_LightSource[4];
%(STRUCT_LUZ_OMNI)s luz_omni[4];
"""%{"STRUCT_LUZ_P3D":STRUCT_LUZ_P3D, "STRUCT_LUZ_OMNI":STRUCT_LUZ_OMNI}

#
#
# OTRO
#
#
COLOR_LUZ_AMBIENTAL="uniform vec4 color_luz_ambiental;"
FUNC_TEX_LOOK_UP="texture"
