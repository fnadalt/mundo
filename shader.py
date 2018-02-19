from panda3d.core import *

import os, os.path

import config
import glsl120
import glsl130

import logging
log=logging.getLogger(__name__)

# globales
shaders=dict() # {tipo:shader,...}
_glsl_version=130
_altitud_agua=None
_plano_recorte_agua=Vec4(0, 0, 1, 0)
_plano_recorte_agua_inv=Vec4(0, 0, -1, 0)

class GeneradorShader:

    # clases
    ClaseNulo="nulo"
    ClaseDebug="debug"
    ClaseGenerico="generico"
    ClaseTerreno="terreno"
    ClaseAgua="agua"
    ClaseCielo="cielo"
    ClaseSol="sol"
    ClaseSombra="sombra"

    @staticmethod
    def iniciar(base, altitud_agua, plano_recorte_agua):
        global _glsl_version, _altitud_agua, _plano_recorte_agua, _plano_recorte_agua_inv
        #
        if base:
            glsl_mj=base.win.getGsg().getDriverShaderVersionMajor()
            glsl_mn=base.win.getGsg().getDriverShaderVersionMinor()
            _glsl_version=int(glsl_mj)*100+int(glsl_mn)
            log.info("opengl glsl version %i"%_glsl_version)
            if _glsl_version<120:
                raise Exception("version de glsl no soportada")
        #
        if _altitud_agua!=None:
            log.warning("GeneradorShader ya iniciado")
            return
        _altitud_agua=altitud_agua
        _plano_recorte_agua=plano_recorte_agua
        _plano_recorte_agua_inv=Vec4(-_plano_recorte_agua[0], -_plano_recorte_agua[1], -_plano_recorte_agua[2], -_altitud_agua)
        #

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
        nodo.setShaderInput("color_luz_ambiental", Vec4(1, 1, 0.93, 1.0)*0.3, priority=prioridad)
        nodo.setShaderInput("offset_periodo_cielo", 0.0, priority=prioridad)
        nodo.setShaderInput("color_cielo_base_inicial", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_cielo_base_final", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_halo_sol_inicial", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("color_halo_sol_final", Vec4(0, 0, 0, 0), priority=prioridad)
        nodo.setShaderInput("plano_recorte_agua", _plano_recorte_agua, priority=prioridad)
        if config.valbool("shader.fog"):
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
        if self._clase==GeneradorShader.ClaseDebug:
            shader=Shader.load(Shader.SL_GLSL, vertex="shaders/debug.v.glsl", fragment="shaders/debug.f.glsl")
            return shader
        #
        glsl=None
        if _glsl_version>=130:
            log.info("se utiliza glsl 130")
            glsl=glsl130
        elif _glsl_version==120:
            log.info("se utiliza glsl 120")
            glsl=glsl120
        # texto
        texto_vs="#version %s\n"%str(_glsl_version)
        texto_fs="#version %s\n"%str(_glsl_version)
        # vs
        texto_vs+=glsl.VS_COMUN
        if self._clase!=GeneradorShader.ClaseCielo:
            texto_vs+=glsl.VS_TEX
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                texto_vs+=glsl.VS_POS_VIEW
                if config.valbool("shader.phong") or config.valbool("shader.sombras"):
                    texto_vs+=glsl.VS_SOMBRA
            if self._clase==GeneradorShader.ClaseAgua or self._clase==GeneradorShader.ClaseSombra:
                texto_vs+=glsl.VS_POS_PROJ
            elif self._clase==GeneradorShader.ClaseTerreno:
                texto_vs+=glsl.VS_TIPO_TERRENO
                if config.valbool("terreno.color_debug"):
                    texto_vs+=glsl.VS_TERRENO_COLOR_DEBUG
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_vs+=glsl.VS_POS_MODELO
        texto_vs+=glsl.VS_MAIN_INICIO
        texto_vs+=glsl.VS_MAIN_COMUN
        if self._clase!=GeneradorShader.ClaseCielo:
            texto_vs+=glsl.VS_MAIN_TEX
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                texto_vs+=glsl.VS_MAIN_VIEW
                if config.valbool("shader.sombras"):
                    texto_vs+=glsl.VS_MAIN_SOMBRA
            if self._clase==GeneradorShader.ClaseTerreno:
                texto_vs+=glsl.VS_MAIN_TIPO_TERRENO
                if config.valbool("terreno.color_debug"):
                    texto_vs+=glsl.VS_MAIN_TERRENO_COLOR_DEBUG
        texto_vs+=glsl.VS_MAIN_POSITION
        if self._clase==GeneradorShader.ClaseAgua or self._clase==GeneradorShader.ClaseSombra:
            texto_vs+=glsl.VS_MAIN_VERTEX_PROJ
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_vs+=glsl.VS_MAIN_VERTEX
        texto_vs+=glsl.VS_MAIN_FIN
        # fs
        texto_fs+=glsl.FS_COMUN
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_fs+=glsl.FS_POS_MODELO
        if self._clase!=GeneradorShader.ClaseCielo:
            if self._clase!=GeneradorShader.ClaseSombra:
                texto_fs+=glsl.FS_TEX_0
                texto_fs+=glsl.FS_POS_VIEW
            if self._clase==GeneradorShader.ClaseTerreno:
                texto_fs+=glsl.FS_TERRENO
                texto_fs+=glsl.FS_TEX_1
                texto_fs+=glsl.FS_TEX_2
                if config.valbool("terreno.color_debug"):
                    texto_fs+=glsl.FS_TERRENO_COLOR_DEBUG
            if self._clase==GeneradorShader.ClaseAgua:
                texto_fs+=glsl.FS_TEX_1
                texto_fs+=glsl.FS_TEX_2
                texto_fs+=glsl.FS_TEX_3
                texto_fs+=glsl.FS_POS_PROJ
                texto_fs+=glsl.FS_AGUA
                texto_fs+=glsl.FS_FUNC_AGUA%{"FS_FUNC_TEX_LOOK_UP":glsl.FS_FUNC_TEX_LOOK_UP}
            if self._clase==GeneradorShader.ClaseSombra:
                texto_fs+=glsl.FS_POS_PROJ
            if self._clase==GeneradorShader.ClaseTerreno or self._clase==GeneradorShader.ClaseGenerico:
                if config.valbool("shader.phong"):
                    texto_fs+=glsl.FS_LUZ
                    fs_func_luz_transform_luz=glsl.FUNC_LIGHT_VEC_TRANSFORM_VTX
                    if self._clase==GeneradorShader.ClaseTerreno and config.valbool("terreno.normal_map"):
                        fs_func_luz_transform_luz=glsl.FUNC_LIGHT_VEC_TRANSFORM_NORMAL_MAP_TERRENO
                        texto_fs+=glsl.FS_FUNC_TRANSFORM_LUZ_NORMAL_MAP_TERRENO
                    fs_func_luz_sombra=""
                    if config.valbool("shader.sombras"):
                        fs_func_luz_sombra=glsl.FS_FUNC_LUZ_SOMBRA
                    texto_fs+=glsl.FS_FUNC_LUZ%{"FS_FUNC_LUZ_SOMBRA":fs_func_luz_sombra, 
                                                "FUNC_LIGHT_VEC_TRANSFORM":fs_func_luz_transform_luz}
                if self._clase==GeneradorShader.ClaseTerreno:
                    texto_fs+=glsl.FS_FUNC_TEX_TERRENO%{"FS_FUNC_TEX_LOOK_UP":glsl.FS_FUNC_TEX_LOOK_UP}
                    if config.valbool("terreno.normal_map"):
                        texto_fs+=glsl.FS_FUNC_NORMAL_MAP_TERRENO%{"FS_FUNC_TEX_LOOK_UP":glsl.FS_FUNC_TEX_LOOK_UP}
                else:
                    texto_fs+=glsl.FS_FUNC_TEX_GENERICO%{"FS_FUNC_TEX_LOOK_UP":glsl.FS_FUNC_TEX_LOOK_UP}
            elif self._clase==GeneradorShader.ClaseSol:
                texto_fs+=glsl.FS_FUNC_SOL%{"FS_FUNC_TEX_LOOK_UP":glsl.FS_FUNC_TEX_LOOK_UP}
            elif self._clase==GeneradorShader.ClaseSombra:
                texto_fs+=glsl.FS_FUNC_SOMBRA
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                if config.valbool("shader.fog"):
                    texto_fs+=glsl.FS_FOG
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_fs+=glsl.FS_FUNC_CIELO
        texto_fs+=glsl.FS_MAIN_INICIO
        if self._clase!=GeneradorShader.ClaseAgua and self._clase!=GeneradorShader.ClaseCielo:
            texto_fs+=glsl.FS_MAIN_CLIP_INICIO
        if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
            texto_fs+=glsl.FS_MAIN_CIELO_FOG
        if self._clase==GeneradorShader.ClaseCielo:
            texto_fs+=glsl.FS_MAIN_CIELO
        else:
            if self._clase==GeneradorShader.ClaseGenerico or self._clase==GeneradorShader.ClaseTerreno:
                if config.valbool("shader.phong"):
                    if self._clase==GeneradorShader.ClaseTerreno and config.valbool("terreno.normal_map"):
                        texto_fs+=glsl.FS_MAIN_LUZ%{"FUNC_NORMAL_SOURCE":glsl.FUNC_NORMAL_SOURCE_NORMAL_MAP_TERRENO}
                    else:
                        texto_fs+=glsl.FS_MAIN_LUZ%{"FUNC_NORMAL_SOURCE":glsl.FUNC_NORMAL_SOURCE_VTX}
                else:
                    texto_fs+=glsl.FS_MAIN_LUZ_BLANCA
                if self._clase==GeneradorShader.ClaseGenerico:
                    texto_fs+=glsl.FS_MAIN_TEX_GENERICO
                else: # terreno
                    if config.valbool("terreno.color_debug"):
                        texto_fs+=glsl.FS_MAIN_TEX_TERRENO_COLOR_DEBUG
                    else:
                        texto_fs+=glsl.FS_MAIN_TEX_TERRENO
            elif self._clase==GeneradorShader.ClaseAgua:
                texto_fs+=glsl.FS_MAIN_AGUA
            elif self._clase==GeneradorShader.ClaseSol:
                texto_fs+=glsl.FS_MAIN_SOL
            elif self._clase==GeneradorShader.ClaseSombra:
                texto_fs+=glsl.FS_MAIN_SOMBRA
            if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                if config.valbool("shader.fog"):
                    texto_fs+=glsl.FS_MAIN_FOG_FACTOR
            if self._clase==GeneradorShader.ClaseAgua and config.valbool("shader.fog"):
                texto_fs+=glsl.FS_MAIN_ALPHA_AGUA
            else:
                if self._clase!=GeneradorShader.ClaseSol and self._clase!=GeneradorShader.ClaseSombra:
                    if config.valbool("shader.fog"):
                        texto_fs+=glsl.FS_MAIN_FOG_COLOR
                if self._clase==GeneradorShader.ClaseGenerico:
                    texto_fs+=glsl.FS_MAIN_ALPHA_TEX_GENERICO
                else:
                    texto_fs+=glsl.FS_MAIN_ALPHA
        texto_fs+=glsl.FS_MAIN_COLOR
        if self._clase!=GeneradorShader.ClaseAgua and self._clase!=GeneradorShader.ClaseCielo:
            texto_fs+=glsl.FS_MAIN_CLIP_FIN
        texto_fs+=glsl.FS_MAIN_FIN
        # archivos
        ruta_archivo_vs="shaders/vs.%s.glsl"%self._clase
        ruta_archivo_fs="shaders/fs.%s.glsl"%self._clase
        #
        if config.archivo_modificado():
            log.info("archivo de inicio modificado...")
            if os.path.exists(ruta_archivo_vs):
                log.info("eliminando archivo shader %s..."%ruta_archivo_vs)
                os.remove(ruta_archivo_vs)
            if os.path.exists(ruta_archivo_fs):
                log.info("eliminando archivo shader %s..."%ruta_archivo_fs)
                os.remove(ruta_archivo_fs)
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
