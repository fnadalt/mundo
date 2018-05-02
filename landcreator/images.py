from panda3d.core import *

from data import PerChunkIterator

import os.path
import time

import logging
log=logging.getLogger(__name__)

class ImagesGenerator:
    
    def __init__(self):
        # parameters
        self.layers=None # [type,...]
        # references
        self.data_mgr=None
    
    def initialize(self, layers, data_mgr):
        log.info("initialize")
        #
        self.layers=layers
        self.data_mgr=data_mgr
    
    def terminate(self):
        log.info("terminate")
        self.data_mgr=None
    
    def execute(self):
        log.info("execute")
        #
        for type, layer in self.layers.items():
            log.info("processing layer '%s'"%type)
            #
            t1=time.time()
            result=False
            #
            if type=="topography":
                result=self._generate_heightmap(layer.height)
            else:
                log.warning("type '%s' not handled, skipping..."%type)
                continue
            #
            if not result:
                return False
            #
            t2=time.time()
            log.info("done processing layer '%s' in %.3f"%(type, (t2-t1)))
        #
        return True

    def _create_image(self):
        size=self.data_mgr.size_chunk
        return PNMImage(size, size)
    
    def _clear_image_data(self, image):
        if not image:
            return
        image.clear()
    
    def _write_image(self, image, file_name):
        #
        if not image:
            return True
        #
        log.info("_write_image '%s'"%file_name)
        #
        file_path=os.path.join(self.data_mgr.directory, file_name)
        result=image.write(file_path)
        if not result:
            log.error("PMNImage.write('%s')=%s"%(file_path, str(result)))
        return result

    def _generate_heightmap(self, height):
        log.info("_generate_heightmap")
        #
        iter=PerChunkIterator(self.data_mgr)
        #
        image=None
        file_name="heightmap_%i_%i.png"%(iter.cur_idx_pos[0], iter.cur_idx_pos[1])
        #
        while not iter.end:
            # step
            iter.next()
            # chunk changed
            if iter.pick_changed_chunk() or iter.end:
                # write current image
                if not self._write_image(image, file_name):
                    return False
                # new image
                self._clear_image_data(image)
                image=self._create_image()
                file_name="heightmap_%i_%i.png"%(iter.cur_idx_pos[0], iter.cur_idx_pos[1])
            if not iter.end: # too much!
                # process descriptor
                descriptor=iter.get_descriptor()
                log.debug(str(descriptor))
                value=descriptor.global_position[1]/height
                # set pixel color
                image.setXel(iter.cur_chunk_x, iter.cur_chunk_y, value, value, value)
        #
        return True
