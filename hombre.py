from panda3d.core import *
from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Hombre(Personaje):

##    # controles?
#    controles={
#                    "w":"avanzar", "s":"retroceder", "a":"desplazar_izquierda", "d":"desplazar_derecha", 
#                    "q":"girar_izquierda", "e":"girar_derecha", "wheel_up":"acercar_camara", "wheel_down":"alejar_camara", 
#                    "mouse1-up":"mirar_adelante", "space":"saltar"
#                    }

    # partes
    Partes=[("torso", ["spine"], ["shoulder.R", "thigh.L", "thigh.R"]), 
            ("pelvis", ["main", "hips", "thigh.L", "thigh.R"], ["spine"]), 
            ("brazo.R", ["shoulder.R"], [])
            ]

    def __init__(self):
        Personaje.__init__(self, "male")
    
    def iniciar(self, parent_node_path, bullet_world):
        Personaje.iniciar(self, parent_node_path, bullet_world, Hombre.Partes)
        # joints
        self.manoD=self.actor.exposeJoint(None, "modelRoot", "hand.R")
        self.manoI=self.actor.exposeJoint(None, "modelRoot", "hand.L")
        # actor
        self.actor.setScale(0.06)

    def _definir_estado(self, idx_capa):
        #
        estado_actual=self._estado_capa[idx_capa]
        estado_nuevo=Personaje._definir_estado(self, idx_capa)
        #
        if idx_capa==0:
            # quieto
            if estado_actual==Personaje.EstadoQuieto:
                if Personaje.EstadoAgarrando in self.objetos_estados:
                    #-> conduciendo
                    nodo_objeto=self.objetos_estados[Personaje.EstadoAgarrando]
                    if nodo_objeto.getName().endswith("_nave"):
                        estado_nuevo=Personaje.EstadoConduciendo
            # conduciendo
            elif estado_actual==Personaje.EstadoConduciendo:
                if not Personaje.EstadoAgarrando in self.objetos_estados:
                    #-> quieto
                    estado_nuevo=Personaje.EstadoQuieto
        #
        return estado_nuevo

    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        Personaje._cambio_estado(self, idx_capa, estado_previo, estado_nuevo)
        # capa 0
        if idx_capa==0:
            if estado_nuevo==Personaje.EstadoQuieto:
                self.actor.loop("quieto", partName="brazo.R")
                self.actor.loop("quieto", partName="torso")
                self.actor.loop("quieto", partName="pelvis")
            elif estado_nuevo==Personaje.EstadoCaminando:
                self.actor.loop("caminar", partName="brazo.R")
                self.actor.loop("caminar", partName="torso")
                self.actor.loop("caminar", partName="pelvis")
            elif estado_nuevo==Personaje.EstadoCorriendo:
                self.actor.setPlayRate(1.5, "correr")
                self.actor.loop("correr", partName="brazo.R")
                self.actor.loop("correr", partName="torso")
                self.actor.loop("correr", partName="pelvis")
            elif estado_nuevo==Personaje.EstadoConduciendo:
                self.actor.pose("ride", 0)
        # capa 1
        elif idx_capa==1:
            pass    
        #

    def _agarrar(self):
        if not Personaje.EstadoAgarrando in self.objetos_estados:
            nodo_objeto=NodePath(self.contactos[0].getNode1())
            if nodo_objeto.getName().endswith("_nave"):
                log.debug("_agarrar %s"%(nodo_objeto.getName()))
                self.objetos_estados[Personaje.EstadoAgarrando]=nodo_objeto
                return True
        return False
    
    def _soltar(self):
        if Personaje.EstadoAgarrando in self.objetos_estados:
            nodo_objeto=self.objetos_estados[Personaje.EstadoAgarrando]
            if nodo_objeto.getName().endswith("_nave"):
                log.debug("_soltar %s"%(nodo_objeto.getName()))
                del self.objetos_estados[Personaje.EstadoAgarrando]
                self.cuerpo.reparentTo(nodo_objeto.getParent())
                self.cuerpo.setPos(nodo_objeto.getX(), nodo_objeto.getY(), self.altitud_suelo)
                self.cuerpo.setHpr(nodo_objeto.getHpr())
                return True
        return False
