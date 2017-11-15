from maingui import MainGui
from texturegui import TextureGui

import logging
log=logging.getLogger(__name__)

FrameBgColor=(0, 0.7, 0.7, 1)
WidgetsBgColor=(0.1, 0.78, 0.78,  1)
TextFgColor=(0.9, 0.9, 0.5, 1)

class GuiManager:

    def __init__(self):
        self.gui_current=None # current, one of MainGui or TextureGui
        self.gui_next=None # next, idem
    
    def load_main(self):
        log.info("load_main")
        self.gui_next=MainGui()
    
    def load_texture_gui(self):
        log.info("load_texture_gui")
        self.gui_next=TextureGui()
    
    def update(self):
        if self.gui_current: # if there's a "gui" frame...
            if not self.gui_current.update(): # if update() is False...
                log.info("remove gui_current %s"%str(self.gui_current))
                self.gui_current.remove() # remove
                self.gui_current=self.gui_next # current<-next
                self.gui_next=None # next->None
                if self.gui_current:
                    self.gui_current.build() # build, create DirectGui objects
                else:
                    return False
        else:
            if self.gui_next: # handles the "first" gui frame case
                log.info("set first gui %s"%str(self.gui_next))
                self.gui_current=self.gui_next
                self.gui_current.build() # build
                self.gui_next=None
        return True

manager=None

def initialize():
    global manager
    if manager:
        log.error("ya iniciado")
        return
    manager=GuiManager()

def terminate():
    global manager
    if not manager:
        log.error("no iniciado")
        return
    manager.close_gui_current()
    manager=None
