# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from contexto import Contexto
from inicio import EscenaInicio  # start scene

# Log
import logging
log = logging.getLogger(__name__)


class Aplicacion(DirectObject):
    """
    * inicia contexto
    * administra escenas
    """

    def __init__(self):
        DirectObject.__init__(self)
        # referencias
        self.contexto = Contexto()
        # componentes
        self.escenas = dict()  # scenes
        self.escena_actual = None  # current scene

    """
    iniciar(), patrón de diseño para objetos de esta aplicación.
    Devuelve boolean.
    """
    def iniciar(self):  # init
        logging.basicConfig(level=logging.DEBUG)
        log.info("iniciar")
        # contexto
        if not self.contexto.iniciar():
            return False
        # configuración de aplicación (app config)
        config_aplicacion = self.contexto.config["aplicacion"]
        # escenas basicas (basic scenes)
        escenas_basicas = config_aplicacion["escenas_basicas"].split(" ")
        for nombre_escena in escenas_basicas:
            log.debug("escena '%s'" % nombre_escena)
            escena = self.__obtener_escena(nombre_escena)
            if not escena:
                return False
            self.escenas[nombre_escena] = escena
        #
        nombre_escena = config_aplicacion["escena_primera"]
        self._cambiar_escena(nombre_escena)
        # eventos
        self.accept("cambiar_escena", self._cambiar_escena)
        self.accept("salir", self.terminar)
        # main loop
        self.contexto.base.run()
        #
        return True

    """
    terminar(), patrón de diseño para objetos de esta aplicación.
    """
    def terminar(self):  # terminate
        log.info("terminar")
        #
        if self.escena_actual:
            self.escena_actual.terminar()
            self.escena_actual = None
        for nombre, escena in list(self.escenas.items()):
            if escena:
                escena.terminar()
                self.escenas[nombre] = None
        #
        base = self.contexto.base
        self.contexto.terminar()
        base.finalizeExit()

    """
    _cambiar_escena() se llama en respuesta a un evento.
    El nombre inicia con _ para indicar que es un método privado.
    """
    def _cambiar_escena(self, nombre_escena):  # change scene
        log.info("cambiar escena a '%s'" % nombre_escena)
        # escena nueva (new scene)
        escena = self.__obtener_escena(nombre_escena)
        if not escena:
            return
        if not escena.iniciar():
            return
        # escena actual? terminar
        if self.escena_actual:
            self.escena_actual.terminar()
            self.escena_actual = None
        #
        self.escena_actual = escena

    """
    __obtener_escena() devuelve una escena sin iniciar, según nombre.
    El nombre inicia con __ para indicar que corresponde a un método a
    ser llamado desde métodos privados.
    Los errores se reportan en el método en que tuvo lugar.
    """
    def __obtener_escena(self, nombre_escena):  # get scene
        escena = None
        if nombre_escena in self.escenas:
            escena = self.escenas[nombre_escena]
        else:
            if nombre_escena == EscenaInicio.Nombre:
                escena = EscenaInicio(self.contexto)
            else:
                log.error("__obtener_escena('%s')" % nombre_escena)
        return escena
