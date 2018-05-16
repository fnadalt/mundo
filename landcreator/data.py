from panda3d.core import *

import os, os.path
import pickle

import logging
log=logging.getLogger(__name__)

#
# DataManager
#
class DataManager:
    
    def __init__(self):
        # external variables
        self.directory="."
        self.size_total=1
        self.size_chunk=1
        self.num_chunks_side=1
        self.num_chunks_total=1
        self.chunk_prefix="chunk"
        # internal variables
        self._cache_min_size=64 # minimum number of chunks at work
        self._cache_max_size=96 # maximum number of chunks at work
        # components
        self._cache=None # {idx_pos:Chunk,...}
        
    def initialize(self, directory, config, size_total, size_chunk):
        log.info("initialize")
        # directory
        self.directory=directory
        # config
        try:
            self.chunk_prefix=config["chunk_prefix"]
        except Exception as e:
            log.exception(str(e))
            return False
        # sizes
        self.size_total=size_total
        self.size_chunk=size_chunk
        if not self._ispow2(self.size_total):
            log.error("size_total must be power of 2")
            return False
        if not self._ispow2(self.size_chunk) or self.size_chunk>self.size_total:
            log.error("size_chunk must be power of 2 and less than size_total")
            return False
        self.num_chunks_side=self.size_total/self.size_chunk
        self.num_chunks_total=self.num_chunks_side**2
        log.info("size_total=%i size_chunk=%i num_chunks_side=%i num_chunks_total=%i"% \
                (self.size_total, self.size_chunk, self.num_chunks_side, self.num_chunks_total))
        # cache
        self._cache=dict()
        #
        return True
    
    def terminate(self):
        log.info("terminate")
        #
        if self._cache:
            for idx_pos, chunk in self._cache.items():
                log.info("terminate chunk %s"%(str(chunk.idx_pos)))
                if chunk.dirty==True:
                    log.info("rewriting dirty cache idx_pos %s"%(str(chunk.idx_pos)))
                    self._write_chunk(chunk)
                #
                chunk.terminate()
            self._cache=None

    def get_descriptor(self, global_position):
        # idx_pos
        idx_pos_x=int(global_position[0]/self.size_chunk) # don't check validity here, for performance?
        idx_pos_y=int(global_position[2]/self.size_chunk)
        idx_pos=(idx_pos_x, idx_pos_y)
        # chunk
        chunk=self._get_chunk(idx_pos)
        if not chunk:
            log.error("chunk data could not be loaded! idx_pos=%s"%str(idx_pos))
            return None
        # descriptor
        return chunk.get_descriptor(global_position)

    def set_chunk_dirty(self, idx_pos):
#        log.info("set_chunk_dirty idx_pos=%s"%str(idx_pos))
        chunk=self._get_chunk(idx_pos)
        if not chunk:
            log.error("chunk data could not be loaded! idx_pos=%s"%str(idx_pos))
            return False
        #
        chunk.dirty=True
        #
        return True

    def _ispow2(self, n):
        return (n & (n - 1)) == 0
    
    def _get_chunk(self, idx_pos):
        chunk=None
        #
        if not idx_pos in self._cache:
            # adjust cache?
            if len(self._cache)>self._cache_max_size:
                self._adjust_cache()
            # load chunk
            if not self._load_chunk(idx_pos):
                return None
        #
        chunk=self._cache[idx_pos]
        #
        return chunk
    
    def _load_chunk(self, idx_pos):
        #log.info("_load_chunk %s"%str(idx_pos))
        chunk=None
        #
        file_name=self.chunk_prefix+"_%i_%i.dat"%(int(idx_pos[0]), int(idx_pos[1]))
        file_path=os.path.join(self.directory, file_name)
        #
        if os.path.exists(file_path):
            log.debug("_load_chunk <<-- '%s'"%file_name)
            with open(file_path, "rb") as file:
                chunk=pickle.load(file)
                self._cache[idx_pos]=chunk
        else:
            chunk=Chunk()
            if not chunk.initialize(idx_pos, self.size_chunk):
                return False
            self._cache[idx_pos]=chunk
            log.debug("_load_chunk -->> '%s'"%file_name)
            self._write_chunk(chunk)
        #
        return True
    
    def _write_chunk(self, chunk):
        #log.info("_write_chunk idx_pos %s"%(str(chunk.idx_pos)))
        #
        file_name=self.chunk_prefix+"_%i_%i.dat"%(int(chunk.idx_pos[0]), int(chunk.idx_pos[1]))
        file_path=os.path.join(self.directory, file_name)
        #
        if os.path.exists(file_path):
            os.remove(file_path)
        # clear dirty
        chunk.dirty=False
        #
        with open(file_path, "wb") as file:
            pickle.dump(chunk, file)
    
    def _adjust_cache(self):
        log.info("_adjust_cache")
        # chunks sorted by access_cntr
        chunks=sorted(self._cache.values(), key=lambda x:x.access_cntr)
        # number of chunks to unload
        num_unload=len(self._cache)-self._cache_min_size
        # gather idx_pos of chunk to be unloaded
        idx_pos_unload=list()
        for i in range(num_unload):
            idx_pos_unload.append(chunks[i].idx_pos)
        # unload
        for idx_pos in idx_pos_unload:
            chunk=self._cache[idx_pos]
            #
            if chunk.dirty:
                log.info("_adjust_cache rewriting dirty cache idx_pos %s"%(str(chunk.idx_pos)))
                self._write_chunk(chunk)
            #
            chunk.terminate()
            self._cache[idx_pos]=None
            del self._cache[idx_pos]

