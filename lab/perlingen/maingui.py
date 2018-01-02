from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *

import gui
from texturegui import TextureGui

import logging
log=logging.getLogger(__name__)

class MainGui(DirectObject):
    
    def __init__(self, base):
        # references:
        self.base=base
        # components:
        self.frame=None
        self.tool=None
    
    def load(self):
        log.info("load")
        #
        self.frame=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(1, 1, -1, 1), pos=(0, 0, 0))
        DirectButton(parent=self.frame, text="texture", frameSize=(-2., 2., -0.7, 0.7), frameColor=gui.WidgetsBgColor, scale=0.1, pos=(0, 0, 0.0), text_fg=gui.TextFgColor, text_pos=(0, -0.15), command=self.open_texture_gui)
        DirectButton(parent=self.frame, text="terrain", frameSize=(-2., 2., -0.7, 0.7), frameColor=gui.WidgetsBgColor, scale=0.1, pos=(0, 0, -0.2), text_fg=gui.TextFgColor, text_pos=(0, -0.15))
        #
        self.base.taskMgr.add(self._update, "main_gui_update_task")
    
    def unload(self):
        log.info("unload")
        #
        self.base.taskMgr.remove("main_gui_update_task")
        #
        self.frame.destroy()
        self.frame=None

    def open_texture_gui(self):
        log.info("open_texture_gui")
        self._unload_tool()
        self.frame.hide()
        self.tool=TextureGui(self.base)
        self.tool.load()
        
    def _unload_tool(self):
        log.info("_unload_tool")
        if self.tool:
            self.tool.unload()
            self.tool=None

    def _update(self, task):
        if self.tool:
            if not self.tool.update():
                self._unload_tool()
                self.frame.show()
        return task.cont
