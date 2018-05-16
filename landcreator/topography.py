from panda3d.core import *

from layer import Layer
from data import PerChunkIterator

import math
import sys

import logging
log=logging.getLogger(__name__)

class Topography(Layer):
    
    def __init__(self, index, data_mgr, config_topography, size_total, ocean_altitude_relative, border_start_relative):
        Layer.__init__(self, "topography", index, data_mgr)
        self.requires_layers=[]
        # parameters:
        self.height=config_topography.getfloat("height")
        self.scale=config_topography.getfloat("scale")
        self.ocean_altitude=ocean_altitude_relative*self.height
        self.border_start_relative=border_start_relative
        #
        self.perlin_seed=9601
        self.perlin_levels=[] # [(scale,amplitude), ...]
        # components:
        self.perlin=None
        # internal variables:
        self._size_half=int(self.data_mgr.size_total/2.0)*self.scale
        self._border_start=self.border_start_relative*self._size_half
    
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
        N, n=self.data_mgr.num_chunks_total, 0
        #
        iter=PerChunkIterator(self.data_mgr)
        while iter.next():
            descriptor=iter.get_descriptor()
            altitude=self._calculate_altitude(descriptor.global_position * self.scale)
            descriptor.global_position.setY(altitude)
            log.debug(str(descriptor))
            if iter.pick_changed_chunk():
                self.data_mgr.set_chunk_dirty(tuple(iter.cur_idx_pos))
                n+=1
                sys.stdout.write("\r%.2f%%"%(n*100/N))
                sys.stdout.flush()
        print("\n")
        #
        return True

    def _calculate_altitude(self, position):
        # perlin noise object
        altitude=self.perlin(position[0], position[2])*0.5+0.5
        #
        altitude*=self.height
        if altitude>self.ocean_altitude+0.25:
            height_above_ocean=altitude-self.ocean_altitude
            height_above_ocean_n=height_above_ocean/(self.height-self.ocean_altitude)
            altitude=self.ocean_altitude
            altitude+=0.25+height_above_ocean*height_above_ocean_n*height_above_ocean_n
            altitude+=75.0*height_above_ocean_n*height_above_ocean_n
            if altitude>self.height:
                log.warning("_calculate_altitude altitude>self.height, truncating...")
                altitude=self.height
        #
        dx, dy=abs(self._size_half-position[0]), abs(self._size_half-position[2])
        #max_center_distance=(dx if dx>dy else dy)
        max_center_distance=math.sqrt(dx**2+dy**2)
        if max_center_distance>(self._border_start):
            transition_factor=(max_center_distance-self._border_start)/(self._size_half-self._border_start)
            altitude=min(self.height, altitude+self.height*transition_factor)
        #
        return altitude

