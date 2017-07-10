from panda3d.core import *
import os, os.path

import logging
log=logging.getLogger(__name__)

class Parcela(GeoMipTerrain):
    
    tamano=32
    pos_offset=tamano/2.0#-0.5

    def __init__(self, height_map, indice_x, indice_y, focal_point):
        #
        self._height_map=height_map
        self.nombre="parcela_%i_%i_%i"%(height_map.id, indice_x, indice_y)
        self.indice_x=indice_x
        self.indice_y=indice_y
        self.nombre_archivo_height_map=os.path.join(os.getcwd(), "parcelas", "%s_heightmap.png"%self.nombre)
        self.imagen=PNMImage()
        #
        GeoMipTerrain.__init__(self, self.nombre)
        self.setBlockSize(32)
        self.setNear(40.0)
        self.setFar(100.0)
        self.setFocalPoint(focal_point)
        #
        self._procesar_imagen()
    
    def _procesar_imagen(self):
        #
        if os.path.exists(self.nombre_archivo_height_map):
            log.debug("se encontro archivo imagen "+self.nombre_archivo_height_map)
            self.imagen.read(Filename(self.nombre_archivo_height_map))
        else:
            log.debug("generando archivo de imagen "+self.nombre_archivo_height_map)
            self.imagen=PNMImage(self.tamano+1, self.tamano+1, 1, 65535)
            #
            offset_x=self.tamano * self.indice_x
            offset_y=self.tamano * self.indice_y
            for x in range(self.imagen.getXSize()):
                for y in range(self.imagen.getYSize()):
                    altitud=self._height_map.getHeight(x+offset_x, y-offset_y)
                    #log.debug("hm %i %i %f"%(x, y, altitud))
                    self.imagen.setGray(x, y, altitud)
            #
            self.imagen.write(Filename(self.nombre_archivo_height_map))
        #
        self.setHeightfield(self.imagen)
