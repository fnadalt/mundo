# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class Terreno(DirectObject):

    def __init__(self, contexto):
        # referencias
        self.contexto = contexto
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
        self.geom.generate()
        # nodo
        self.nodo = self.geom.getRoot()
        self.nodo.setSz(10)
        self.nodo.reparentTo(self.contexto.base.render)
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
