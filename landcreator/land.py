import configparser
import os, os.path
import time

import logging
log=logging.getLogger(__name__)

from data import DataManager
from topography import Topography
from images import ImagesGenerator

# default config dict
_defaul_config={"global": {
                            "name":"land", 
                            "seed":1234, 
                            "size_total":512, 
                            "size_chunk":512, 
                            "border":"ice", # [ice|ocean]
                            "ocean_altitude":0.15 # [0,1]
                            }, 
                "layers": {
                            "topography":True, 
                            "rivers":True, 
                            "temperature":True, 
                            "humidity":True, 
                            "biomes":True, 
                            "vegetation":True
                            }, 
                "data":   {
                            "chunk_prefix":"chunk"
                            }, 
                "topography":  {
                                "height":300.0
                                }
                }

#
# Land
#
class Land:
    
    # layers
    Layers=[
            "topography", 
            "rivers", 
            "temperature", 
            "humidity", 
            "biomes", 
            "vegetation"
            ]
    
    def __init__(self):
        self.config=None
        self.generate_images=False
        self.directory="."
        self.name="land"
        self.size_total=1
        self.size_chunk=1
        self.ocean_altitude=0.15
        self.data_mgr=None # DataManager
        self.layers=None # dict()
        self.reset() # redundancy?
    
    def create(self, land_file, remove_files, create_default, generate_images):
        log.info("create, file=%s"%land_file)
        #
        self.generate_images=generate_images
        # config
        self.config=self._configure(land_file, create_default)
        if not self.config:
            return False
        # set up directory
        self.directory=self._setup_directory(remove_files)
        if not self.directory:
            return False
        # set up data
        self.data_mgr=self._setup_data_mgr(self.config, self.size_total, self.size_chunk)
        if not self.data_mgr:
            self.reset()
            return False
        # set up layers
        self.layers=self._setup_layers(self.config, self.data_mgr, self.size_total)
        if not self.layers:
            return False
        # validate layers
        if not self._validate_layers(self.layers):
            self.reset()
            return False
        # process layers
        if not self._process_layers(self.layers, self.config):
            self.reset()
            return False
        # generate images
        if generate_images and not self._generate_images(self.layers, self.data_mgr):
            self.reset()
            return False
        #
        return True
        
    def reset(self):
        log.info("reset")
        self.config=None
        self.directory="."
        #
        if self.layers:
            for type, layer in self.layers.items():
                layer.clear()
                self.layers[type]=None
            self.layers=None
        #
        if self.data_mgr:
            self.data_mgr.terminate()
    
    def _configure(self, file, create_default):
        log.info("_configure")
        # configparser
        config=configparser.ConfigParser()
        config.read_dict(_defaul_config)
        # file?
        if not os.path.exists(file):
            if not create_default:
                log.error("file '%s' does not exist"%file)
                return None
            else:
                log.info("create file '%s' with default parameters"%file)
                if os.path.exists(file):
                    log.error("file '%s' already exists")
                    return None
                with open(file, "w") as fp:
                    config.write(fp)
                return None
        # read file
        try:
            config.read(file)
        except Exception as e:
            log.exception("exception at reading file:\n%s"%str(e))
            return None
        #
        log.info("read global configuration")
        try:
            self.name=config["global"]["name"]
            self.size_total=int(config["global"]["size_total"])
            self.size_chunk=int(config["global"]["size_chunk"])
            self.ocean_altitude=float(config["global"]["ocean_altitude"])
        except Exception as e:
            log.exception(str(e))
            return None
        #
        return config

    def _setup_directory(self, remove_files):
        log.info("_setup_directory")
        #
        directory=self.name
        #
        if os.path.exists(directory) and not remove_files:
            log.error("directory '%s' exists and remove_files=False"%directory)
            return None
        elif os.path.exists(directory) and remove_files:
            if not os.path.isdir(directory):
                log.error("'%s' is not a directory"%directory)
                return None
            #
            log.info("removing files inside directory '%s'"%directory)
            for file in os.listdir(directory):
                path=os.path.join(directory, file)
                log.info("remove '%s'"%path)
                if os.path.isdir(file):
                    log.warning("'%s' is a directory... skipping."%path)
                    continue
                os.remove(path)
        elif not os.path.exists(directory):
            log.info("create directory '%s'"%directory)
            os.mkdir(directory)
        #
        return directory
    
    def _setup_data_mgr(self, config, size_total, size_chunk):
        log.info("_setup_data_mgr")
        #
        if not "data" in config:
            log.error("no 'data' section in config")
            return None
        config_data=config["data"]
        #
        data_mgr=DataManager()
        if not data_mgr.initialize(self.directory, config_data, size_total, size_chunk):
            return None
        return data_mgr
    
    def _setup_layers(self, config, data_mgr, size_total):
        log.info("_setup_layers")
        #
        if not "layers" in config:
            log.error("no 'layers' section in config")
            return None
        config_layers=config["layers"]
        #
        layers=dict()
        index=0
        for layer in Land.Layers:
            log.info("create layer '%s':"%layer)
            create_layer=False
            try:
                create_layer=True if config_layers[layer]=="True" else False
            except Exception as e:
                log.exception(str(e))
                return None
            if not create_layer:
                log.info("skipping...")
                continue
            #
            if layer=="topography":
                layers["topography"]=Topography(index, data_mgr, size_total, self.ocean_altitude)
                log.info("created.")
            else:
                log.warning("unknown layer '%s'"%layer)
                index-=1 # compensate index+=1
            #
            index+=1
        #
        return layers
    
    def _validate_layers(self, layers):
        log.info("_validate_layers")
        #
        log.info("layers requirements...")
        for type, layer in layers.items():
            for requirement in layer.requires_layers:
                if requirement in layers:
                    required_layer=layers[type]
                    if required_layer.index>=layer.index:
                        log.error("required layer '%s' for layer '%s' needs to be created before")
                        return False
                else:
                    log.error("requirement '%s' missing for layer '%s' (%s)"%(requirement, layer.type, str(layer.requires_layers)))
                    return False
        log.info("ok.")
        #
        return True

    def _process_layers(self, layers, config):
        log.info("_process_layers")
        #
        for type, layer in layers.items():
            log.info("process layer '%s'"%type)
            #
            config_type=dict()
            if type in config:
                config_type=config[type]
            else:
                log.warning("no configuration information for layer '%s'"%type)
            t1=time.time()
            if not layer.process(config_type):
                return False
            t2=time.time()
            log.info("done processing layer '%s' in time %.3f"%(type, (t2-t1)))
        #
        return True

    def _generate_images(self, layers, data_mgr):
        log.info("_generate_images")
        #
        images_generator=ImagesGenerator()
        images_generator.initialize(layers, data_mgr)
        #
        result=images_generator.execute()
        #
        images_generator.terminate()
        #
        return result
