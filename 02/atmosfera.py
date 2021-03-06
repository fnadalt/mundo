# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

import math

# log
import logging
log = logging.getLogger(__name__)


class Atmosfera(DirectObject):
    """
    * administra la epoca (hora, año, etc...)
    * contiene cielo, sol (con su rig), agua, etc
    * contiene AmbientLight y DirectionalLight (sol)
    * se mueve en referencia al objetivo
    """

    def __init__(self, contexto):
        # referencias
        self.contexto = contexto
        self.objetivo = contexto.base.render
        # componentes
        self.nodo = None
        self.cielo = None  # sky
        self.luz_ambiental = None  # ambient light
        self.sol_rig = None
        self.sol_nodo = None  # sun node
        self.sol_luz = None  # sun light
        self.plano_agua = None  # water plane
        # parametros
        self.segundos = 0.0  # elapsed seconds
        self.segundos_dia = 60  # seconds/day
        # variables externas (external variables)
        self.hora_normalizada = 0.0  # normalized hour
        # variables internas (internal variables)
        self._tiempo_anterior = 0.0  # (previous time)

    def iniciar(self):
        log.info("iniciar")
        b = self.contexto.base
        # nodo
        self.nodo = b.render.attachNewNode("atmosfera")
        # cielo
        self.cielo = b.loader.loadModel("modelos/atmosfera/sky_box.egg")
        self.cielo.reparentTo(b.render)
        self.cielo.setScale(10)
        self.cielo.setCompass()
        # luz ambiental
        luz_ambiental = AmbientLight("luz_ambiental")
        luz_ambiental.setColor((0.1, 0.1, 0.2, 1.0))
        self.luz_ambiental = self.nodo.attachNewNode(luz_ambiental)
        b.render.setLight(self.luz_ambiental)
        # sol
        self.sol_rig = self.nodo.attachNewNode("sol_rig")
        self.sol_nodo = b.loader.loadModel("modelos/atmosfera/sol.egg")
        self.sol_nodo.reparentTo(self.sol_rig)
        self.sol_nodo.setY(100)
        self.sol_luz = self.sol_nodo.attachNewNode(DirectionalLight("sol"))
        self.sol_luz.lookAt(self.nodo)
        self.sol_luz.node().setColor((0.8, 0.8, 1.0, 1.0))
        self.sol_luz.node().setShadowCaster(True, 256, 256)
        b.render.setLight(self.sol_luz)
        # agua
        self.agua = b.loader.loadModel("modelos/atmosfera/agua.egg")
        self.agua.reparentTo(self.nodo)
        # eventos
        self.accept("establecer_objetivo", self.establecer_objetivo)
        # tasks
        self.contexto.base.taskMgr.doMethodLater(
            0.166,
            self._update,
            "Atmosfera_update"
            )
        #
        return True

    def terminar(self):
        log.info("terminar")
        # tasks
        self.contexto.base.taskMgr.remove("Atmosfera_update")
        # eventos
        self.ignoreAll()
        #
        self.establecer_objetivo(None)
        # cielo
        if self.cielo:
            self.cielo.removeNode()
            self.cielo = None
        # nodo
        if self.nodo:
            self.contexto.base.render.clearLight(self.luz_ambiental)
            self.contexto.base.render.clearLight(self.sol_luz)
            self.luz_ambiental = None
            self.sol_rig = None
            self.sol_nodo = None
            self.sol_luz = None
            self.plano_agua = None
            self.nodo.removeNode()
            self.nodo = None

    def establecer_objetivo(self, objetivo):
        if objetivo:
            self.objetivo = objetivo
        else:
            self.objetivo = self.contexto.base.render

    def obtener_info(self):
        info = "Atmosfera hora=%s" \
            % (self.obtener_hora_formateada())
        return info

    def obtener_hora_formateada(self):  # get formatted time
        hora = 7 + 24 * self.hora_normalizada
        minutos, hora = math.modf(hora)
        hora %= 24
        minutos *= 60
        minutos = "0" + str(int(minutos))
        return "%i:%s" % (hora, minutos[-2:])

    def _update(self, task):
        b = self.contexto.base
        # posición
        pos_obj = self.objetivo.getPos(b.render)
        self.nodo.setPos(pos_obj.getX(), pos_obj.getY(), 0)
        # dt, segundos
        t = b.taskMgr.globalClock.getFrameTime()
        self.segundos += (t - self._tiempo_anterior)
        self.segundos %= self.segundos_dia
        self._tiempo_anterior = t
        # hora normalizada
        self.hora_normalizada = self.segundos / self.segundos_dia
        # sol
        self.sol_rig.setP(360 * self.hora_normalizada)
        #
        return task.again
