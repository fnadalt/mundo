from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Hombre(Personaje):

    controles={
                    "w":"avanzar", "s":"retroceder", "a":"desplazar_izquierda", "d":"desplazar_derecha", 
                    "q":"girar_izquierda", "e":"girar_derecha", "wheel_up":"acercar_camara", "wheel_down":"alejar_camara", 
                    "mouse1-up":"mirar_adelante", "space":"saltar"
                    }

    def __init__(self, mundo):
        Personaje.__init__(self, mundo, "hombre")
        #
