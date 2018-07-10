# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.bullet import BulletWorld, BulletDebugNode

from cntrlcam import ControladorCamara
from input import Input
from atmosfera import Atmosfera
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
        self.debug_fisica = None
        self.input = None
        self.terreno = None  # terrain
        self.estaticos = None  # static (model instances)
        self.animados = None  # animated (model instances, actors)
        self.items = None
        self.atmosfera = None  # atmosphere
        self.cntrlcam = None  # camera controller

    def iniciar(self):
        log.info("iniciar")
        b = self.contexto.base
        # física
        self.mundo_fisica.setGravity(Vec3(0, 0, -9.81))
        df = BulletDebugNode("debug_fisica")
        self.mundo_fisica.setDebugNode(df)
        self.debug_fisica = b.render.attachNewNode(df)
        self.debug_fisica.hide()
        # input
        self.input = Input(self.contexto)
        if not self.input.iniciar():
            return False
        # terreno
        self.terreno = Terreno(self.contexto, self.mundo_fisica)
        if not self.terreno.iniciar():
            return False
        # atmosfera
        self.atmosfera = Atmosfera(self.contexto)
        if not self.atmosfera.iniciar():
            return False
        # controlador camara
        self.cntrlcam = ControladorCamara(self.contexto)
        if not self.cntrlcam.iniciar():
            return False
        # luz
        luz_nodo = b.render.attachNewNode(PointLight("luz"))
        luz_nodo.setZ(10)
        b.render.setLight(luz_nodo)
        #
        pelota = b.loader.loadModel("modelos/items/pelota.egg")
        pelota.reparentTo(b.render)
        pelota.setPos(0, 0.5, 0.5)
        b.messenger.send("establecer_objetivo", [pelota])
        # eventos
        self.accept("control-e", b.messenger.toggleVerbose)
        self.accept("escape-up", self._salir)
        # tasks
        b.taskMgr.add(self._update, "Mundo_update")
        #
        return True

    def terminar(self):
        log.info("terminar")
        # camara
        if self.cntrlcam:
            self.cntrlcam.terminar()
            self.cntrlcam = None
        # atmosfera
        if self.atmosfera:
            self.atmosfera.terminar()
            self.atmosfera = None
        # terreno
        if self.terreno:
            self.terreno.terminar()
            self.terreno = None
        # input
        if self.input:
            self.input.terminar()
            self.input = None
        # hijos restantes (remaining children)
        for child in self.contexto.base.render.getChildren():
            child.removeNode()
        # eventos
        self.ignoreAll()
        # tasks
        self.contexto.base.taskMgr.remove("Mundo_update")

    def _salir(self):
        self.contexto.base.messenger.send("cambiar_escena", ["inicio"])

    def _update(self, task):
        # física
        dt = self.contexto.base.taskMgr.globalClock.getDt()
        self.mundo_fisica.doPhysics(dt, 10, 1.0 / 180.0)
        #
        return task.cont
