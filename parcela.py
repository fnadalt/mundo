from panda3d.core import *
import voxels
import os, os.path

import logging
log=logging.getLogger(__name__)

class Parcela:
    
    tamano=64
    pos_offset=tamano/2.0#-0.5

    def __init__(self, height_map, indice_x, indice_y):
        #
        self._height_map=height_map
        self.nombre="parcela_%i_%i_%i"%(height_map.id, indice_x, indice_y)
        self.indice_x=indice_x
        self.indice_y=indice_y
        self.optimizar=False
    
    def obtener_altitud(self, x, y):
        offset_x=self.tamano * self.indice_x
        offset_y=self.tamano * self.indice_y
        return self._height_map.getHeight(x+offset_x, y-offset_y)
    
    def establecer_optimizacion(self, flag):
        self.optimizar=flag
    
    def generar(self):
        pass
        
    def actualizar(self):
        pass
    
class ParcelaGeoMip(Parcela):

    def __init__(self, height_map, indice_x, indice_y, focal_point):
        Parcela.__init__(self, height_map, indice_x, indice_y)
        #
        self.nombre_archivo_height_map=os.path.join(os.getcwd(), "parcelas", "%s_heightmap.png"%self.nombre)
        # GeoMipTerrain
        self._geomip=GeoMipTerrain(self.nombre)
        self._geomip.setBruteforce(True)
        self._geomip.setBlockSize(32)
        self._geomip.setNear(40.0)
        self._geomip.setFar(500.0)
        self._geomip.setFocalPoint(focal_point)
        self._geomip.setHeightfield(self._generar_heightfield())
    
    def _generar_heightfield(self):
        _hf=None
        #
        if os.path.exists(self.nombre_archivo_height_map):
            #log.debug("se encontro archivo heightmap "+self.nombre_archivo_height_map)
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
    
    def establecer_optimizacion(self, flag):
        Parcela.establecer_optimizacion(self, flag)
        self._geomip.setBruteforce(not flag)
        
    def generar(self):
        self._geomip.generate()
        return self._geomip.getRoot()

    def actualizar(self):
        self._geomip.update()

class ParcelaVoxel(Parcela):
    
    def __init__(self, height_map, indice_x, indice_y, focal_point):
        Parcela.__init__(self, height_map, indice_x, indice_y)
        # voxels
        self.volumen=voxels.Objeto(self.nombre, int(self.tamano), int(self.tamano), int(self.tamano/2), 0)
    
    def _definir_volumen(self):
        dim_z=self.volumen.obtener_dimension_z()
        for x in range(self.volumen.obtener_dimension_x()):
            for y in range(self.volumen.obtener_dimension_y()):
                altitud=self.obtener_altitud(x, y)
                altitud*=self.tamano/dim_z
                for h in range(altitud): # altitud+1?
                    self.volumen.establecer_valor(x, y, h, 255)
    
    def generar(self):
        geom=self.volumen.construir_cubos()
        return NodePath(geom)
    
    def actualizar(self):
        pass
