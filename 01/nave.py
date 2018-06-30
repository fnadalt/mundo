from panda3d.core import *
from panda3d.bullet import *
from personaje import Personaje

from input import InputMapper

import logging
log=logging.getLogger(__name__)

class Nave(Personaje):
    
    # estados
    # capa 0
    EstadoReposo=Personaje.EstadoClaseDerivadaBase+1
    
    def __init__(self):
        Personaje.__init__(self, "nave")

    def iniciar(self, parent_node_path, bullet_world):
        Personaje.iniciar(self, parent_node_path, bullet_world)
        #
        self.actor.setY(0.15)
        #
        self._estado_capa[0]=Nave.EstadoReposo
    
    def _generar_cuerpo_fisica(self):
        shp=BulletBoxShape(Vec3(0.2,0.75,0.60))
        rb=BulletRigidBodyNode(self.prefijo_cuerpo_personaje+self.clase)
        rb.setMass(1000.0)
        rb.addShape(shp)
        rb.setKinematic(False)
        rb.setStatic(True)
        self._ajuste_altura=rb.getShapeBounds().getRadius()
        return rb

    def _definir_estado(self, idx_capa):
        return Nave.EstadoReposo
    
    def _cambio_params(self, params_previos, params_nuevos):
        pass

    def _procesar_estados(self, dt):
        pass
    
    def _procesar_contactos(self):
        #
        if self.cuerpo.node().isStatic():
            return
