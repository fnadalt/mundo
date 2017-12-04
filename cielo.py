from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Cielo:
    
    # colores
    ColorNoche=Vec4(0.0, 0.0, 0.2, 1.0)
    ColorAmanecer=Vec4(0.95, 0.75, 0.2, 1.0)
    ColorDia=Vec4(0.9, 1.0, 1.0, 1.0)
    ColorAtardecer=Vec4(0.95, 0.65, 0.3, 1.0)
    ColorIntermedioDiaNoche=(ColorDia+ColorNoche)/2.0
    ColorHaloDia=Vec4(1.0, 1.0, 1.0, 1.0)
    
    def __init__(self, base):
        # referencias:
        self.base=base
        # variables externas:
        self.color=Cielo.ColorNoche
        # variable internas:
        self._periodo_actual=0 # [0,3]; noche,amanecer,dia,atardecer
        self._offset_periodo_anterior=0
        self._color_inicial=Cielo.ColorNoche
        self._color_final=Cielo.ColorNoche
        self._color_actual=Cielo.ColorNoche
        self._colores_post_pico=False
        # componentes:
        # nodo
        self.nodo=self.base.cam.attachNewNode("sky_dome")
        #self.nodo.setColor(self._color_inicial)
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/cielo.v.glsl", fragment="shaders/cielo.f.glsl")
        self.nodo.setShader(shader)
        self.nodo.setShaderInput("posicion_sol", Vec3(0, 0, 0))
        self.nodo.setShaderInput("periodo", 0)
        self.nodo.setShaderInput("offset_periodo", 0.0)
        self.nodo.setShaderInput("color_base_inicial", Cielo.ColorNoche)
        self.nodo.setShaderInput("color_base_final", Cielo.ColorNoche)
        self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorNoche)
        self.nodo.setShaderInput("color_halo_final", Cielo.ColorNoche)
        # modelo
        self.modelo=self.base.loader.loadModel("objetos/sky_dome")
        self.modelo.reparentTo(self.nodo)
        self.modelo.setMaterialOff(1)
        self.modelo.setTextureOff(1)
        self.modelo.setLightOff(1)
        #self.modelo.setShaderOff(1)
        #self.modelo.setTwoSided(True)
        # luz
        self.luz=self.nodo.attachNewNode(AmbientLight("luz ambiental"))
        self.luz.node().setColor(Cielo.ColorNoche)
    
    # shader
    def update(self, posicion_sol, hora_normalizada, periodo, offset_periodo):
        # determinar periodo
        if periodo!=self._periodo_actual:
            self._periodo_actual=periodo
            self._procesa_cambio_periodo(self._periodo_actual, False)
        #
        if self._periodo_actual==1 or self._periodo_actual==3:
            if offset_periodo>0.5:
                offset_periodo-=0.5
                if self._offset_periodo_anterior<=0.5:
                    self._establecer_colores(offset_periodo, True)
            offset_periodo*=2
        # shader
        self.nodo.setShaderInput("posicion_sol", posicion_sol)
        self.nodo.setShaderInput("offset_periodo", offset_periodo)
        #
        self._offset_periodo_anterior=offset_periodo
    
    def obtener_info(self):
        info="Cielo\n"
        return info

    def _procesar_cambio_periodo(self, periodo, post_pico):
        self.nodo.setShaderInput("periodo", self._periodo_actual)
        if periodo==0:
            self.nodo.setShaderInput("color_base_inicial", Cielo.ColorNoche)
            self.nodo.setShaderInput("color_base_final", Cielo.ColorNoche)
            self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorNoche)
            self.nodo.setShaderInput("color_halo_final", Cielo.ColorNoche)
        elif periodo==1:
            if not post_pico:
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorNoche)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorNoche)
                self.nodo.setShaderInput("color_halo_final", Cielo.ColorAmanecer)
            else:
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorDia)
                self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorAmanecer)
                self.nodo.setShaderInput("color_halo_final", Cielo.ColorDia)
        elif periodo==2:
            self.nodo.setShaderInput("color_base_inicial", Cielo.ColorDia)
            self.nodo.setShaderInput("color_base_final", Cielo.ColorDia)
            self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorDia)
            self.nodo.setShaderInput("color_halo_final", Cielo.ColorHaloDia)
        elif self._periodo_actual==3:
            if not post_pico:
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorDia)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorHaloDia)
                self.nodo.setShaderInput("color_halo_final", Cielo.ColorAtardecer)
            else:
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorNoche)
                self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorAtardecer)
                self.nodo.setShaderInput("color_halo_final", Cielo.ColorNoche)
