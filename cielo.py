from panda3d.core import *

class Cielo:
    
    color=Vec4(0.7, 1.0, 1.0, 1.0)
    
    ruta_modelo="objetos/sky_box"
    #ruta_modelo="terrain/models/rgbCube"
    
    def __init__(self, base):
        self.base=base
        #
        #return # paque no funque
        self.nodo=self.base.cam.attachNewNode("sky_node")
        self.sky_box=self.base.loader.loadModel(Cielo.ruta_modelo)
        self.sky_box.reparentTo(self.nodo)
        self.sky_box.setScale(400.0)
        self.sky_box.setMaterialOff(1)
        self.sky_box.setTextureOff(1)
        self.sky_box.setLightOff(1)
        self.sky_box.setShaderOff(1)
        self.sky_box.setTwoSided(True)
        self.sky_box.setColor(Cielo.color)
