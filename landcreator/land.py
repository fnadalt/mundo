import configparser
import os, os.path
import time

import logging
log=logging.getLogger(__name__)

from data import DataManager
from topography import Topography
from images import ImagesGenerator
from map import MapGenerator

# default config dict
_defaul_config={"global": {
                            "name":"land", 
                            "size_total":512, 
                            "size_chunk":512, 
                            "ocean_altitude_relative":0.15,  # [0,1]
                            "border_start_relative":0.1
                            }, 
                "layers": {
                            "topography":True, 
                            "rivers":True, 
                            "temperature":True, 
                            "humidity":True, 
                            "vegetation":True
                            }, 
                "data":   {
                            "chunk_prefix":"chunk"
                            }, 
                "topography":  {
                                "height":300.0, 
                                "scale":1.0
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
            "vegetation"
            ]
    
    # file extensions
    FilePrefixes=[
                  "chunk", 
                  "heightmap", 
                  "topography", 
                  "temperature", 
                  "humidity"
                  ]
    
    def __init__(self):
        self.config=None
        self.generate_images=False
        self.directory="."
        self.name="land"
        self.size_total=1
        self.size_chunk=1
        self.ocean_altitude_relative=0.15
        self.border_start_relative=0.1
        self.topography_height=300.0
        self.topography_scale=1.0
        self.data_mgr=None # DataManager
        self.layers=None # dict()
        self.reset() # redundancy?
    
    def execute(self, args):
        log.info("execute, file=%s"%args.land_file)
        # config
        self.config=self._configure(args.land_file, args.create_default_land_file)
        if not self.config:
            return False
        # set up directory
        self.directory=self._setup_directory(args.remove_files, args.generate_data, args.generate_images, args.generate_map)
        if not self.directory:
            return False
        # set up data
        self.data_mgr=self._setup_data_mgr()
        if not self.data_mgr:
            self.reset()
            return False
        # set up layers
        self.layers=self._setup_layers()
        if not self.layers:
            return False
        # validate layers
        if not self._validate_layers():
            self.reset()
            return False
        # generate data
        if args.generate_data:
            # process layers
            if not self._generate_data():
                self.reset()
                return False
        # generate images
        if args.generate_images and not self._generate_images():
            self.reset()
            return False
        # generate map
        if args.generate_map!="" and not self._generate_map(args.generate_map, args.map_size):
            self.reset()
            return False
        # terminate
        if self.data_mgr:
            self.data_mgr.terminate()
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
    
    def _configure(self, file, create_default_land_file):
        log.info("_configure")
        # configparser
        config=configparser.ConfigParser()
        config.read_dict(_defaul_config)
        # file?
        if not os.path.exists(file):
            if not create_default_land_file:
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
            self.ocean_altitude_relative=float(config["global"]["ocean_altitude_relative"])
            self.border_start_relative=float(config["global"]["border_start_relative"])
        except Exception as e:
            log.exception(str(e))
            return None
        #
        return config

    def _setup_directory(self, remove_files, generate_data, generate_images, map):
        log.info("_setup_directory")
        #
        directory=self.name
        #
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                log.error("'%s' is not a directory"%directory)
                return None
            #
            log.info("gathering files to remove in '%s'"%directory)
            paths_to_remove=list()
            for file in os.listdir(directory):
                path=os.path.join(directory, file)
                if os.path.isdir(file):
                    log.warning("'%s' is a directory... skipping."%path)
                    continue
                prefix=file.split(".")[0].split("_")[0].lower()
                if prefix not in Land.FilePrefixes:
                    log.warning("found not expected prefix '%s' in file '%s'... skipping"%(prefix, file))
                    continue
                if ((generate_data or generate_images) and prefix=="heightmap") or \
                    (generate_data and prefix=="chunk") or \
                    (map=="topography" and prefix=="topography") or \
                    (map=="temperature" and prefix=="temperature") or \
                    (map=="humidity" and prefix=="humidity"):
                        paths_to_remove.append(path)
            #
            log.info("remove files inside directory '%s'?"%directory)
            if len(paths_to_remove)>0 and not remove_files:
                log.error("directory '%s' contains files to be removed and remove_files=False"%directory)
                return None
            else:
                log.info("no files to be removed")
            for path in paths_to_remove:
                log.info("remove '%s'"%path)
                os.remove(path)
        elif not os.path.exists(directory):
            log.info("create directory '%s'"%directory)
            os.mkdir(directory)
        #
        return directory
    
    def _setup_data_mgr(self):
        log.info("_setup_data_mgr")
        #
        if not "data" in self.config:
            log.error("no 'data' section in config")
            return None
        config_data=self.config["data"]
        #
        data_mgr=DataManager()
        if not data_mgr.initialize(self.directory, config_data, self.size_total, self.size_chunk):
            return None
        return data_mgr
    
    def _setup_layers(self):
        log.info("_setup_layers")
        #
        if not "layers" in self.config:
            log.error("no 'layers' section in config")
            return None
        config_layers=self.config["layers"]
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
                config_topography=self.config["topography"]
                layers["topography"]=Topography(index, self.data_mgr, config_topography, self.size_total, self.ocean_altitude_relative, self.border_start_relative)
                log.info("created.")
            else:
                log.warning("unknown layer '%s'"%layer)
                index-=1 # compensate index+=1
            #
            index+=1
        #
        return layers
    
    def _validate_layers(self):
        log.info("_validate_layers")
        #
        log.info("layers requirements...")
        for type, layer in self.layers.items():
            for requirement in layer.requires_layers:
                if requirement in self.layers:
                    required_layer=self.layers[type]
                    if required_layer.index>=layer.index:
                        log.error("required layer '%s' for layer '%s' needs to be created before")
                        return False
                else:
                    log.error("requirement '%s' missing for layer '%s' (%s)"%(requirement, layer.type, str(layer.requires_layers)))
                    return False
        log.info("ok.")
        #
        return True

    def _generate_data(self):
        log.info("_generate_data")
        #
        for type, layer in self.layers.items():
            log.info("process layer '%s'"%type)
            #
            config_type=dict()
            if type in self.config:
                config_type=self.config[type]
            else:
                log.warning("no configuration information for layer '%s'"%type)
            t1=time.time()
            if not layer.process(config_type):
                return False
            t2=time.time()
            log.info("done processing layer '%s' in time %.3f"%(type, (t2-t1)))
        #
        return True

    def _generate_images(self):
        log.info("_generate_images")
        #
        images_generator=ImagesGenerator()
        images_generator.initialize(self.layers, self.data_mgr)
        #
        result=images_generator.execute()
        #
        images_generator.terminate()
        #
        return result

    def _generate_map(self, map, map_size):
        log.info("_generate_map '%s' size=%i"%(map, map_size))
        #
        config_topography=self.config["topography"]
        #
        map_generator=MapGenerator()
        map_generator.initialize(self.data_mgr, config_topography, map, map_size, self.ocean_altitude_relative)
        #
        result=map_generator.execute()
        #
        map_generator.terminate()
        #
        return result
