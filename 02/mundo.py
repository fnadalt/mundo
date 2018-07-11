# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
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
        self.texto_info = None  # info text
        self.debug_hud = None
        # parametros
        self.cargar_terreno = True
        self.cargar_atmosfera = True

    def iniciar(self):
        log.info("iniciar")
        self._establecer_parametros()
        #
        b = self.contexto.base
        # física
        self.mundo_fisica.setGravity(Vec3(0, 0, -9.81))
        df = BulletDebugNode("debug_fisica")
        self.mundo_fisica.setDebugNode(df)
        self.debug_fisica = b.render.attachNewNode(df)
        self.debug_fisica.hide()
        self.accept("f11", self._toggle_debug_fisica)
        # input
        self.input = Input(self.contexto)
        if not self.input.iniciar():
            return False
        # terreno
        if self.cargar_terreno:
            self.terreno = Terreno(self.contexto, self.mundo_fisica)
            if not self.terreno.iniciar():
                return False
        # atmosfera
        if self.cargar_atmosfera:
            self.atmosfera = Atmosfera(self.contexto)
            if not self.atmosfera.iniciar():
                return False
        # controlador camara
        self.cntrlcam = ControladorCamara(self.contexto)
        if not self.cntrlcam.iniciar():
            return False
        # info texto
        self.info_texto = OnscreenText(
            text="cámara: f1:libre f2:1ºpers f3:3ºpers\n"
                 "debug física: f11")
        # debug hud
        self.debug_hud = OnscreenText(
            parent=b.a2dTopLeft,
            text="Debug?",
            pos=(0, -0.1),
            scale=0.05,
            align=TextNode.ALeft
            )
        # pelota (ball)
        pelota = b.loader.loadModel("modelos/items/pelota.egg")
        pelota.reparentTo(b.render)
        pelota.setPos(0, 0.5, 15)
        b.messenger.send("establecer_objetivo", [pelota])
        # eventos
        self.accept("escape-up", self._salir)
        # tasks
        b.taskMgr.doMethodLater(
            0.1,
            self._update_debug_hud,
            "Mundo_update_debug_hud")
        b.taskMgr.add(self._update, "Mundo_update")
        #
        return True

    def terminar(self):
        log.info("terminar")
        # camara
        if self.cntrlcam:
            self.cntrlcam.terminar()
            self.cntrlcam = None
        # debug hud
        if self.debug_hud:
            self.debug_hud.destroy()
            self.debug_hud = None
        # info texto
        if self.info_texto:
            self.info_texto.destroy()
            self.info_texto = None
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
        # física
        self.mundo_fisica.clearDebugNode()
        self.debug_fisica.removeNode()
        # eventos
        self.ignoreAll()
        # tasks
        self.contexto.base.taskMgr.remove("Mundo_update_debug_hud")
        self.contexto.base.taskMgr.remove("Mundo_update")

    def _establecer_parametros(self):
        log.info("_establecer_parametros")
        try:
            cfg = self.contexto.config["mundo"]
            self.cargar_terreno = cfg["terreno"]
            self.cargar_atmosfera = cfg["atmosfera"]
        except ValueError as e:
            log.exception("error en el análisis de la configuración: " + str(e))

    def _toggle_texto_info(self):
        pass

    def _toggle_debug_fisica(self):
        if self.debug_fisica.isHidden():
            self.debug_fisica.show()
        else:
            self.debug_fisica.hide()

    def _salir(self):
        self.contexto.base.messenger.send("cambiar_escena", ["inicio"])

    def _update_debug_hud(self, task):
        info = "Debug\n"
        info += self.input.obtener_info()
        self.debug_hud["text"] = info
        return task.again

    def _update(self, task):
        # física
        dt = self.contexto.base.taskMgr.globalClock.getDt()
        self.mundo_fisica.doPhysics(dt, 10, 1.0 / 180.0)
        #
        return task.cont
