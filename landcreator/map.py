from panda3d.core import *

import sys
import os.path
import time

import logging
log=logging.getLogger(__name__)

class MapGenerator:
    
    def __init__(self):
        # references
        self.data_mgr=None
        # parameters
        self.map="topography"
        self.map_size=512
        self.topography_height=255.0
        self.ocean_altitude=0.0
    
    def initialize(self, data_mgr, config_topography, map, map_size, ocean_altitude_relative):
        log.info("initialize")
        #
        self.data_mgr=data_mgr
        self.map=map
        self.map_size=map_size
        self.topography_height=config_topography.getfloat("height")
        self.ocean_altitude=self.topography_height*ocean_altitude_relative
    
    def terminate(self):
        log.info("terminate")
        self.data_mgr=None
    
    def execute(self):
        log.info("execute")
        #
        t1=time.time()
        result=False
        #
        if self.map=="topography":
            result=self._generate_map_topography()
        #
        if not result:
            return False
        #
        t2=time.time()
        log.info("done generating map '%s' in %.3f"%(self.map, (t2-t1)))
        #
        return True
    
    def _generate_map_topography(self):
        log.info("_generate_map_topography")
        #
        sizes_ratio=self.data_mgr.size_total/self.map_size
        n, N=0, self.map_size**2
        #
        file_name="%s.png"%(self.map)
        image=PNMImage(self.map_size, self.map_size, 1)
        #
        for x in range(self.map_size):
            for y in range(self.map_size):
                pos_x, pos_y=x*sizes_ratio, y*sizes_ratio
                descriptor=self.data_mgr.get_descriptor(Vec3(pos_x, 0.0, pos_y))
                log.debug(str(descriptor))
                height=descriptor.global_position[1]
                value=height/self.topography_height if height>self.ocean_altitude else 0.0
                # set pixel color
                image.setGray(x, y, value)
            # progress
            n+=self.map_size
            sys.stdout.write("\r%.3f%%"%(n*100/N))
            sys.stdout.flush()
        print("\n")
        #
        log.info("write file '%s'"%file_name)
        return image.write(os.path.join(self.data_mgr.directory, file_name))
