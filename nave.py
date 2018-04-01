from panda3d.core import *
from panda3d.bullet import *
from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Nave(Personaje):
    
    def __init__(self):
        Personaje.__init__(self, "nave")

    def iniciar(self, parent_node_path, bullet_world):
        Personaje.iniciar(self, parent_node_path, bullet_world)
        #
        shp=self.cuerpo.node().getShape(0)
        self.cuerpo.node().removeShape(shp)
        self.cuerpo.node().addShape(BulletBoxShape(Vec3(0.2,0.75,0.60)))
        self.actor.setY(0.15)
    
    def _procesar_estados(self, dt):
        pass
