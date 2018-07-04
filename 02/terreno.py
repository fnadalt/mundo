# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from panda3d.bullet import *

# log
import logging
log = logging.getLogger(__name__)


class Terreno(DirectObject):

    def __init__(self, contexto, mundo_fisica):
        # referencias
        self.contexto = contexto
        self.mundo_fisica = mundo_fisica
        # componentes
        self.nodo = None  # node
        self.geom = None

    def iniciar(self):
        log.info("iniciar")
        # geom
        self.geom = GeoMipTerrain("terreno")
        self.geom.setHeightfield("terreno/texturas/heightmap.png")
        self.geom.setBlockSize(32)
        self.geom.setNear(40)
        self.geom.setFar(100)
        self.geom.setFocalPoint(base.camera)
        self.geom.setBruteforce(False)
        self.geom.generate()
        # nodo
        shape = BulletHeightfieldShape(self.geom.heightfield(), 10.0, ZUp)
        rbody = BulletRigidBodyNode("Terreno_rbody")
        rbody.addShape(shape)
        self.mundo_fisica.attachRigidBody(rbody)
        self.nodo = self.contexto.base.render.attachNewNode(rbody)
        self.geom.getRoot().reparentTo(self.nodo)
        # tasks
        self.contexto.base.taskMgr.doMethodLater(
            0.500,
            self._update,
            "Terreno_update"
            )
        #
        return True

    def terminar(self):
        log.info("terminar")
        #
        self.geom = None
        if self.nodo:
            self.nodo.removeNode()
            self.nodo = None
        # tasks
        self.contexto.base.taskMgr.remove("Terreno_update")

    def _update(self, task):
        self.geom.update()
        return task.again
