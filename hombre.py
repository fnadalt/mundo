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

    # estados
    # capa 0
    EstadoConduciendo=101

    def __init__(self):
        Personaje.__init__(self, "male")
        # variables control
        self.conduciendo=False
    
    def construir(self, parent_node_path, bullet_world):
        Personaje.construir(self, parent_node_path, bullet_world, Hombre.Partes)
        # joints
        self.handR=self.actor.exposeJoint(None, "modelRoot", "hand.R")
        # actor
        self.actor.setScale(0.06)

    def _definir_estado(self, idx_capa):
        estado_actual=self._estado_capa[idx_capa]
        estado_nuevo=Personaje._definir_estado(self, idx_capa)
        # capa 0
        if idx_capa==0:
            # conduciendo
            if estado_actual==Hombre.EstadoConduciendo:
                #->quieto
                if not self.conduciendo:
                    estado_nuevo=Personaje.EstadoQuieto
            # (cualquiera)
            if self.conduciendo:
                #->conduciendo
                estado_nuevo=Hombre.EstadoConduciendo
        # capa 1
        elif idx_capa==1:
            pass
        return estado_nuevo

    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        Personaje._cambio_estado(self, idx_capa, estado_previo, estado_nuevo)
        # capa 0
        if estado_nuevo==Personaje.EstadoQuieto:
            self.actor.pose("sostener", 0, partName="brazo.R")
            self.actor.loop("quieto", partName="torso")
            self.actor.loop("quieto", partName="pelvis")
        elif estado_nuevo==Personaje.EstadoCaminando:
            #self.actor.setPlayRate(1.0, "caminar") # |4.0
            self.actor.pose("sostener", 0, partName="brazo.R")
            self.actor.loop("caminar", partName="torso")
            self.actor.loop("caminar", partName="pelvis")
        elif estado_nuevo==Personaje.EstadoCorriendo:
            self.actor.setPlayRate(1.5, "correr")
            self.actor.pose("sostener", 0, partName="brazo.R")
            self.actor.loop("correr", partName="torso")
            self.actor.loop("correr", partName="pelvis")
        elif estado_nuevo==Hombre.EstadoConduciendo:
            self.actor.pose("ride", 0)
        # capa 1
        #
