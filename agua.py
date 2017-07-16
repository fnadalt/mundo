from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua:
    
    def __init__(self, mundo):
        self.mundo=mundo
        #
        self.nodo=self.mundo.base.loader.loadModel("objetos/plano")
        self.nodo.setSx(128.0)
        self.nodo.setSy(128.0)
        self.nodo.setTransparency(TransparencyAttrib.MAlpha)
        #
        m=Material()
        m.setDiffuse((0.0, 0.0, 1.0, 1.0))
        m.setShininess(2.0)
        #self.nodo.setMaterial(m)
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/agua.vert", fragment="shaders/agua.frag")
        self.nodo.setShader(shader)
