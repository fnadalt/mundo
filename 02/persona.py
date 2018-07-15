# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from panda3d.core import *

from proveedores import Topografia

# log
import logging
log = logging.getLogger(__name__)


class Persona(DirectObject):

    def __init__(self, contexto, _input):
        # referencias
        self.contexto = contexto
        self.input = _input
        self.topografia = None
        # componentes
        self.actor = None

    def iniciar(self):
        log.info("iniciar")
        b = self.contexto.base
        # referencias
        self.topografia = self.contexto.obtener_proveedor(Topografia.Nombre)
        # actor
        self.actor = Actor("modelos/hombre/male.egg")
        self.actor.reparentTo(b.render)
        # tasks
        self.contexto.base.taskMgr.add(self._update, "Persona_update")
        #
        return True

    def terminar(self):
        log.info("terminar")
        # tasks
        self.contexto.base.taskMgr.remove("Persona_update")
        # referencias
        self.input = None
        self.topografia = None
        # actor
        if self.actor:
            self.actor.delete()
            self.actor = None

    def _update(self, task):
        pos2d = Vec2(self.actor.getX(), self.actor.getY())
        self.actor.setZ(self.topografia.obtener_altitud(pos2d))
        return task.cont
