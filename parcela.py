from panda3d.core import *
import os, os.path

import logging
log=logging.getLogger(__name__)

class Parcela(GeoMipTerrain):
    
    tamano=32#128
    pos_offset=tamano/2.0#-0.5

    def __init__(self, height_map, x, y, focal_point):
        #
        self._height_map=height_map
        self.nombre="parcela_%i_%i"%(x, y)
        self.posicion=Vec2(x, y)
        self.nombre_archivo_height_map="%s.png"%self.nombre
        self.imagen=PNMImage()
        #
        GeoMipTerrain.__init__(self, self.nombre)
        self.setBlockSize(32)
        self.setNear(40.0)
        self.setFar(100.0)
        self.setFocalPoint(focal_point)
        #
        self._procesar_imagen()
        self.generate()
    
    def _procesar_imagen(self):
        #
        if os.path.exists(self.nombre_archivo_height_map):
            log.debug("se encontro archivo imagen "+self.nombre_archivo_height_map)
            self.imagen.read(Filename(self.nombre_archivo_height_map))
        else:
            log.debug("generando archivo de imagen "+self.nombre_archivo_height_map)
            self.imagen=PNMImage(self.tamano+1, self.tamano+1, 1, 65535)
            #
            offset_x=self.tamano * self.posicion.getX()
            offset_y=self.tamano * self.posicion.getY()
            for x in range(self.imagen.getXSize()):
                for y in range(self.imagen.getYSize()):
                    altitud=self._height_map.getHeight(x+offset_x, y-offset_y)
                    #log.debug("hm %i %i %f"%(x, y, altitud))
                    self.imagen.setGray(x, y, altitud)
            #
            self.imagen.write(Filename(self.nombre_archivo_height_map))
        #
        self.setHeightfield(self.imagen)
