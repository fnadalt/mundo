from panda3d.core import *

from layer import Layer
from data import PerChunkIterator

import math

import logging
log=logging.getLogger(__name__)

class Topography(Layer):
    
    def __init__(self, index, data_mgr, size_total, ocean_altitude):
        Layer.__init__(self, "topography", index, data_mgr, size_total)
        self.requires_layers=[]
        # parameters:
        self.height=500.0 # float
        self.ocean_altitude=ocean_altitude # [0,1]
        self.ocean_height=0.0
        #
        self.perlin_seed=1234
        self.perlin_levels=[] # [(scale,amplitude), ...]
        # components:
        self.perlin=None
    
    def _read_config_options(self, config):
        log.info("_read_config_options")
        try:
            self.height=float(config["height"])
        except Exception as e:
            log.exception(str(e))
            return False
        return True

    def _setup_layer(self):
        log.info("_setup_layer")
        # parameters
        self.ocean_height=math.ceil(self.height*self.ocean_altitude)
        # perlin noise
        self.perlin_levels=[(256.0, 1.0), (64.0, 0.2), (32.0, 0.075), (16.0, 0.005), (8.0, 0.001)]
        self.perlin=StackedPerlinNoise2()
        sum_amplitudes=0.0
        for scale, amplitude in self.perlin_levels:
            sum_amplitudes+=amplitude
        for scale, amplitude in self.perlin_levels:
            noise=PerlinNoise2(scale, scale, 256, self.perlin_seed)
            self.perlin.addLevel(noise, amplitude/sum_amplitudes)
        #
        return True

    def _process_data(self):
        log.info("_process_data")
        #
        iter=PerChunkIterator(self.data_mgr)
        while iter.next():
            descriptor=iter.get_descriptor()
            altitude=self._calculate_altitude(descriptor.global_position)
            descriptor.global_position.setY(altitude)
            log.debug(str(descriptor))
        #
        return True

    def _calculate_altitude(self, position):
        # perlin noise object
        altitude=self.perlin(position[0], position[2])*0.5+0.5
        #
        altitude*=self.height
#        if altitud>Sistema.TopoAltitudOceano+0.25:
#            altura_sobre_agua=altitud-Sistema.TopoAltitudOceano
#            altura_sobre_agua_n=altura_sobre_agua/(Sistema.TopoAlturaSobreOceano)
#            altitud=Sistema.TopoAltitudOceano
#            altitud+=0.25+altura_sobre_agua*altura_sobre_agua_n*altura_sobre_agua_n
#            altitud+=75.0*altura_sobre_agua_n*altura_sobre_agua_n
#            if altitud>Sistema.TopoAltura:
#                log.warning("obtener_altitud_suelo altitud>Sistema.TopoAltura, recortando...")
#                altitud=Sistema.TopoAltura
#        #
#        latitud=self.obtener_latitud(posicion)
#        if latitud>Sistema.TopoExtension:
#            factor_transicion=(latitud-Sistema.TopoExtension)/(Sistema.TopoExtensionTransicion-Sistema.TopoExtension)
#            altitud=min(Sistema.TopoAltura, altitud+Sistema.TopoAltura*factor_transicion)
        #
        return altitude

