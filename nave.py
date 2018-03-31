#from panda3d.core import *
from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Nave(Personaje):
    
    def __init__(self):
        Personaje.__init__(self, "nave")

    def construir(self, parent_node_path, bullet_world):
        Personaje.construir(self, parent_node_path, bullet_world)
