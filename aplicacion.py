from direct.showbase.ShowBase import ShowBase
from mundo import Mundo

import logging
logging.basicConfig(level=logging.DEBUG)
log=logging.getLogger(__name__)

class Aplicacion(ShowBase):
    
    def __init__(self):
        #
        ShowBase.__init__(self)
        self.disableMouse()
        self.setFrameRateMeter(True)
        #
        self.mundo=Mundo(self)
        self.mundo.setShaderAuto(1)
        
    def iniciar(self):
        self.run()

    def step(self):
        self.taskMgr.step()
        self.taskMgr.step()        