#
# LocationDescriptor
#
class LocationDescriptor:
    
    def __init__(self, global_position=Vec3.zero()):
        # topography
        self.global_position=global_position
        self.normal=Vec3(0, 1, 0)
        # river
        self.river=0.0
        # climate
        self.temperature=0.0
        self.humidity=0.0
        # vegetation
        self.vegetation=None
    
    def __str__(self):
        return "LocationDescriptor@%s n=%s river=%.2f temp=%.2f hum=%.2f"% \
                (str(self.global_position), str(self.normal), self.river, self.temperature, self.humidity)

#
# Chunk
#
class Chunk:
    
    AccessCounter=0
    
    @staticmethod
    def increase_access_counter():
        Chunk.AccessCounter+=1
        return Chunk.AccessCounter
    
    def __init__(self):
        # external variables
        self.access_cntr=0
        self.idx_pos=Vec2.zero()
        self.size=1
        self.chunk_position=Vec2.zero()
        self.dirty=False
        # components
        self._descriptors=None
    
    def initialize(self, idx_pos, size):
        #
        self.access_cntr=Chunk.increase_access_counter()
        #
        self.idx_pos=idx_pos
        self.size=size
        self.chunk_position=Vec3(idx_pos[0], 0, idx_pos[1])*size
        #
        self._descriptors=list()
        for x in range(size):
            row=list()
            for y in range(size):
                global_position=Vec3(self.chunk_position[0]+x, 0.0, self.chunk_position[2]+y)
                descriptor=LocationDescriptor(global_position)
                row.append(descriptor)
            self._descriptors.append(row)
        #
        return True
    
    def terminate(self):
        #
        if self._descriptors:
            for row in self._descriptors:
                for i in range(len(row)):
                    row[i]=None
            self._descriptors=None

    def get_descriptor(self, global_position):
        self.access_cntr=Chunk.increase_access_counter()
        local_position=global_position-self.chunk_position
        return self._descriptors[int(local_position[0])][int(local_position[2])]

#
# PerChunkIterator
#
class PerChunkIterator:
    
    def __init__(self, data_mgr):
        # references
        self.data_mgr=data_mgr
        # external variables
        self.cur_idx_pos=[0, 0]
        self.cur_chunk_x=-1
        self.cur_chunk_y=0
        self.cur_pos_x=-1
        self.cur_pos_y=0
        self.end=False
        # internal variables
        self._changed_chunk=True

    def next(self):
        # step x
        self.cur_chunk_x+=1
        self.cur_pos_x+=1
        # step y
        if self.cur_chunk_x==self.data_mgr.size_chunk:
            self.cur_chunk_x=0
            self.cur_chunk_y+=1
            self.cur_pos_y+=1
            if self.cur_chunk_y==self.data_mgr.size_chunk:
                self.cur_chunk_y=0
                self.cur_idx_pos[0]+=1
                self._changed_chunk=True
                if self.cur_pos_x==self.data_mgr.size_total:
                    if self.cur_pos_y==self.data_mgr.size_total:
                        self.end=True
                        return False
                    self.cur_idx_pos[0]=0
                    self.cur_idx_pos[1]+=1
                    self._changed_chunk=True
                    self.cur_pos_x=0
                self.cur_pos_y=self.cur_idx_pos[1]*self.data_mgr.size_chunk
            self.cur_pos_x=self.cur_idx_pos[0]*self.data_mgr.size_chunk
        return True
    
    def get_descriptor(self):
        position=Vec3(self.cur_pos_x, 0.0, self.cur_pos_y)
        return self.data_mgr.get_descriptor(position)

    def pick_changed_chunk(self):
        changed=self._changed_chunk
        self._changed_chunk=False
        return changed

