# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.bullet import BulletWorld
from input import Input

# log
import logging
log = logging.getLogger(__name__)


class EscenaMundo(DirectObject):
    """
    * escena del mundo virtual
    """

    Nombre = "mundo"  # world

    def __init__(self, contexto):
        DirectObject.__init__(self)
        # referencias
        self.contexto = contexto
        # componentes
        self.mundo_fisica = BulletWorld()  # physics world
        self.input = None
        self.atmosfera = None  # atmosphere
        self.terreno = None  # terrain
        self.estaticos = None  # static (model instances)
        self.animados = None  # animated (model instances)
        self.items = None

    def iniciar(self):
        log.info("iniciar")
        # física
        self.mundo_fisica.setGravity(Vec3(0, 0, -9.81))
        # input
        self.input = Input(self.contexto)
        if not self.input.iniciar():
            return False
        # eventos
        self.accept("escape-up", self._salir)
        #
        return True

    def terminar(self):
        log.info("terminar")
        # input
        if self.input:
            self.input.terminar()
            self.input = None
        # eventos
        self.ignoreAll()
        #
        #self.contexto = None

    def _salir(self):
        self.contexto.base.messenger.send("cambiar_escena", ["inicio"])
