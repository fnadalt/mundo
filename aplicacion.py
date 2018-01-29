from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import loadPrcFileData

from mundo import Mundo
import config

import logging
logging.basicConfig(level=logging.DEBUG)
log=logging.getLogger(__name__)

class Aplicacion(ShowBase):
    
    def __init__(self):
        #
        ShowBase.__init__(self)
        PStatClient.connect()
        #
        loadPrcFileData('', 'gl-coordinate-system default') # ? indicado para usar trans_world_to_clip_of_light
        #loadPrcFileData('', 'sync-video 0')
        #loadPrcFileData('', 'notify-level debug')
        #
        self.disableMouse()
        self.setFrameRateMeter(True)
        #
        self.mundo=Mundo(self)
        
    def iniciar(self):
        config.iniciar()
        self.mundo.iniciar()
        self.run()

    def step(self):
        self.taskMgr.step()
        self.taskMgr.step()        
