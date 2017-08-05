from panda3d.core import *
import os, os.path

import logging
log=logging.getLogger(__name__)

class Parcela(GeoMipTerrain):
    
    tamano=64
    pos_offset=tamano/2.0#-0.5
    #
    RUTA_ARCH_TEX_ARENA="texturas/arena.png"
    RUTA_ARCH_TEX_TIERRA="texturas/tierra.png"
    RUTA_ARCH_TEX_PASTO="texturas/pasto.png"
    RUTA_ARCH_TEX_NIEVE="texturas/nieve.png"

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
        #
        #self._generar_imagen_textura()
    
    def _obtener_altitud(self, x, y):
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
                    altitud=self._obtener_altitud(x, y)
                    _hf.setGray(x, y, altitud)
            #
            _hf.write(Filename(self.nombre_archivo_height_map))
        #
        return _hf

    def _generar_imagen_textura(self):
        _ruta_archivo="parcelas/%s_textura.png"%self.nombre
        if os.path.exists(_ruta_archivo):
            log.debug("se encontro archivo de textura "+_ruta_archivo)
            return
        log.debug("generando archivo de textura "+_ruta_archivo)
        # texturas fuente
        _img_tex_arena=PNMImage()
        _img_tex_tierra=PNMImage()
        _img_tex_pasto=PNMImage()
        _img_tex_nieve=PNMImage()
        _img_tex_arena.read(Parcela.RUTA_ARCH_TEX_ARENA)
        _img_tex_tierra.read(Parcela.RUTA_ARCH_TEX_TIERRA)
        _img_tex_pasto.read(Parcela.RUTA_ARCH_TEX_PASTO)
        _img_tex_nieve.read(Parcela.RUTA_ARCH_TEX_NIEVE)
        #log.debug("textura arena %sx%s"%(str(_img_tex_arena.getXSize()), str(_img_tex_arena.getYSize())))
        #log.debug("textura tierra %sx%s"%(str(_img_tex_tierra.getXSize()), str(_img_tex_tierra.getYSize())))
        #log.debug("textura pasto %sx%s"%(str(_img_tex_pasto.getXSize()), str(_img_tex_pasto.getYSize())))
        #log.debug("textura nieve %sx%s"%(str(_img_tex_nieve.getXSize()), str(_img_tex_nieve.getYSize())))
        # parametros
        _img_tex_arena_iPos=[0, 0]
        _img_tex_tierra_iPos=[0, 0]
        _img_tex_pasto_iPos=[0, 0]
        _img_tex_nieve_iPos=[0, 0]
        _corte_arena=0.42
        _corte_tierra=0.46
        _corte_pasto=0.60
        #
        _img_tex_tamano=256
        _img_tex=PNMImage(_img_tex_tamano, _img_tex_tamano)
        for x in range(_img_tex_tamano):
            for y in range(_img_tex_tamano):
                _hf_x=(x+self.tamano * self.indice_x)*Parcela.tamano/_img_tex_tamano
                _hf_y=(y-self.tamano * self.indice_y)*Parcela.tamano/_img_tex_tamano
                _altitud=self._obtener_altitud(_hf_x+0.5, _hf_y+0.5)
                pixel=None
                if _altitud<_corte_arena:
                    pixel=_img_tex_arena.getPixel(_img_tex_arena_iPos[0], _img_tex_arena_iPos[1])
                    #log.debug("pixel arena @%s->%s"%(str(_img_tex_arena_iPos), str(pixel)))
                    _img_tex_arena_iPos[0]+=1
                    if _img_tex_arena_iPos[0]>=_img_tex_arena.getXSize():
                        _img_tex_arena_iPos[0]=0
                elif _altitud>=_corte_arena and _altitud<_corte_tierra:
                    pixel=_img_tex_tierra.getPixel(_img_tex_tierra_iPos[0], _img_tex_tierra_iPos[1])
                    #log.debug("pixel tierra @%s->%s"%(str(_img_tex_tierra_iPos), str(pixel)))
                    _img_tex_tierra_iPos[0]+=1
                    if _img_tex_tierra_iPos[0]>=_img_tex_tierra.getXSize():
                        _img_tex_tierra_iPos[0]=0
                elif _altitud>=_corte_tierra and _altitud<_corte_pasto:
                    pixel=_img_tex_pasto.getPixel(_img_tex_pasto_iPos[0], _img_tex_pasto_iPos[1])
                    #log.debug("pixel pasto @%s->%s"%(str(_img_tex_pasto_iPos), str(pixel)))
                    _img_tex_pasto_iPos[0]+=1
                    if _img_tex_pasto_iPos[0]>=_img_tex_pasto.getXSize():
                        _img_tex_pasto_iPos[0]=0
                else: # nieve
                    pixel=_img_tex_nieve.getPixel(_img_tex_nieve_iPos[0], _img_tex_nieve_iPos[1])
                    #log.debug("pixel nieve @%s->%s"%(str(_img_tex_nieve_iPos), str(pixel)))
                    _img_tex_nieve_iPos[0]+=1
                    if _img_tex_nieve_iPos[0]>=_img_tex_nieve.getXSize():
                        _img_tex_nieve_iPos[0]=0
                #log.debug("establecer pixel tex @%s->%s"%(str((_hf_x, _hf_y)), str(pixel)))
                _img_tex.setPixel(x, y, pixel)
            _img_tex_arena_iPos[0]=0
            _img_tex_arena_iPos[1]+=1
            if _img_tex_arena_iPos[1]>=_img_tex_arena.getYSize():
                _img_tex_arena_iPos[1]=0
            _img_tex_tierra_iPos[0]=0
            _img_tex_tierra_iPos[1]+=1
            if _img_tex_tierra_iPos[1]>=_img_tex_tierra.getYSize():
                _img_tex_tierra_iPos[1]=0
            _img_tex_pasto_iPos[0]=0
            _img_tex_pasto_iPos[1]+=1
            if _img_tex_pasto_iPos[1]>=_img_tex_pasto.getYSize():
                _img_tex_pasto_iPos[1]=0
            _img_tex_nieve_iPos[0]=0
            _img_tex_nieve_iPos[1]+=1
            if _img_tex_nieve_iPos[1]>=_img_tex_nieve.getYSize():
                _img_tex_nieve_iPos[1]=0
        #
        _img_tex.write(Filename(_ruta_archivo))
        return _img_tex
