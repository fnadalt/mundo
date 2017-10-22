from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Sol:
    
    def __init__(self, base):
        # referencias:
        self.base=base
        # componentes:
        self.pivot=None
        self.nodo=None
        self.luz=None
        # variable internas:
        self._datos_periodos=dict() # {periodo:[color,hora_max,duracion,prox_periodo], ...}
        # componentes:
        # pivot de rotacion
        self.pivot=self.base.render.attachNewNode("pivot_sol")
        self.pivot.setP(10.0) # inclinacion "estacional"
        # esfera solar
        self.nodo=self.base.loader.loadModel("objetos/sol")
        self.nodo.reparentTo(self.pivot)
        self.nodo.setX(300.0)
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
        _luz=DirectionalLight("sol_d")
        _luz.setColor(Vec4(1.0, 1.0, 0.7, 1.0))
        self.luz=self.nodo.attachNewNode(_luz)

    def update(self, hora_normalizada):
        # componentes
        self.pivot.setR(360.0 * hora_normalizada)
        self.luz.lookAt(self.pivot)
        self.luz.node().setColor(LVector4())

    def obtener_info(self):
        info="Sol roll=%.2f"%(self.pivot.getR())
        return info
