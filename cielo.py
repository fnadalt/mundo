from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Cielo:
    
    # colores
    ColorNoche=LVector4(0.0, 0.0, 0.2, 1.0)
    ColorAmanecer=LVector4(0.95, 0.75, 0.2, 1.0)
    ColorDia=Vec4(0.9, 1.0, 1.0, 1.0)
    ColorAtardecer=LVector4(0.95, 0.65, 0.3, 1.0)
    
    ruta_modelo="objetos/sky_box"
    
    def __init__(self, base):
        # referencias:
        self.base=base
        # variables externas:
        self.color=Cielo.ColorNoche
        # variable internas:
        self._periodo_actual=0 # [0,3]; noche,amanecer,dia,atardecer
        self._color_inicial=Cielo.ColorNoche
        self._color_final=Cielo.ColorNoche
        self._color_actual=Cielo.ColorNoche
        self._colores_post_pico=False
        # componentes:
        # nodo
        self.nodo=self.base.cam.attachNewNode("sky_node_3d")
        #self.nodo.setColor(self._color_inicial)
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/cielo.v.glsl", fragment="shaders/cielo.f.glsl")
        self.nodo.setShader(shader)
        # modelo
        self.modelo=self.base.loader.loadModel(Cielo.ruta_modelo)
        self.modelo.reparentTo(self.nodo)
        self.modelo.setScale(400.0)
        self.modelo.setMaterialOff(1)
        self.modelo.setTextureOff(1)
        self.modelo.setLightOff(1)
        #self.modelo.setShaderOff(1)
        #self.modelo.setTwoSided(True)
        # luz
        self.luz=self.nodo.attachNewNode(AmbientLight("luz ambiental"))
        self.luz.node().setColor(Cielo.ColorNoche)
    
    def update(self, hora_normalizada, periodo, offset_periodo):
        # determinar periodo
        if periodo!=self._periodo_actual:
            self._periodo_actual=periodo
            self._establecer_colores(offset_periodo)
        # calcular color de la luz solar
        _offset=offset_periodo
        if (self._periodo_actual==1 or self._periodo_actual==3):
            if _offset>0.5:
                _offset-=0.5
                if not self._colores_post_pico:
                    self._establecer_colores(offset_periodo, self._color_actual)
                    self._colores_post_pico=True
            _offset*=2.0
        else:
            if self._colores_post_pico:
                self._colores_post_pico=False
        self._color_actual=self._color_inicial+((self._color_final-self._color_inicial)*_offset)
        #log.info("update p=%i _o=%.2f c=%s cpp=%s"%(periodo, _offset, str(self._color_actual), str(self._colores_post_pico)))
        # aplicar colores
        self.nodo.setColor(self._color_actual)
        self.luz.node().setColor(Cielo.ColorNoche*(1.0-hora_normalizada)+(self._color_actual*0.2))

    def obtener_info(self):
        info="Cielo p=%i ci=%s cf=%s\n"%(self._periodo_actual, str(self._color_inicial), str(self._color_final))
        info+="Cielo cc=%s cl=%s"%(str(self.nodo.getColor()), str(self.luz.node().getColor()))
        return info

    def _establecer_colores(self, offset_periodo, color_inicial=None):
        if self._periodo_actual==0:
            self._color_inicial=Cielo.ColorNoche if not color_inicial else color_inicial
            self._color_final=Cielo.ColorNoche
        elif self._periodo_actual==1:
            if offset_periodo<0.5:
                self._color_inicial=Cielo.ColorNoche if not color_inicial else color_inicial
                self._color_final=Cielo.ColorAmanecer
            else:
                self._color_inicial=Cielo.ColorAmanecer if not color_inicial else color_inicial
                self._color_final=Cielo.ColorDia
        elif self._periodo_actual==2:
            self._color_inicial=Cielo.ColorDia if not color_inicial else color_inicial
            self._color_final=Cielo.ColorDia
        elif self._periodo_actual==3:
            if offset_periodo<0.5:
                self._color_inicial=Cielo.ColorDia if not color_inicial else color_inicial
                self._color_final=Cielo.ColorAtardecer
            else:
                self._color_inicial=Cielo.ColorAtardecer if not color_inicial else color_inicial
                self._color_final=Cielo.ColorNoche
        #log.info("_establecer_colores p=%i offset_periodo=%.2f ci=%s cf=%s"%(self._periodo_actual, offset_periodo, str(self._color_inicial), str(self._color_final)))
