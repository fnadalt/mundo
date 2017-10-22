from panda3d.core import *

class Cielo:
    
    Color=Vec4(0.9, 1.0, 1.0, 1.0)
    TinteBase=Vec4(1.0, 1.0, 1.0, 1.0)
    TinteMediodia=Vec4(1.1, 1, 0.3, 1.0)
    TinteMedianoche=Vec4(0, 0, 0.1, 1.0)
    
    ruta_modelo="objetos/sky_box"
    
    def __init__(self, base):
        self.base=base
        #
        #return # paque no funque
        # componentes:
        # nodo
        self.nodo=self.base.cam.attachNewNode("sky_node")
        # modelo
        self.modelo=self.base.loader.loadModel(Cielo.ruta_modelo)
        self.modelo.reparentTo(self.nodo)
        self.modelo.setScale(400.0)
        self.modelo.setMaterialOff(1)
        self.modelo.setTextureOff(1)
        self.modelo.setLightOff(1)
        self.modelo.setShaderOff(1)
        self.modelo.setTwoSided(True)
        self.modelo.setColor(Cielo.Color)
        # variables externas:
        self.tinte=Cielo.TinteBase
    
    def update(self, hora):
        # calcular tinte
        if hora>=0.0 and hora<6.0:
            self.tinte=Cielo.TinteMedianoche+(Cielo.TinteBase-Cielo.TinteMedianoche)*(hora/6.0)
        elif hora>=6.0 and hora<12.0:
            self.tinte=Cielo.TinteBase+(Cielo.TinteMediodia-Cielo.TinteBase)*((hora-6.0)/6.0)
        elif hora>=12.0 and hora<18.0:
            self.tinte=Cielo.TinteMediodia+(Cielo.TinteBase-Cielo.TinteMediodia)*((hora-12.0)/6.0)
        elif hora>=18.0 and hora<24.0:
            self.tinte=Cielo.TinteBase+(Cielo.TinteMedianoche-Cielo.TinteBase)*((hora-18.0)/6.0)
        self.tinte[3]=1.0
        # aplicar tinte
        self.nodo.setColorScale(self.tinte)

    def obtener_info(self):
        info="Cielo tinte=%s"%(str(self.tinte))
        return info
