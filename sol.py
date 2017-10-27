from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Sol:

    # colores
    ColorNoche=LVector4(0.0, 0.0, 0.0, 1.0)
    ColorAmanecer=LVector4(0.95, 0.75, 0.2, 1.0)
    ColorDia=LVector4(1.0, 1.0, 0.85, 1.0)
    ColorAtardecer=LVector4(0.95, 0.65, 0.3, 1.0)

    def __init__(self, base):
        # referencias:
        self.base=base
        # componentes:
        self.pivot=None
        self.nodo=None
        self.luz=None
        # variable internas:
        self._periodo_actual=0 # [0,3]; noche,amanecer,dia,atardecer
        self._color_inicial=Sol.ColorNoche
        self._color_final=Sol.ColorNoche
        self._color_actual=Sol.ColorNoche
        self._colores_post_pico=False
        # componentes:
        # pivot de rotacion
        self.pivot=self.base.render.attachNewNode("pivot_sol")
        self.pivot.setP(10.0) # inclinacion "estacional"
        # esfera solar
        self.nodo=self.base.loader.loadModel("objetos/sol")
        self.nodo.reparentTo(self.pivot)
        self.nodo.setX(400.0)
        self.nodo.setScale(5.0)
        self.nodo.setColor(1.0, 1.0, 0.2, 1.0)
        self.nodo.setLightOff(1)
        self.nodo.setShaderOff(1)
        self.nodo.setFogOff(1)
#        self.nodo.setCompass()
#        self.nodo.setBin('background', 2)
#        self.nodo.setDepthWrite(False)
#        self.nodo.setDepthTest(False)
        # luz direccional
        self.luz=self.nodo.attachNewNode(DirectionalLight("luz solar"))
        self.luz.node().setColor(Vec4(1.0, 1.0, 0.7, 1.0))
        
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
        self._color_actual[3]=1.0
        # componentes
        self.pivot.setR(360.0 * hora_normalizada)
        self.luz.lookAt(self.pivot)
        self.luz.node().setColor(self._color_actual)
        
    def _establecer_colores(self, offset_periodo, color_inicial=None):
        if self._periodo_actual==0:
            self._color_inicial=Sol.ColorNoche if not color_inicial else color_inicial
            self._color_final=Sol.ColorNoche
        elif self._periodo_actual==1:
            if offset_periodo<0.5:
                self._color_inicial=Sol.ColorNoche if not color_inicial else color_inicial
                self._color_final=Sol.ColorAmanecer
            else:
                self._color_inicial=Sol.ColorAmanecer if not color_inicial else color_inicial
                self._color_final=Sol.ColorDia
        elif self._periodo_actual==2:
            self._color_inicial=Sol.ColorDia if not color_inicial else color_inicial
            self._color_final=Sol.ColorDia
        elif self._periodo_actual==3:
            if offset_periodo<0.5:
                self._color_inicial=Sol.ColorDia if not color_inicial else color_inicial
                self._color_final=Sol.ColorAtardecer
            else:
                self._color_inicial=Sol.ColorAtardecer if not color_inicial else color_inicial
                self._color_final=Sol.ColorNoche
        #log.info("_establecer_colores p=%i offset_periodo=%.2f ci=%s cf=%s"%(self._periodo_actual, offset_periodo, str(self._color_inicial), str(self._color_final)))
    
    def obtener_info(self):
            info="Sol roll=%.2f p=%i ci=%s cf=%s c=%s"%(self.pivot.getR(), self._periodo_actual, str(self._color_inicial), str(self._color_final), str(self.luz.node().getColor()))
            return info
