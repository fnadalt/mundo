from configuracion import Configuracion
from datos import Datos

from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Sistema0:
    
    def __init__(self):
        # componentes
        self.configuracion=None
        self.directorio=None
        self.datos=None
        self.reloj=None
        self.cursor=Vec3()
        # variables externas
        self.tamano_parcela=64
        self.radio_extension_terreno_minimo=2 # num parcelas
        self.radio_extension_terreno_optimo=6 # num parcelas
        # variables internas
        self._iniciado=False
    
    def iniciar(self):
        log.info("iniciar")
        #
        if self._iniciado:
            log.error("_iniciado=True")
            return False
        # configuracion
        self.configuracion=Configuracion()
        if not self.configuracion.iniciar():
            return False
        # datos
        self.datos=Datos()
        self.datos.tamano_parcela=self.tamano_parcela
        self.datos.radio_extension_terreno_minimo=self.radio_extension_terreno_minimo
        self.datos.radio_extension_terreno_optimo=self.radio_extension_terreno_optimo
        if not self.datos.iniciar():
            return False
        #
        return True
    
    def terminar(self):
        log.info("terminar")
        if self.datos:
            self.datos.terminar()
            self.datos=None
        if self.configuracion:
            self.configuracion.terminar()
            self.configuracion=None

if __name__=="__main__":
    sistema=Sistema0()
    sistema.iniciar()
    sistema.terminar()
