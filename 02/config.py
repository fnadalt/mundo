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
        # variables internas (internal variables)
        self._rel_aspecto = 4 / 3  # screen aspect ratio

    def iniciar(self):
        log.info("iniciar")
        # variables
        self._rel_aspecto = self.contexto.base.getAspectRatio()
        # marco
        self.marco = DirectFrame(
            parent=self.contexto.base.aspect2d,
            frameSize=(0, 2 * self._rel_aspecto, -1, 1),
            frameColor=(0, 0.5, 0.5, 1),
            pos=(-self._rel_aspecto, 0, 0)
            )
        # secciones
        self.secciones = DirectFrame(
            parent=self.marco,
            pos=(0, 0, 0),
            frameSize=(0, 1, -1, 1),
            frameColor=(0.35, 0.1, 0, 1))
        # título
        DirectLabel(
            parent=self.secciones,
            text="configuración",
            scale=0.125,
            pos=(0.5, 0, 0.9),
            frameColor=(0, 0, 0, 0),
            text_fg=(0.9, 0.7, 0.6, 1))
        # botones
        boton = self._crear_boton_seccion("aplicación")
        boton.setPos(0.5, 0, 0.7)
        boton = self._crear_boton_seccion("mundo")
        boton.setPos(0.5, 0, 0.4)
        boton = self._crear_boton_seccion("input")
        boton.setPos(0.5, 0, 0.1)
        boton = self._crear_boton_seccion("terreno")
        boton.setPos(0.5, 0, -0.2)
        # eventos
        self.accept("aspectRatioChanged", self._ajustar_rel_aspecto)
        #
        return True

    def terminar(self):
        log.info("terminar")
        # eventos
        self.ignoreAll()
        # marco
        if self.marco:
            self.marco.destroy()
            self.marco = None

    def _ajustar_rel_aspecto(self):
        self._rel_aspecto = self.contexto.base.getAspectRatio()
        log.debug("_ajustar_rel_aspecto -> %.3f" % self._rel_aspecto)
        self.marco.setPos(-self._rel_aspecto, 0, 0)
        self.marco["frameSize"] = (0, 2 * self._rel_aspecto, -1, 1)

    def _crear_boton_seccion(self, texto):  # create section button
        boton = DirectButton(parent=self.marco,
                             frameSize=(-0.35, 0.35, -0.1, 0.1),
                             frameColor=(0.35, 0.35, 0.1, 1),
                             relief="raised",
                             borderWidth=(0.01, 0.01),
                             text=texto,
                             text_scale=0.1,
                             text_fg=(0.5, 0.5, 0.3, 1)
                            )
        return boton
