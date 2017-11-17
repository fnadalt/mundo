#!/usr/bin/python

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

import gui
from maingui import MainGui

import logging
logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)

class App(ShowBase):

    def __init__(self):
        super(App, self).__init__()
        #
        PStatClient.connect()
        # base
        self.disableMouse()
        self.camera.setPos(-0.3, -2.5, 0)
        self.win.setClearColor(gui.AppBgColor)
    
    def load(self):
        log.info("load")
        #
        self.main_gui=MainGui(self)
        self.main_gui.load()
    
    def unload(self):
        log.info("unload")
        #
        self.main_gui.unload()

if __name__=="__main__":
    #        
    app=App()
    app.load()
    app.run()
    app.unload()
