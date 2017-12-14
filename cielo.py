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
    
    def __init__(self, base, altitud_agua):
        # referencias:
        self.base=base
        # componentes:
        # nodo
        self.nodo=self.base.cam.attachNewNode("sky_dome")
        self.nodo.setBin("background", 10)
        # modelo
        self.modelo=self.base.loader.loadModel("objetos/sky_dome")
        self.modelo.reparentTo(self.nodo)
        self.modelo.setMaterialOff(1)
        self.modelo.setTextureOff(1)
        self.modelo.setLightOff(1)
        self.modelo.node().adjustDrawMask(DrawMask(3), DrawMask(4), DrawMask(0))
        # luz
        self.luz=self.nodo.attachNewNode(AmbientLight("luz_ambiental"))
        self.luz.node().setColor(Cielo.ColorNoche)
        # variable externas:
        self.altitud_agua=altitud_agua
        # variable internas:
        self._periodo_actual=0 # [0,3]; noche,amanecer,dia,atardecer
        self._offset_periodo_anterior=0
        self._color_ambiente_inicial=Cielo.ColorNoche
        self._color_ambiente_final=Cielo.ColorNoche
        # init:
        self._establecer_shader()
        self.nodo.setZ(self.altitud_agua)
    
    # shader
    def update(self, posicion_sol, hora_normalizada, periodo, offset_periodo):
        # determinar periodo
        if periodo!=self._periodo_actual:
            #log.info("update cambio periodo de %i a %i; posicion_sol=[%s]; hora_normalizada=%.2f; offset_periodo=%.2f"%(self._periodo_actual, periodo, ",".join(["%.2f"%n for n in posicion_sol]), hora_normalizada, offset_periodo))
            self._periodo_actual=periodo
            self._procesar_cambio_periodo(self._periodo_actual, False)
        #
        _offset_corregido=offset_periodo
        if self._periodo_actual==1 or self._periodo_actual==3:
            if _offset_corregido>0.5:
                _offset_corregido-=0.5
                if self._offset_periodo_anterior<=0.5:
                    #log.info("update cambio subperiodo; posicion_sol=[%s]; hora_normalizada=%.2f; offset_periodo=%.2f (anterior=%.2f)"%(",".join(["%.2f"%n for n in posicion_sol]), hora_normalizada, offset_periodo, self._offset_periodo_anterior))
                    self._procesar_cambio_periodo(self._periodo_actual, True)
            _offset_corregido*=2
        # shader
        self.nodo.setShaderInput("posicion_sol", posicion_sol)
        self.nodo.setShaderInput("offset_periodo", _offset_corregido)
        # luz ambiental
        _color_luz=Vec4(self._color_ambiente_inicial*(1.0-_offset_corregido))+Vec4(self._color_ambiente_final*_offset_corregido)
        self.luz.node().setColor(_color_luz)
        #
        self._offset_periodo_anterior=offset_periodo
    
    def obtener_info(self):
        info="Cielo color_luz=%s\n"%(str(self.luz.node().getColor()))
        return info

    def _procesar_cambio_periodo(self, periodo, post_pico):
        self.nodo.setShaderInput("periodo", periodo)
        if periodo==0:
            self._color_ambiente_inicial=Cielo.ColorNoche
            self._color_ambiente_final=Cielo.ColorNoche
            self.nodo.setShaderInput("color_base_inicial", Cielo.ColorNoche)
            self.nodo.setShaderInput("color_base_final", Cielo.ColorNoche)
            self.nodo.setShaderInput("color_halo_inicial", self._color_ambiente_inicial)
            self.nodo.setShaderInput("color_halo_final", self._color_ambiente_final)
        elif periodo==1:
            if not post_pico:
                self._color_ambiente_inicial=Cielo.ColorNoche
                self._color_ambiente_final=Cielo.ColorAmanecer
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorNoche)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_halo_inicial", self._color_ambiente_inicial)
                self.nodo.setShaderInput("color_halo_final", self._color_ambiente_final)
            else:
                self._color_ambiente_inicial=Cielo.ColorAmanecer
                self._color_ambiente_final=Cielo.ColorHaloDia
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorDia)
                self.nodo.setShaderInput("color_halo_inicial", self._color_ambiente_inicial)
                self.nodo.setShaderInput("color_halo_final", self._color_ambiente_final)
        elif periodo==2:
            self._color_ambiente_inicial=Cielo.ColorHaloDia
            self._color_ambiente_final=Cielo.ColorHaloDia
            self.nodo.setShaderInput("color_base_inicial", Cielo.ColorDia)
            self.nodo.setShaderInput("color_base_final", Cielo.ColorDia)
            self.nodo.setShaderInput("color_halo_inicial", self._color_ambiente_inicial)
            self.nodo.setShaderInput("color_halo_final", self._color_ambiente_final)
        elif self._periodo_actual==3:
            if not post_pico:
                self._color_ambiente_inicial=Cielo.ColorHaloDia
                self._color_ambiente_final=Cielo.ColorAtardecer
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorDia)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_halo_inicial", self._color_ambiente_inicial)
                self.nodo.setShaderInput("color_halo_final", self._color_ambiente_final)
            else:
                self._color_ambiente_inicial=Cielo.ColorAtardecer
                self._color_ambiente_final=Cielo.ColorNoche
                self.nodo.setShaderInput("color_base_inicial", Cielo.ColorIntermedioDiaNoche)
                self.nodo.setShaderInput("color_base_final", Cielo.ColorNoche)
                self.nodo.setShaderInput("color_halo_inicial", self._color_ambiente_inicial)
                self.nodo.setShaderInput("color_halo_final", self._color_ambiente_final)

    def _establecer_shader(self):
        shader_nombre_base="cielo" #"cielo"
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/%s.v.glsl"%shader_nombre_base, fragment="shaders/%s.f.glsl"%shader_nombre_base)
        self.nodo.setShader(shader, 1)
        self.nodo.setShaderInput("altitud_agua", self.altitud_agua)
        self.nodo.setShaderInput("posicion_sol", Vec3(0, 0, 0))
        self.nodo.setShaderInput("periodo", 0)
        self.nodo.setShaderInput("offset_periodo", 0.0)
        self.nodo.setShaderInput("color_base_inicial", Cielo.ColorNoche)
        self.nodo.setShaderInput("color_base_final", Cielo.ColorNoche)
        self.nodo.setShaderInput("color_halo_inicial", Cielo.ColorNoche)
        self.nodo.setShaderInput("color_halo_final", Cielo.ColorNoche)
        
