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
        self.btn_config = None
        self.btn_mundo = None
        self.btn_salir = None  # exit

    def iniciar(self):
        log.info("iniciar")
        #
        self.marco = DirectFrame(parent=self.contexto.base.render2d)
        self.marco["frameSize"] = (-1, 1, -1, 1)
        #
        self.btn_config = self._crear_boton()
        self.btn_config["text"] = "configuración"
        self.btn_config["command"] = self._abrir_configuracion
        self.btn_config.setPos(Vec3(0, 0, 0.25))
        #
        self.btn_mundo = self._crear_boton()
        self.btn_mundo["text"] = "mundo"
        self.btn_mundo["command"] = self._abrir_mundo
        self.btn_mundo.setPos(Vec3(0, 0, 0))
        #
        self.btn_salir = self._crear_boton()
        self.btn_salir["text"] = "salir"
        self.btn_salir["command"] = self._salir
        self.btn_salir.setPos(Vec3(0, 0, -0.25))
        #
        return True

    def terminar(self):
        log.info("terminar")

    def _crear_boton(self):  # create button
        boton = DirectButton(parent=self.marco)
        boton["frameSize"] = (-0.35, 0.35, -0.1, 0.1)
        boton["relief"] = "raised"
        boton["borderWidth"] = (0.01, 0.01)
        boton["text"] = "boton"
        boton["text_scale"] = 0.1
        return boton

    def _abrir_configuracion(self):
        log.info("_abrir_configuracion")
        #mensajero = self.contexto.base.messenger

    def _abrir_mundo(self):
        log.info("_abrir_mundo")
        #mensajero = self.contexto.base.messenger

    def _salir(self):
        log.info("_salir")
        mensajero = self.contexto.base.messenger
        mensajero.send("salir")
