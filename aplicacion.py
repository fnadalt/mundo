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
        ShowBase.__init__(self)
        # componentes:
        self.mundo=None
        
    def iniciar(self):
        PStatClient.connect()
        #
        loadPrcFileData('', 'gl-coordinate-system default') # ? indicado para usar trans_world_to_clip_of_light
        #loadPrcFileData('', 'sync-video 0')
        #loadPrcFileData('', 'notify-level debug')
        loadPrcFileData('', 'dump-generated-shaders 1')
        #
        self.disableMouse()
        self.setFrameRateMeter(True)
        #
        self.win.setCloseRequestEvent("cerrar_aplicacion")
        #
        config.iniciar()
        self.mundo=Mundo(self)
        self.mundo.iniciar()
        #
        self.accept("cerrar_aplicacion", self.cerrar_aplicacion)
        self.run()

    def step(self):
        self.taskMgr.step()
        self.taskMgr.step()        

    def cerrar_aplicacion(self):
        log.info("cerrar_aplicacion")
        config.escribir_archivo()
        self.mundo.terminar()
        self.finalizeExit()

