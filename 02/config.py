# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGuiGlobals import *
from direct.gui.DirectGui import *
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class EscenaConfig(DirectObject):
    """
    * configuración
    """

    Nombre = "config"

    def __init__(self, contexto):
        DirectObject.__init__(self)
        # referencias
        self.contexto = contexto
        # componentes
        self.marco = None  # frame
        self.secciones = None
        self.paneles_config = dict()

    def iniciar(self):
        log.info("iniciar")
        # marco
        self.marco = DirectFrame(parent=self.contexto.base.aspect2d)
        self.marco["frameSize"] = (-1.0, 1.0, -1.0, 1.0)
        # secciones
        self.secciones = DirectFrame(parent=self.marco, pos=(-1, 0, 1))
        self.secciones["frameSize"] = (0.0, 0.75, 0, -2.0)
        self.secciones["frameColor"] = (0.35, 0.1, 0, 1)
        #
        DirectLabel(
            parent=self.secciones,
            text="hola",
            scale=0.1,
            pos=(0.1, 0, -1),
            frameColor=(0, 0, 0, 0))
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
