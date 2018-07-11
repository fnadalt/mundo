# -*- coding: utf-8 -*-

from panda3d.core import *


class Topografia:
    """
    * proveedor básico de datos de topografía.
    * esta interfaz debería ser implementada por Terreno, por ejemplo.
    """

    Nombre = "topografia"

    Normal = Vec3(0, 0, 1)

    def __init__(self):
        pass

    def obtener_altitud(self, pos2d):  # get altitude
        return 0.0

    def obtener_normal(self, pos2d):  # get normal
        return Topografia.Normal
