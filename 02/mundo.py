# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.bullet import BulletWorld

from cntrlcam import ControladorCamara
from input import Input
from terreno import Terreno

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
        self.cntrlcam = None  # camera controller

    def iniciar(self):
        log.info("iniciar")
        # física
        self.mundo_fisica.setGravity(Vec3(0, 0, -9.81))
        # input
        self.input = Input(self.contexto)
        if not self.input.iniciar():
            return False
        # terreno
        self.terreno = Terreno(self.contexto)
        if not self.terreno.iniciar():
            return False
        # controlador camara
        self.cntrlcam = ControladorCamara(self.contexto)
        if not self.cntrlcam.iniciar():
            return False
        # luz
        luz_nodo = self.contexto.base.render.attachNewNode(PointLight("luz"))
        luz_nodo.setZ(10)
        self.contexto.base.render.setLight(luz_nodo)
        #
        pelota = self.contexto.base.loader.loadModel("modelos/items/pelota.egg")
        pelota.reparentTo(self.contexto.base.render)
        pelota.setPos(0, 0.5, 0.5)
        self.cntrlcam.establecer_objetivo(pelota)
        # eventos
        self.accept("control-e", self.contexto.base.messenger.toggleVerbose)
        self.accept("escape-up", self._salir)
        #
        return True

    def terminar(self):
        log.info("terminar")
        # camara
        if self.cntrlcam:
            self.cntrlcam.terminar()
            self.cntrlcam = None
        # terrreno
        if self.terreno:
            self.terreno.terminar()
            self.terreno = None
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
