from direct.gui.DirectGui import *

import gui

import logging
log=logging.getLogger(__name__)

class MainGui:
    
    def __init__(self):
        self.frame=None
        self.trigger_load_texture_gui=False
    
    def build(self):
        log.info("build")
        self.frame=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(1, 1, -1, 1), pos=(0, 0, 0))
        DirectButton(parent=self.frame, text="texture", frameSize=(-2., 2., -0.7, 0.7), frameColor=gui.WidgetsBgColor, scale=0.1, pos=(0, 0, 0.0), text_fg=gui.TextFgColor, text_pos=(0, -0.15), command=self.open_texture_gui)
        DirectButton(parent=self.frame, text="terrain", frameSize=(-2., 2., -0.7, 0.7), frameColor=gui.WidgetsBgColor, scale=0.1, pos=(0, 0, -0.2), text_fg=gui.TextFgColor, text_pos=(0, -0.15))
    
    def open_texture_gui(self):
        # DirectButton "TextureGui" just sets a trigger flag and returns
        self.trigger_load_texture_gui=True
    
    def remove(self): # remove
        log.info("remove")
        self.frame.destroy()
        self.frame=None
    
    def update(self):
        if self.trigger_load_texture_gui: # check trigger
            log.info("trigger_load_texture_gui")
            gui.manager.load_texture_gui() # loads TextureGui into gui.manager.gui_next (gui_next)
            self.trigger_load_texture_gui=False
            return False
        return True
