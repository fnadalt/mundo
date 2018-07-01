# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGuiGlobals import *
from direct.gui.DirectGui import *
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class EscenaInicio(DirectObject):
    """
    * configurar
    * iniciar mundo
    * salir
    """

    Nombre = "inicio"  # start

    def __init__(self, contexto):
        DirectObject.__init__(self)
        # referencias
        self.contexto = contexto
        # componentes
        self.marco = None  # frame

    def iniciar(self):
        log.info("iniciar")
        #
        self.marco = DirectFrame(parent=self.contexto.base.aspect2d)
        self.marco["frameSize"] = (-0.5, 0.5, -0.5, 0.5)
        #
        btn_mundo = self._crear_boton()
        btn_mundo["text"] = "mundo"
        btn_mundo["command"] = self._abrir_mundo
        btn_mundo.setPos(Vec3(0, 0, 0.25))
        #
        btn_config = self._crear_boton()
        btn_config["text"] = "configuración"
        btn_config["command"] = self._abrir_configuracion
        btn_config.setPos(Vec3(0, 0, 0))
        #
        btn_salir = self._crear_boton()
        btn_salir["text"] = "salir"
        btn_salir["command"] = self._salir
        btn_salir.setPos(Vec3(0, 0, -0.25))
        #
        return True

    def terminar(self):
        log.info("terminar")
        if self.marco:
            self.marco.destroy()
            self.marco = None
        #self.contexto = None  # el objeto es terminado, no destruido

    def _crear_boton(self):  # create button
        boton = DirectButton(parent=self.marco,
                             frameSize=(-0.35, 0.35, -0.1, 0.1),
                             relief="raised",
                             borderWidth=(0.01, 0.01),
                             text="botón",
                             text_scale=0.1
                            )
        return boton

    def _abrir_configuracion(self):
        log.info("_abrir_configuracion")
        #mensajero = self.contexto.base.messenger

    def _abrir_mundo(self):
        log.info("_abrir_mundo")
        self.contexto.base.messenger.send("cambiar_escena", ["mundo"])

    def _salir(self):
        log.info("_salir")
        self.contexto.base.messenger.send("salir")
