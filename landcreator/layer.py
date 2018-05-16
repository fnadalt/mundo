
import logging
log=logging.getLogger(__name__)

class Layer:
    
    def __init__(self, type, index, data_mgr):
        # external variables
        self.type=type
        self.index=index
        self.requires_layers=list()
        # references
        self.data_mgr=data_mgr
    
    def clear(self):
        log.info("clear layer '%s'"%self.type)
        self.requires_layers=list()
        self.data_mgr=None

    def process(self, config):
        log.info("process layer '%s'..."%self.type)
        #
        if not self._read_config_options(config):
            return False
        #
        if not self._setup_layer():
            return False
        #
        if not self._process_data():
            return False
        #
        log.info("done processing layer '%s'."%self.type)
        return True
    
    def _read_config_options(self, config):
        log.error("_read_config_options not implemented for layer '%s'"%self.type)
        return False

    def _setup_layer(self):
        log.error("_setup_layer not implemented for layer '%s'"%self.type)
        return False

    def _process_data(self):
        log.error("_process_data not implemented for layer '%s'"%self.type)
        return False
