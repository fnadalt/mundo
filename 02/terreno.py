# -*- coding: utf-8 -*-

import math

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

from proveedores import Topografia

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
        # parametros
        self.altura = 10.0  # height
        self.factor_estiramiento = 0.05  # stretch factor, xy

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
        self.nodo = self.geom.getRoot()
        self.nodo.reparentTo(self.contexto.base.render)
        self.nodo.setScale(
            self.factor_estiramiento,
            self.factor_estiramiento,
            self.altura)
        # tasks
        self.contexto.base.taskMgr.doMethodLater(
            0.500,
            self._update,
            "Terreno_update"
            )
        # proveedor de datos
        self.contexto.registrar_proveedor(Topografia.Nombre, self)
        #
        return True

    def terminar(self):
        log.info("terminar")
        # proveedor de datos
        self.contexto.remover_proveedor(Topografia.Nombre)
        #
        self.geom = None
        if self.nodo:
            self.nodo.removeNode()
            self.nodo = None
        # tasks
        self.contexto.base.taskMgr.remove("Terreno_update")

    """
    * proveedor de datos de topografia
    """
    def obtener_altitud(self, pos2d):
        elevacion = self.geom.getElevation(pos2d.getX(), pos2d.getY())
        elevacion *= self.altura
        return elevacion

    """
    * proveedor de datos de topografia
    """
    def obtener_normal(self, pos2d):
        pospix = self._obtener_pos_pixel(pos2d)
        normal = self.geom.getNormal(pospix.GetX(), pospix.getY())
        normal.set(
            normal.getX() / self.factor_estiramiento,
            normal.getY() / self.factor_estiramiento,
            normal.getZ() / self.altura,
            )
        return normal.normalized()

    def _obtener_pos_pixel(self, pos2d):
        intx = math.floor(pos2d.getX() / self.factor_estiramiento)
        intx += self.geom.heightmap().getReadXSize() / 2
        inty = math.floor(pos2d.getY() / self.factor_estiramiento)
        inty += self.geom.heightmap().getReadYSize() / 2
        return Vec2(intx, inty)

    def _update(self, task):
        self.geom.update()
        return task.again
