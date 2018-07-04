# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class ControladorCamara(DirectObject):  # CameraController

    # tipos (types)
    TipoLibre = 0  # free
    TipoPrimeraPersona = 1  # first person
    TipoTerceraPersona = 2  # third person

    def __init__(self, contexto):
        # referencias
        self.contexto = contexto
        self.objetivo = contexto.base.render
        # componentes
        self.nodo = None
        # parámetros
        self.dist_rot_min = 0.25
        self.dist_rot_max = 0.50
        # variables externas (external variables)
        self.tipo = ControladorCamara.TipoTerceraPersona
        self.factores_rot = Vec2()  # rotation factors

    def iniciar(self):
        log.info("iniciar")
        # referencias
        self.establecer_objetivo(None)
        # nodo
        render = self.contexto.base.render
        self.nodo = render.attachNewNode("ControladorCamara_nodo")
        self.contexto.base.camera.reparentTo(self.nodo)
        # variables
        self.factores_rot = Vec2(2, -1)
        # tipo
        self.establecer_tipo(self.tipo)
        # eventos
        self.accept("f1",
            self.establecer_tipo, [ControladorCamara.TipoLibre])
        self.accept("f2",
            self.establecer_tipo, [ControladorCamara.TipoPrimeraPersona])
        self.accept("f3",
            self.establecer_tipo, [ControladorCamara.TipoTerceraPersona])
        self.accept("wheel_up", self._ajustar_distancia, [1])
        self.accept("wheel_down", self._ajustar_distancia, [-1])
        self.accept("establecer_objetivo", self.establecer_objetivo)
        #
        return True

    def terminar(self):
        log.info("terminar")
        #
        self.establecer_objetivo(None)
        # eventos
        self.ignoreAll()
        # tasks
        taskMgr = self.contexto.base.taskMgr
        if taskMgr.hasTaskNamed("ControladorCamara_update"):
            taskMgr.remove("ControladorCamara_update")

    def establecer_tipo(self, tipo):
        log.info("establecer_tipo %i" % tipo)
        taskMgr = self.contexto.base.taskMgr
        camara = self.contexto.base.camera
        if tipo == ControladorCamara.TipoLibre:
            if taskMgr.hasTaskNamed("ControladorCamara_update"):
                taskMgr.remove("ControladorCamara_update")
            self.contexto.base.enableMouse()
            self.tipo = tipo
        elif tipo == ControladorCamara.TipoPrimeraPersona or \
            tipo == ControladorCamara.TipoTerceraPersona:
            self.contexto.base.disableMouse()
            camara.setPos(0, 0, 0)
            camara.setHpr(0, 0, 0)
            self.nodo.setHpr(0, 0, 0)
            if not taskMgr.hasTaskNamed("ControladorCamara_update"):
                taskMgr.add(self._update, "ControladorCamara_update")
            if tipo == ControladorCamara.TipoTerceraPersona:
                camara.setY(-5)
                self.nodo.setP(-15)
            self.tipo = tipo
        else:
            log.error("tipo no reconocido %i" % tipo)

    def establecer_objetivo(self, objetivo):
        if objetivo:
            self.objetivo = objetivo
        else:
            self.objetivo = self.contexto.base.render

    def _ajustar_distancia(self, sentido):
        if self.tipo == ControladorCamara.TipoTerceraPersona:
            camara = self.contexto.base.camera
            y = camara.getY()
            y += 2 * sentido
            y = min(max(-200, y), 0)
            camara.setY(y)

    def _update(self, task):
        self.nodo.setPos(self.objetivo.getPos() + Vec3(0, 0, 1))
        mouse_pos = Vec2.zero()
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            mouse_pos = Vec2(x, y)
        h, p = self.nodo.getH(), self.nodo.getP()
        dh = max(-self.dist_rot_max, min(self.dist_rot_max, mouse_pos.getX()))
        dp = max(-self.dist_rot_max, min(self.dist_rot_max, mouse_pos.getY()))
        if abs(dh) < self.dist_rot_min or abs(dh) > (self.dist_rot_max - 0.01):
            dh = 0
        if abs(dp) < self.dist_rot_min or abs(dp) > (self.dist_rot_max - 0.01):
            dp = 0
        h += -dh * self.factores_rot.getX()
        p += -dp * self.factores_rot.getY()
        self.nodo.setHpr(h, p, 0)
        #
        return task.cont
