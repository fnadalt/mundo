from panda3d.core import *
import os, os.path

import logging
log=logging.getLogger(__name__)

class Parcela(GeoMipTerrain):
    
    tamano=64
    pos_offset=tamano/2.0#-0.5

    def __init__(self, height_map, indice_x, indice_y, focal_point):
        #
        self._height_map=height_map
        self.nombre="parcela_%i_%i_%i"%(height_map.id, indice_x, indice_y)
        self.indice_x=indice_x
        self.indice_y=indice_y
        self.nombre_archivo_height_map=os.path.join(os.getcwd(), "parcelas", "%s_heightmap.png"%self.nombre)
        # GeoMipTerrain
        GeoMipTerrain.__init__(self, self.nombre)
        self.setBruteforce(True)
        self.setBlockSize(32)
        self.setNear(40.0)
        self.setFar(500.0)
        self.setFocalPoint(focal_point)
        self.setHeightfield(self._generar_heightfield())
    
    def obtener_altitud(self, x, y):
        offset_x=self.tamano * self.indice_x
        offset_y=self.tamano * self.indice_y
        return self._height_map.getHeight(x+offset_x, y-offset_y)
    
    def _generar_heightfield(self):
        _hf=None
        #
        if os.path.exists(self.nombre_archivo_height_map):
            log.debug("se encontro archivo heightmap "+self.nombre_archivo_height_map)
            _hf=PNMImage()
            _hf.read(Filename(self.nombre_archivo_height_map))
        else:
            log.debug("generando archivo de heightmap "+self.nombre_archivo_height_map)
            _hf=PNMImage(self.tamano+1, self.tamano+1, 1, 65535)
            #
            for x in range(_hf.getXSize()):
                for y in range(_hf.getYSize()):
                    altitud=self.obtener_altitud(x, y)
                    _hf.setGray(x, y, altitud)
            #
            _hf.write(Filename(self.nombre_archivo_height_map))
        #
        return _hf
