#!/usr/bin/python

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

import logging
logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)

import gui

class App(DirectObject):

    FrameBgColor=(0, 0.7, 0.7, 1)
    WidgetsBgColor=(0.1, 0.78, 0.78,  1)
    TextFgColor=(0.9, 0.9, 0.5, 1)
    
    def __init__(self):
        super(DirectObject, self).__init__()
        #
        PStatClient.connect()
        # base
        base.disableMouse()
        base.camera.setPos(-0.3, -2.5, 0)
        base.win.setClearColor(App.FrameBgColor)
        base.taskMgr.add(self.update, "update")
        # gui
        gui.initialize()
        gui.manager.load_main() # load_main

    def update(self, task):
        if not gui.manager.update():
            return task.done
        return task.cont
    
    def clean_up(self): # clean
        gui.terminate()

if __name__=="__main__":
    #        
    base=ShowBase()
    app=App()
    base.run()
    app.clean_up()
