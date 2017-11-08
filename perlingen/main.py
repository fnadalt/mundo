#!/usr/bin/python

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *

from textura import Textura

class App(ShowBase):

    ColorFondoFrame=(0, 0.7, 0.7, 1)
    ColorFondoWidgets=(0.1, 0.78, 0.78,  1)
    ColorTexto=(0.9, 0.9, 0.5, 1)
    
    def __init__(self):
        super(App, self).__init__()
        # escenas:
        self.textura=None
        self.terreno=None
        # componentes:
        self.frame=None
        # init:
        PStatClient.connect()
        self.disableMouse()
        self.camera.setPos(-0.3, -2.5, 0)
        self.win.setClearColor(App.ColorFondoFrame)
        self.construir_gui()

    def construir_gui(self):
        print("construir_gui")
        self.clean_up()
        if not self.frame:
            print("crear frame")
            self.frame=DirectFrame(frameColor=App.ColorFondoFrame, frameSize=(1, 1, -1, 1), pos=(0, 0, 0))
        else:
            print("show frame")
            self.frame.show()
        DirectButton(parent=self.frame, text="textura", frameSize=(-2., 2., -0.7, 0.7), frameColor=App.ColorFondoWidgets, scale=0.1, pos=(0, 0, 0.0), text_fg=App.ColorTexto, text_pos=(0, -0.15), command=self.abrir_textura)
        DirectButton(parent=self.frame, text="terreno", frameSize=(-2., 2., -0.7, 0.7), frameColor=App.ColorFondoWidgets, scale=0.1, pos=(0, 0, -0.2), text_fg=App.ColorTexto, text_pos=(0, -0.15))
    
    def clean_up(self):
        if self.textura:
            self.textura=None
    
    def abrir_textura(self):
        print("abrir_textura")
        self.frame.hide()
        self.textura=Textura(self)
        self.textura.construir()
        
if __name__=="__main__":
    app=App()
    app.run()
