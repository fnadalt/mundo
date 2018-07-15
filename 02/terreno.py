# -*- coding: utf-8 -*-

import math
import os.path

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from panda3d.bullet import *

from proveedores import Topografia

# log
import logging
log = logging.getLogger(__name__)


class Terreno(DirectObject):
    """
    * administra GeomMipTerrain
    * administra Bullet shape
    * proveedor de interfaz de Topografia
    """

    def __init__(self, contexto, mundo_fisica):
        # referencias
        self.contexto = contexto
        self.mundo_fisica = mundo_fisica
        # componentes
        self.nodo = None  # node
        self.geom = None
        self.cuerpo = None  # physic body
        # parametros
        self.heightmap = "heightmap.png"
        self.altura = 10.0  # height
        self.factor_estiramiento = 1  # stretch factor, xy
        self.wireframe = False
        self.brute_force = False
        self.fisica = True  # enable physics
        # variables externas  # external variables
        self.longitud_lado = 0  # heightmap image side length

    def iniciar(self):
        log.info("iniciar")
        self._establecer_parametros()
        # heightfield
        image_file_path = os.path.join(
            "terreno/texturas/",
            self.heightmap)
        heightfield = PNMImage(image_file_path)
        # geom
        self.geom = GeoMipTerrain("terreno")
        self.geom.setHeightfield(heightfield)
        self.geom.setBlockSize(32)
        self.geom.setNear(40)
        self.geom.setFar(100)
        self.geom.setFocalPoint(base.camera)
        self.geom.setBruteforce(self.brute_force)
        self.geom.generate()
        # longitud lado
        if heightfield.getReadXSize() != heightfield.getReadYSize():
            log.error("heightfield debe ser cuadrado")
            return False
        self.longitud_lado = self.geom.heightfield().getReadXSize()
        # nodo
        self.nodo = self.geom.getRoot()
        self.nodo.reparentTo(self.contexto.base.render)
        self.nodo.setPos(
            -self.longitud_lado / 2 * self.factor_estiramiento,
            -self.longitud_lado / 2 * self.factor_estiramiento,
            0)
        self.nodo.setScale(
            self.factor_estiramiento,
            self.factor_estiramiento,
            self.altura)
        if self.wireframe:
            self.nodo.setRenderModeWireframe()
        # física
        if self.fisica:
            shp = BulletHeightfieldShape(
                self.geom.heightfield(),
                self.altura,
                ZUp)
            rbody = BulletRigidBodyNode("cuerpo_terreno")
            rbody.addShape(shp)
            self.mundo_fisica.attachRigidBody(rbody)
            self.cuerpo = self.contexto.base.render.attachNewNode(rbody)
            self.cuerpo.setPos(
                0,
                0,
                self.altura / 2)
            self.cuerpo.setSx(self.factor_estiramiento)
            self.cuerpo.setSy(self.factor_estiramiento)
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
        # tasks
        self.contexto.base.taskMgr.remove("Terreno_update")
        # proveedor de datos
        self.contexto.remover_proveedor(Topografia.Nombre)
        # física
        if self.cuerpo:
            self.mundo_fisica.attachRigidBody(self.cuerpo.node())
            self.cuerpo.removeNode()
            self.cuerpo = None
        # nodo y geom
        self.geom = None
        if self.nodo:
            self.nodo.removeNode()
            self.nodo = None

    def _establecer_parametros(self):
        log.info("_establecer_parametros")
        try:
            cfg = self.contexto.config["terreno"]
            self.heightmap = cfg.get("heightmap")
            self.altura = cfg.getfloat("altura")
            self.factor_estiramiento = cfg.getfloat("factor_estiramiento")
            self.wireframe = cfg.getboolean("wireframe")
            self.brute_force = cfg.getboolean("brute_force")
            self.fisica = cfg.getboolean("fisica")
        except ValueError as e:
            log.exception("error en el análisis de la configuración: " + str(e))

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
        intx += self.longitud_lado / 2
        inty = math.floor(pos2d.getY() / self.factor_estiramiento)
        inty += self.longitud_lado / 2
        return Vec2(intx, inty)

    def _update(self, task):
        self.geom.update()
        return task.again
