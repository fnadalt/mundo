# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.bullet import BulletWorld

# log
import logging
log = logging.getLogger(__name__)


class EscenaMundo(DirectObject):
    """
    * escena del mundo virtual
    """

    Nombre = "mundo"  # world

    def __init__(self, contexto):
        # referencias
        self.contexto = contexto
        # componentes
        self.mundo_fisico = BulletWorld()
        self.atmosfera = None  # atmosphere
        self.terreno = None  # terrain
        self.agua = None  # water
        self.estaticos = None  # static (model instances)
        self.animados = None  # animated (model instances)
        self.items = None

    def iniciar(self):
        log.info("iniciar")
        # fisica
        self.mundo_fisico.setGravity(Vec3(0, 0, -9.81))
        # eventos
        self.accept("escape-up", self._salir)
        #
        return True

    def terminar(self):
        log.info("terminar")
        # eventos
        self.ignoreAll()
        #
        #self.contexto = None

    def _salir(self):
        self.contexto.base.messenger.send("cambiar_escena", ["inicio"])

