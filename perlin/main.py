from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *

class App(ShowBase):
    
    def __init__(self):
        super(App, self).__init__()
        # componentes:
        self.plano=None
        # init:
        self.disableMouse()
        self.camera.setPos(-0.3, -2.5, 0)
        self._generar_plano()
        self._generar_gui()
    
    def _generar_plano(self):
        _card=CardMaker("plano")
        _card.setFrame(-0.5, 0.5, -0.5, 0.5)
        _card.setColor(1, 0, 0, 1)
        self.plano=self.render.attachNewNode(_card.generate())
    
    def _generar_gui(self):
        self.lista=DirectScrolledFrame(frameSize=(-0.5, 0.5, -0.5, 0.5))

if __name__=="__main__":
    app=App()
    app.run()
